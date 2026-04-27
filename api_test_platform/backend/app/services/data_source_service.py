"""
Data Source Service - 数据源服务
支持CSV、JSON和数据库数据源的数据加载、预览、校验
"""
import csv
import json
import os
import random
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
import sqlalchemy

from app.models.data_source import DataSource
from app.models.environment import EnvDatabase


class DataSourceError(Exception):
    """数据源错误"""
    pass


class ValidationError(Exception):
    """数据校验错误"""
    pass


class DataSourceService:
    """数据源服务 - 负责数据加载、预览、校验"""

    def __init__(self, db: Session):
        self.db = db

    def _get_data_source(self, data_source_id: int) -> DataSource:
        """获取数据源配置"""
        data_source = self.db.query(DataSource).filter(
            DataSource.id == data_source_id,
            DataSource.enabled == True
        ).first()
        if not data_source:
            raise HTTPException(status_code=404, detail="数据源不存在或已禁用")
        return data_source

    def _parse_config(self, config_str: str) -> Dict[str, Any]:
        """解析数据源配置"""
        try:
            return json.loads(config_str)
        except json.JSONDecodeError as e:
            raise DataSourceError(f"数据源配置格式错误: {e}")

    async def load_data(self, data_source_id: int) -> List[Dict[str, Any]]:
        """加载数据源数据

        Args:
            data_source_id: 数据源ID

        Returns:
            数据列表
        """
        data_source = self._get_data_source(data_source_id)
        config = self._parse_config(data_source.source_config)

        source_type = data_source.source_type.lower()

        if source_type == "csv":
            return self._load_csv(config)
        elif source_type == "json":
            return self._load_json(config)
        elif source_type == "database":
            return self._load_from_database(config)
        else:
            raise DataSourceError(f"不支持的数据源类型: {source_type}")

    def load_data_with_error(
        self,
        data_source: DataSource,
        environment_id: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], str]:
        """加载数据源数据（带错误返回）

        Args:
            data_source: 数据源对象
            environment_id: 环境ID（用于数据库数据源）

        Returns:
            (数据列表, 错误信息) 元组
        """
        try:
            config = self._parse_config(data_source.source_config)
            source_type = data_source.source_type.lower()

            if source_type == "csv":
                data = self._load_csv(config)
            elif source_type == "json":
                data = self._load_json(config)
            elif source_type == "database":
                data = self._load_from_database(config, environment_id)
            else:
                return [], f"不支持的数据源类型: {source_type}"

            # 应用变量映射
            variable_mapping = config.get("variable_mapping", {})
            if variable_mapping:
                data = self._apply_variable_mapping(data, variable_mapping)

            return data, ""
        except Exception as e:
            return [], str(e)

    def _apply_variable_mapping(
        self,
        data: List[Dict[str, Any]],
        variable_mapping: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """应用变量映射

        Args:
            data: 原始数据列表
            variable_mapping: 变量映射 {变量名: 源字段名}

        Returns:
            映射后的数据列表
        """
        if not variable_mapping:
            return data

        mapped_data = []
        for row in data:
            mapped_row = {}
            for var_name, source_field in variable_mapping.items():
                mapped_row[var_name] = row.get(source_field, "")
            mapped_data.append(mapped_row)

        return mapped_data

    def _load_csv(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """加载CSV数据

        Args:
            config: {
                "file_path": "data/test.csv",
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": true
            }

        Returns:
            数据列表，每行数据为字典
        """
        file_path = config.get("file_path")
        if not file_path:
            raise DataSourceError("CSV文件路径未配置")

        if not os.path.exists(file_path):
            raise DataSourceError(f"CSV文件不存在: {file_path}")

        encoding = config.get("encoding", "utf-8")
        delimiter = config.get("delimiter", ",")
        has_header = config.get("has_header", True)

        try:
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                if has_header:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    return [row for row in reader]
                else:
                    reader = csv.reader(f, delimiter=delimiter)
                    return [{"col_" + str(i): val for i, val in enumerate(row)}
                            for row in reader]
        except UnicodeDecodeError:
            raise DataSourceError(f"CSV文件编码错误，请使用正确的编码格式")
        except Exception as e:
            raise DataSourceError(f"CSV文件读取失败: {e}")

    def _load_json(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """加载JSON数据

        Args:
            config: {
                "file_path": "data/test.json",
                "json_path": "$.data.items",  # JSONPath提取
                "encoding": "utf-8"
            }

        Returns:
            数据列表，每条数据为字典
        """
        from jsonpath_ng import parse as jsonpath_parse

        file_path = config.get("file_path")
        if not file_path:
            raise DataSourceError("JSON文件路径未配置")

        if not os.path.exists(file_path):
            raise DataSourceError(f"JSON文件不存在: {file_path}")

        encoding = config.get("encoding", "utf-8")
        json_path = config.get("json_path")

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)

            # 如果指定了JSONPath，提取数据
            if json_path:
                jsonpath_expr = jsonpath_parse(json_path)
                matches = jsonpath_expr.find(data)
                if not matches:
                    raise DataSourceError(f"JSONPath未匹配到数据: {json_path}")

                # 如果匹配结果是列表，直接返回
                result = matches[0].value
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict):
                    return [result]
                else:
                    raise DataSourceError(f"JSONPath提取的数据类型不支持: {type(result)}")

            # 如果没有JSONPath，根据数据类型处理
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                raise DataSourceError(f"JSON数据格式不支持: {type(data)}")

        except json.JSONDecodeError as e:
            raise DataSourceError(f"JSON格式错误: {e}")
        except UnicodeDecodeError:
            raise DataSourceError(f"JSON文件编码错误，请使用正确的编码格式")
        except Exception as e:
            if isinstance(e, DataSourceError):
                raise
            raise DataSourceError(f"JSON文件读取失败: {e}")

    def _load_from_database(
        self,
        config: Dict[str, Any],
        environment_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """从数据库加载数据

        Args:
            config: {
                "database_id": 1,  # 环境数据库配置ID
                "sql": "SELECT * FROM users WHERE status = :status",
                "params": {"status": "active"}  # 可选参数
            }
            environment_id: 环境ID

        Returns:
            数据列表，每条数据为字典
        """
        database_id = config.get("database_id")
        sql = config.get("sql")

        if not database_id:
            raise DataSourceError("数据库ID未配置")
        if not sql:
            raise DataSourceError("SQL语句未配置")

        # 查询数据库配置
        db_config = self.db.query(EnvDatabase).filter(
            EnvDatabase.id == database_id
        ).first()

        if not db_config:
            raise DataSourceError(f"数据库配置不存在: {database_id}")

        try:
            # 构建数据库连接URL
            db_url = self._build_database_url(db_config)
            engine = sqlalchemy.create_engine(db_url)

            # 执行SQL查询
            with engine.connect() as conn:
                params = config.get("params", {})
                result = conn.execute(sqlalchemy.text(sql), params or {})
                columns = list(result.keys())

                # 转换为字典列表
                data = []
                for row in result:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # 处理特殊类型
                        if hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        row_dict[col] = value
                    data.append(row_dict)

                return data

        except sqlalchemy.exc.SQLAlchemyError as e:
            raise DataSourceError(f"数据库查询失败: {e}")
        except Exception as e:
            raise DataSourceError(f"数据库连接失败: {e}")

    def _build_database_url(self, db_config: EnvDatabase) -> str:
        """构建数据库连接URL

        Args:
            db_config: 数据库配置对象

        Returns:
            数据库连接URL
        """
        db_type = db_config.db_type.lower()

        # 映射数据库类型到SQLAlchemy方言
        dialect_map = {
            "mysql": "mysql+pymysql",
            "postgresql": "postgresql+psycopg2",
            "postgres": "postgresql+psycopg2",
            "sqlite": "sqlite",
            "oracle": "oracle+cx_oracle",
            "mssql": "mssql+pymssql",
            "sqlserver": "mssql+pymssql",
        }

        dialect = dialect_map.get(db_type, db_type)

        if db_type == "sqlite":
            return f"sqlite:///{db_config.database}"

        url = f"{dialect}://{db_config.username}:{db_config.password}@{db_config.host}"
        if db_config.port:
            url += f":{db_config.port}"
        url += f"/{db_config.database}"

        return url

    async def preview(
        self,
        data_source_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """预览数据（分页）

        Args:
            data_source_id: 数据源ID
            page: 页码（从1开始）
            page_size: 每页大小

        Returns:
            {
                "total": 总记录数,
                "page": 当前页,
                "page_size": 每页大小,
                "data": 数据列表,
                "fields": 字段列表,
                "field_types": 字段类型映射
            }
        """
        data = await self.load_data(data_source_id)

        if not data:
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "data": [],
                "fields": [],
                "field_types": {}
            }

        # 获取字段列表和类型
        fields = list(data[0].keys()) if data else []
        field_types = {}
        for field in fields:
            values = [row.get(field) for row in data if row.get(field) is not None]
            if values:
                field_types[field] = type(values[0]).__name__
            else:
                field_types[field] = "string"

        # 分页
        total = len(data)
        start = (page - 1) * page_size
        end = start + page_size
        page_data = data[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": page_data,
            "fields": fields,
            "field_types": field_types
        }

    async def get_statistics(self, data_source_id: int) -> Dict[str, Any]:
        """获取数据统计信息

        Args:
            data_source_id: 数据源ID

        Returns:
            {
                "total_records": 总记录数,
                "field_count": 字段数量,
                "fields": 字段列表,
                "field_types": 字段类型映射,
                "null_counts": 空值统计,
                "sample_values": 示例值
            }
        """
        data = await self.load_data(data_source_id)

        if not data:
            return {
                "total_records": 0,
                "field_count": 0,
                "fields": [],
                "field_types": {},
                "null_counts": {},
                "sample_values": {}
            }

        # 获取字段列表
        fields = list(data[0].keys()) if data else []

        # 统计字段类型
        field_types = {}
        for field in fields:
            values = [row.get(field) for row in data if row.get(field) is not None]
            if values:
                field_types[field] = type(values[0]).__name__
            else:
                field_types[field] = "string"

        # 统计空值
        null_counts = {}
        for field in fields:
            null_counts[field] = sum(1 for row in data if row.get(field) is None)

        # 获取示例值（前3条）
        sample_values = {}
        for field in fields:
            values = [row.get(field) for row in data[:3] if row.get(field) is not None]
            sample_values[field] = values

        return {
            "total_records": len(data),
            "field_count": len(fields),
            "fields": fields,
            "field_types": field_types,
            "null_counts": null_counts,
            "sample_values": sample_values
        }

    async def test_connection(self, data_source_id: int) -> Dict[str, Any]:
        """测试数据源连接

        Args:
            data_source_id: 数据源ID

        Returns:
            {
                "success": 是否成功,
                "message": 消息,
                "record_count": 记录数（如果成功）
            }
        """
        try:
            data_source = self._get_data_source(data_source_id)
            config = self._parse_config(data_source.source_config)

            source_type = data_source.source_type.lower()
            file_path = config.get("file_path")

            if source_type in ("csv", "json"):
                if not file_path:
                    return {
                        "success": False,
                        "message": "文件路径未配置",
                        "record_count": None
                    }

                if not os.path.exists(file_path):
                    return {
                        "success": False,
                        "message": f"文件不存在: {file_path}",
                        "record_count": None
                    }

                # 尝试加载数据
                data = await self.load_data(data_source_id)
                return {
                    "success": True,
                    "message": "连接成功",
                    "record_count": len(data)
                }
            else:
                return {
                    "success": False,
                    "message": f"不支持的数据源类型: {source_type}",
                    "record_count": None
                }

        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "record_count": None
            }

    async def validate_data(self, data_source_id: int) -> Dict[str, Any]:
        """校验数据源数据

        Args:
            data_source_id: 数据源ID

        Returns:
            {
                "valid": 是否有效,
                "errors": 错误列表,
                "warnings": 警告列表
            }
        """
        errors = []
        warnings = []

        try:
            data_source = self._get_data_source(data_source_id)
            config = self._parse_config(data_source.source_config)

            # 检查文件路径
            file_path = config.get("file_path")
            if not file_path:
                errors.append("文件路径未配置")
                return {
                    "valid": False,
                    "errors": errors,
                    "warnings": warnings
                }

            # 加载数据
            data = await self.load_data(data_source_id)

            if not data:
                warnings.append("数据源为空")
                return {
                    "valid": True,
                    "errors": errors,
                    "warnings": warnings
                }

            # 检查必填字段
            required_fields = config.get("required_fields", [])
            if required_fields:
                for field in required_fields:
                    if field not in data[0]:
                        errors.append(f"缺少必填字段: {field}")
                    else:
                        # 检查是否有空值
                        null_count = sum(1 for row in data if row.get(field) is None or row.get(field) == "")
                        if null_count > 0:
                            warnings.append(f"字段 '{field}' 有 {null_count} 条空值记录")

            # 检查数据一致性
            fields = set(data[0].keys())
            for i, row in enumerate(data):
                row_fields = set(row.keys())
                if row_fields != fields:
                    missing = fields - row_fields
                    extra = row_fields - fields
                    if missing:
                        warnings.append(f"第 {i+1} 行缺少字段: {missing}")
                    if extra:
                        warnings.append(f"第 {i+1} 行多余字段: {extra}")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }

        except Exception as e:
            errors.append(str(e))
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }
