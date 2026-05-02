"""
Encryption Service
使用AES-256-GCM加密敏感数据
"""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import base64
from typing import Optional
from app.core.config import settings


class EncryptionService:
    """
    加密服务类
    
    加密算法: AES-256-GCM
    密钥派生: PBKDF2-HMAC-SHA256
    密钥长度: 256 bits
    盐值长度: 128 bits
    Nonce长度: 96 bits
    """
    
    KEY_LENGTH = 32  # 256 bits
    SALT_LENGTH = 16  # 128 bits
    NONCE_LENGTH = 12  # 96 bits
    ITERATIONS = 100000  # PBKDF2迭代次数
    
    def __init__(self, master_key: Optional[str] = None):
        """
        初始化加密服务
        
        Args:
            master_key: 主密钥，从环境变量或密钥管理服务获取
        """
        self.master_key = (master_key or settings.ENCRYPTION_MASTER_KEY).encode('utf-8')
    
    def _derive_key(self, salt: bytes) -> bytes:
        """派生数据加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(self.master_key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密数据
        
        Returns:
            格式: base64(salt + nonce + ciphertext)
        """
        if not plaintext:
            return ""
        
        salt = os.urandom(self.SALT_LENGTH)
        nonce = os.urandom(self.NONCE_LENGTH)
        key = self._derive_key(salt)
        
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        
        # 组合: salt(16) + nonce(12) + ciphertext
        encrypted = salt + nonce + ciphertext
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        if not encrypted_data:
            return ""
        
        try:
            encrypted = base64.b64decode(encrypted_data.encode('utf-8'))
            
            salt = encrypted[:self.SALT_LENGTH]
            nonce = encrypted[self.SALT_LENGTH:self.SALT_LENGTH + self.NONCE_LENGTH]
            ciphertext = encrypted[self.SALT_LENGTH + self.NONCE_LENGTH:]
            
            key = self._derive_key(salt)
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")


# 全局加密服务实例
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """获取加密服务实例"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def encrypt_password(password: str) -> str:
    """加密密码"""
    return get_encryption_service().encrypt(password)


def decrypt_password(encrypted_password: str) -> str:
    """解密密码"""
    return get_encryption_service().decrypt(encrypted_password)
