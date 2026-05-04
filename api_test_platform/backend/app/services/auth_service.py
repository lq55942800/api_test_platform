import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.base_models import User, TeamMember, Team
from app.models.auth import RefreshToken
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UpdateUserRequest,
    ChangePasswordRequest,
    TokenResponse,
    UserResponse,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user_id: int) -> tuple:
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, int(expires_delta.total_seconds())


def create_refresh_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def validate_password_strength(password: str) -> Optional[str]:
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if len(password) > 32:
        return "Password must be at most 32 characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one digit"
    return None


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: RegisterRequest) -> TokenResponse:
        strength_error = validate_password_strength(data.password)
        if strength_error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=strength_error)

        existing_user = self.db.query(User).filter(User.username == data.username).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

        existing_email = self.db.query(User).filter(User.email == data.email).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=get_password_hash(data.password),
            full_name=data.full_name,
            is_active=True,
            is_superuser=False,
        )
        self.db.add(user)
        self.db.flush()

        default_team = self.db.query(Team).filter(Team.id == 1).first()
        if default_team:
            membership = TeamMember(
                team_id=default_team.id,
                user_id=user.id,
                role="tester",
                status="active",
            )
            self.db.add(membership)

        self.db.commit()
        self.db.refresh(user)

        return self._create_token_response(user)

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.db.query(User).filter(User.username == data.username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining = int((user.locked_until - datetime.utcnow()).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked. Try again in {remaining} seconds",
            )

        if not verify_password(data.password, user.password_hash):
            user.login_fail_count = (user.login_fail_count or 0) + 1

            if user.login_fail_count >= settings.LOGIN_MAX_FAIL_COUNT:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
                self.db.commit()
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account locked for {settings.LOGIN_LOCK_MINUTES} minutes due to too many failed attempts",
                )

            remaining_attempts = settings.LOGIN_MAX_FAIL_COUNT - user.login_fail_count
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Incorrect username or password. {remaining_attempts} attempts remaining",
            )

        user.login_fail_count = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        return self._create_token_response(user)

    def refresh_token(self, refresh_token_str: str) -> TokenResponse:
        try:
            payload = jwt.decode(
                refresh_token_str, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            user_id = int(payload.get("sub"))
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        token_hash = hash_token(refresh_token_str)
        stored_token = (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False,
            )
            .first()
        )

        if not stored_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found or revoked")

        if stored_token.expires_at < datetime.utcnow():
            stored_token.is_revoked = True
            self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        stored_token.is_revoked = True

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

        self.db.commit()

        return self._create_token_response(user)

    def logout(self, user: User) -> None:
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False,
        ).update({"is_revoked": True})
        self.db.commit()

    def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("type") != "access":
                raise credentials_exception
            user_id_str: str = payload.get("sub")
            if user_id_str is None:
                raise credentials_exception
            user_id = int(user_id_str)
        except JWTError:
            raise credentials_exception

        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        return user

    def get_current_active_user(self, user: User) -> User:
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining = int((user.locked_until - datetime.utcnow()).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked. Try again in {remaining} seconds",
            )
        return user

    def update_profile(self, user: User, data: UpdateUserRequest) -> User:
        if data.email is not None and data.email != user.email:
            existing = self.db.query(User).filter(User.email == data.email, User.id != user.id).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
            user.email = data.email

        if data.full_name is not None:
            user.full_name = data.full_name

        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user: User, data: ChangePasswordRequest) -> None:
        if not verify_password(data.old_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect current password")

        strength_error = validate_password_strength(data.new_password)
        if strength_error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=strength_error)

        user.password_hash = get_password_hash(data.new_password)
        self.db.commit()

    def _create_token_response(self, user: User) -> TokenResponse:
        access_token, expires_in = create_access_token(user.id)
        refresh_token_str = create_refresh_token(user.id)

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token_str),
            expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(refresh_token_record)
        self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=expires_in,
            user=UserResponse.model_validate(user),
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    auth_service = AuthService(db)
    return auth_service.get_current_user(token)


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    if current_user.locked_until and current_user.locked_until > datetime.utcnow():
        remaining = int((current_user.locked_until - datetime.utcnow()).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {remaining} seconds",
        )
    return current_user
