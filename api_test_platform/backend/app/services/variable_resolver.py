"""
Variable Resolver Service
"""
import re
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.environment import Environment, EnvService, EnvVariable, EnvServiceVariable
from app.core.encryption import decrypt_password
from app.core.logging import get_logger

logger = get_logger(__name__)


class VariableResolver:
    VARIABLE_PATTERN = re.compile(r'\{\{([a-zA-Z0-9_\-\.]+)\}\}')
    MAX_DEPTH = 10

    def __init__(self, db: Session):
        self.db = db
        self._env_cache: Dict[int, dict] = {}
        logger.debug("VariableResolver initialized")

    def load_environment(self, environment_id: int) -> dict:
        logger.info(f"Loading environment variables: environment_id={environment_id}")
        if environment_id in self._env_cache:
            logger.debug(f"Environment variables loaded from cache: environment_id={environment_id}")
            return self._env_cache[environment_id]

        env = self.db.query(Environment).filter(
            Environment.id == environment_id,
            Environment.is_active == True
        ).first()

        if not env:
            logger.warning(f"Environment not found or inactive: environment_id={environment_id}")
            return {}

        variables = {}
        for var in env.variables:
            value = var.value
            if var.is_encrypted and value:
                try:
                    value = decrypt_password(value)
                except Exception as e:
                    logger.warning(f"Failed to decrypt environment variable: key={var.key}, error={str(e)}")
            variables[f"env.{var.key}"] = value

        for service in env.services:
            for server in service.servers:
                base_url = f"{server.protocol}://{server.host}"
                if server.port:
                    base_url += f":{server.port}"
                if server.base_path:
                    base_url += server.base_path
                variables[f"{service.name}.baseUrl"] = base_url
                variables[f"{service.name}.host"] = server.host
                if server.port:
                    variables[f"{service.name}.port"] = str(server.port)

            for db in service.databases:
                db_key = f"{service.name}.db.{db.name}"
                password = db.password
                if db.is_default or True:
                    try:
                        password = decrypt_password(password)
                    except Exception as e:
                        logger.warning(f"Failed to decrypt database password: service={service.name}, db={db.name}, error={str(e)}")
                variables[f"{db_key}.host"] = db.host
                if db.port:
                    variables[f"{db_key}.port"] = str(db.port)
                variables[f"{db_key}.database"] = db.database
                variables[f"{db_key}.username"] = db.username
                variables[f"{db_key}.password"] = password

            for var in service.variables:
                value = var.value
                if var.is_encrypted and value:
                    try:
                        value = decrypt_password(value)
                    except Exception as e:
                        logger.warning(f"Failed to decrypt service variable: service={service.name}, key={var.key}, error={str(e)}")
                variables[f"{service.name}.{var.key}"] = value

        self._env_cache[environment_id] = variables
        logger.info(f"Environment variables loaded: environment_id={environment_id}, variable_count={len(variables)}")
        return variables

    def resolve(
        self,
        text: str,
        environment_id: int,
        case_variables: Optional[Dict[str, str]] = None,
        scenario_variables: Optional[Dict[str, str]] = None
    ) -> Tuple[str, Dict[str, str], List[str]]:
        logger.info(f"Resolving variables: environment_id={environment_id}, text_length={len(text) if text else 0}")
        if not text:
            return text, {}, []

        env_vars = self.load_environment(environment_id)

        all_vars = {}
        all_vars.update(env_vars)

        if case_variables:
            for key, value in case_variables.items():
                all_vars[key] = value
                all_vars[f"case.{key}"] = value
            logger.debug(f"Added case variables: count={len(case_variables)}")

        if scenario_variables:
            for key, value in scenario_variables.items():
                all_vars[key] = value
                all_vars[f"scenario.{key}"] = value
            logger.debug(f"Added scenario variables: count={len(scenario_variables)}")

        resolved_text = text
        resolved_vars = {}
        unresolved = []
        depth = 0

        while depth < self.MAX_DEPTH:
            matches = self.VARIABLE_PATTERN.findall(resolved_text)
            if not matches:
                break

            has_changes = False
            for var_name in matches:
                placeholder = f"{{{{{var_name}}}}}"
                if var_name in all_vars:
                    resolved_text = resolved_text.replace(placeholder, str(all_vars[var_name]))
                    resolved_vars[var_name] = all_vars[var_name]
                    has_changes = True
                else:
                    if var_name not in unresolved:
                        unresolved.append(var_name)

            if not has_changes:
                break
            depth += 1

        if depth >= self.MAX_DEPTH:
            logger.warning(f"Variable resolution reached max depth ({self.MAX_DEPTH}), possible circular reference")

        if unresolved:
            logger.warning(f"Unresolved variables: {unresolved}")

        logger.debug(f"Variable resolution completed: resolved_count={len(resolved_vars)}, unresolved_count={len(unresolved)}, depth={depth}")
        return resolved_text, resolved_vars, unresolved

    def clear_cache(self, environment_id: Optional[int] = None):
        if environment_id:
            self._env_cache.pop(environment_id, None)
            logger.debug(f"Environment cache cleared: environment_id={environment_id}")
        else:
            self._env_cache.clear()
            logger.debug("All environment cache cleared")

    def get_service_url(self, environment_id: int, service_name: str) -> Optional[str]:
        logger.debug(f"Getting service URL: environment_id={environment_id}, service_name={service_name}")
        env_vars = self.load_environment(environment_id)
        url = env_vars.get(f"{service_name}.baseUrl")
        if not url:
            logger.warning(f"Service URL not found: service_name={service_name}")
        return url

    def get_database_config(self, environment_id: int, service_name: str, db_name: str) -> Optional[Dict[str, str]]:
        logger.debug(f"Getting database config: environment_id={environment_id}, service_name={service_name}, db_name={db_name}")
        env_vars = self.load_environment(environment_id)
        prefix = f"{service_name}.db.{db_name}"
        config = {}
        for key, value in env_vars.items():
            if key.startswith(prefix):
                config[key.replace(f"{prefix}.", "")] = value
        if not config:
            logger.warning(f"Database config not found: service_name={service_name}, db_name={db_name}")
        return config if config else None
