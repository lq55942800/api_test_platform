import json
import time
from typing import Any, Dict, List, Optional
from app.core.logging import get_logger
from app.services.processors.base_processor import BaseProcessor, ActionResult

logger = get_logger(__name__)


class DatabaseProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        start = time.monotonic()
        config = self._get_config(action)
        action_id = action.get("id", "")
        action_name = action.get("name", "")
        logger.info(f"DatabaseProcessor executing: action_id={action_id}, action_name={action_name}")
        try:
            environment_id = config.get("environment_id")
            service_id = config.get("service_id")
            query_type = config.get("query_type", "select")
            sql = config.get("sql", "")
            variable_mapping = config.get("variable_mapping", [])
            result_variable = config.get("result_variable")
            timeout = config.get("timeout", 30000)
            sql = self._resolve_expression(sql)
            logger.debug(f"DatabaseProcessor: query_type={query_type}, sql_length={len(sql)}, timeout={timeout}ms")
            db_config = self._resolve_db_config(environment_id, service_id, context)
            if not db_config:
                logger.error(f"Database config not found: environment_id={environment_id}, service_id={service_id}")
                return ActionResult(
                    id=action_id,
                    name=action_name,
                    type="database",
                    success=False,
                    error=f"Database config not found for environment_id={environment_id}, service_id={service_id}",
                    duration_ms=int((time.monotonic() - start) * 1000),
                )
            logger.debug(f"Database config resolved: db_type={db_config.get('db_type')}, host={db_config.get('host')}")
            results = await self._execute_sql(db_config, sql, query_type, timeout)
            output = {}
            if query_type == "select" and results:
                first_row = results[0] if results else {}
                for mapping in variable_mapping:
                    col = mapping.get("column", "")
                    var_name = mapping.get("variable", "")
                    scope = mapping.get("scope", "request")
                    value = first_row.get(col)
                    if self.variable_manager:
                        self.variable_manager.set(var_name, value, scope)
                    output[var_name] = value
                    logger.debug(f"Database variable mapping: column={col}, variable={var_name}, value={value}, scope={scope}")
                if result_variable and self.variable_manager:
                    self.variable_manager.set(result_variable, results, "request")
                    output[result_variable] = results
                    logger.debug(f"Database result variable: variable={result_variable}, row_count={len(results)}")
            elif query_type in ("insert", "update", "delete"):
                output["affected_rows"] = results if isinstance(results, int) else len(results) if isinstance(results, list) else 0
                logger.debug(f"Database affected rows: {output['affected_rows']}")
            logger.info(f"DatabaseProcessor completed: action_id={action_id}, query_type={query_type}, success=True, duration_ms={int((time.monotonic() - start) * 1000)}")
            return ActionResult(
                id=action_id,
                name=action_name,
                type="database",
                success=True,
                duration_ms=int((time.monotonic() - start) * 1000),
                output=output,
            )
        except Exception as e:
            logger.error(f"DatabaseProcessor error: action_id={action_id}, error={str(e)}", exc_info=True)
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="database",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )

    def _resolve_db_config(self, environment_id: Optional[int], service_id: Optional[int], context: Dict) -> Optional[Dict]:
        logger.debug(f"Resolving database config: environment_id={environment_id}, service_id={service_id}")
        db_session = context.get("db_session")
        if not db_session:
            db_configs = context.get("database_configs", {})
            datasource_id = context.get("datasource_id")
            if datasource_id:
                config = db_configs.get(str(datasource_id))
                if config:
                    logger.debug(f"Database config found from datasource_id: {datasource_id}")
                else:
                    logger.warning(f"Database config not found for datasource_id: {datasource_id}")
                return config
            logger.warning(f"No db_session or datasource_id available for database config resolution")
            return None

        from app.models.environment import EnvService, EnvDatabase
        if service_id:
            service = db_session.query(EnvService).filter(EnvService.id == service_id).first()
            if service:
                db_record = db_session.query(EnvDatabase).filter(
                    EnvDatabase.service_id == service_id
                ).first()
                if db_record:
                    logger.debug(f"Database config found via service_id: {service_id}")
                    return self._db_record_to_config(db_record)

        if environment_id:
            service = db_session.query(EnvService).filter(
                EnvService.environment_id == environment_id
            ).first()
            if service:
                db_record = db_session.query(EnvDatabase).filter(
                    EnvDatabase.service_id == service.id
                ).first()
                if db_record:
                    logger.debug(f"Database config found via environment_id: {environment_id}")
                    return self._db_record_to_config(db_record)

        logger.warning(f"Database config not resolved: environment_id={environment_id}, service_id={service_id}")
        return None

    def _db_record_to_config(self, db_record) -> Dict:
        config = {
            "db_type": db_record.db_type,
            "host": db_record.host,
            "port": db_record.port,
            "database": db_record.database,
            "username": db_record.username,
            "password": db_record.password,
            "charset": db_record.charset or "utf8mb4",
        }
        if db_record.extra_config:
            try:
                extra = json.loads(db_record.extra_config)
                config.update(extra)
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Failed to parse database extra_config")
        logger.debug(f"Database record converted to config: db_type={config['db_type']}, host={config['host']}")
        return config

    async def _execute_sql(self, db_config: Dict, sql: str, query_type: str, timeout: int) -> Any:
        db_type = db_config.get("db_type", "sqlite")
        logger.info(f"Executing SQL: db_type={db_type}, query_type={query_type}, sql_length={len(sql)}")
        if db_type == "sqlite":
            import sqlite3
            conn = sqlite3.connect(db_config.get("database", ":memory:"))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)
            if query_type == "select":
                columns = [desc[0] for desc in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                conn.close()
                logger.debug(f"SQLite select completed: row_count={len(rows)}")
                return rows
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                logger.debug(f"SQLite execute completed: affected_rows={affected}")
                return affected
        elif db_type in ("mysql", "postgresql"):
            import importlib
            if db_type == "mysql":
                module = importlib.import_module("pymysql")
                conn_kwargs = {
                    "host": db_config.get("host", "localhost"),
                    "port": int(db_config.get("port", 3306)),
                    "user": db_config.get("username", ""),
                    "password": db_config.get("password", ""),
                    "database": db_config.get("database", ""),
                    "charset": db_config.get("charset", "utf8mb4"),
                }
            else:
                module = importlib.import_module("psycopg2")
                conn_kwargs = {
                    "host": db_config.get("host", "localhost"),
                    "port": int(db_config.get("port", 5432)),
                    "user": db_config.get("username", ""),
                    "password": db_config.get("password", ""),
                    "dbname": db_config.get("database", ""),
                }
            conn = module.connect(**conn_kwargs)
            cursor = conn.cursor()
            cursor.execute(sql)
            if query_type == "select":
                columns = [desc[0] for desc in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                conn.close()
                logger.debug(f"{db_type} select completed: row_count={len(rows)}")
                return rows
            else:
                conn.commit()
                affected = cursor.rowcount
                conn.close()
                logger.debug(f"{db_type} execute completed: affected_rows={affected}")
                return affected
        else:
            logger.error(f"Unsupported database type: {db_type}")
            raise ValueError(f"Unsupported database type: {db_type}")
