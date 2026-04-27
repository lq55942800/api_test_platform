"""
Data Driven Engine - 数据驱动执行引擎
负责迭代执行测试用例并汇总结果
"""
import json
import random
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.data_source import DataSource
from app.services.debug_engine import DebugEngine
from app.services.data_source_service import DataSourceService


class DataDrivenEngine:
    """数据驱动执行引擎 - 负责迭代执行和结果汇总"""

    def __init__(self, db: Session):
        self.db = db
        self.debug_engine = DebugEngine(db)
        self.data_source_service = DataSourceService(db)

    async def execute(
        self,
        api_id: int,
        data_source_id: int,
        environment_id: Optional[int] = None,
        iteration_config: Optional[Dict[str, Any]] = None,
        user_id: int = 0
    ) -> Dict[str, Any]:
        """执行数据驱动测试

        Args:
            api_id: 接口ID
            data_source_id: 数据源ID
            environment_id: 环境ID
            iteration_config: 迭代配置
                {
                    "mode": "sequential" | "range",
                    "start": 0,      # range模式起始索引
                    "end": 10,       # range模式结束索引
                }
            user_id: 用户ID

        Returns:
            {
                "summary": {
                    "total": 总数,
                    "passed": 通过数,
                    "failed": 失败数,
                    "skipped": 跳过数,
                    "pass_rate": 通过率,
                    "start_time": 开始时间,
                    "end_time": 结束时间,
                    "duration_ms": 耗时
                },
                "details": [...]
            }
        """
        start_time = datetime.utcnow()

        # 加载数据
        data = await self.data_source_service.load_data(data_source_id)

        if not data:
            return {
                "summary": {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "pass_rate": 0.0,
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.utcnow().isoformat(),
                    "duration_ms": 0
                },
                "details": []
            }

        # 迭代执行
        results = await self._iterate_and_execute(
            api_id, data, environment_id, iteration_config or {}, user_id
        )

        # 汇总结果
        summary = self._aggregate_results(results, start_time)

        return {
            "summary": summary,
            "details": results
        }

    async def execute_data_driven(
        self,
        test_case_id: int,
        environment_id: int,
        data_source_id: int,
        fail_strategy: str = "stop",
        timeout: int = 600000,
        user_id: int = 0
    ) -> Dict[str, Any]:
        """执行数据驱动测试（新版本，支持失败策略和随机迭代）

        Args:
            test_case_id: 测试用例ID（接口ID）
            environment_id: 环境ID
            data_source_id: 数据源ID
            fail_strategy: 失败策略 ("stop" | "continue")
            timeout: 超时时间（毫秒）
            user_id: 用户ID

        Returns:
            {
                "success": 是否全部成功,
                "total_iterations": 总迭代次数,
                "passed_count": 通过数,
                "failed_count": 失败数,
                "results": [...]
            }
        """
        # 查询数据源
        data_source = self.db.query(DataSource).filter(
            DataSource.id == data_source_id,
            DataSource.test_case_id == test_case_id
        ).first()

        if not data_source:
            return {
                "success": False,
                "error": f"数据源不存在: {data_source_id}"
            }

        # 加载数据
        data, error = self.data_source_service.load_data_with_error(
            data_source, environment_id
        )

        if error:
            return {
                "success": False,
                "error": f"加载数据失败: {error}"
            }

        if not data:
            return {
                "success": False,
                "error": "数据源为空"
            }

        # 根据迭代模式处理数据
        iteration_mode = data_source.iteration_mode or "sequential"
        if iteration_mode == "random":
            random.shuffle(data)

        results = []
        passed_count = 0
        failed_count = 0

        for i, row_data in enumerate(data):
            iteration_result = {
                "iteration": i + 1,
                "data": row_data,
                "status": "pending"
            }

            try:
                # 注入变量
                self._inject_variables(row_data)

                # 执行调试
                result = await self.debug_engine.execute(
                    api_id=test_case_id,
                    environment_id=environment_id,
                    user_id=user_id
                )

                if result.get("status_code") is not None and result.get("status_code") < 400:
                    iteration_result["status"] = "passed"
                    iteration_result["status_code"] = result.get("status_code")
                    iteration_result["elapsed_ms"] = result.get("elapsed_ms")
                    iteration_result["response_body"] = result.get("body")
                    iteration_result["assertion_summary"] = result.get("assertion_summary")
                    passed_count += 1
                else:
                    iteration_result["status"] = "failed"
                    iteration_result["error"] = result.get("error_message") or f"HTTP {result.get('status_code')}"
                    iteration_result["status_code"] = result.get("status_code")
                    iteration_result["elapsed_ms"] = result.get("elapsed_ms")
                    iteration_result["response_body"] = result.get("body")
                    failed_count += 1

                    # 根据失败策略决定是否继续
                    if fail_strategy == "stop":
                        results.append(iteration_result)
                        break

            except Exception as e:
                iteration_result["status"] = "error"
                iteration_result["error"] = str(e)
                failed_count += 1

                if fail_strategy == "stop":
                    results.append(iteration_result)
                    break

            results.append(iteration_result)

        return {
            "success": failed_count == 0,
            "total_iterations": len(data),
            "passed_count": passed_count,
            "failed_count": failed_count,
            "results": results
        }

    async def _iterate_and_execute(
        self,
        api_id: int,
        data: List[Dict[str, Any]],
        environment_id: Optional[int],
        iteration_config: Dict[str, Any],
        user_id: int
    ) -> List[Dict[str, Any]]:
        """迭代执行测试

        Args:
            api_id: 接口ID
            data: 数据列表
            environment_id: 环境ID
            iteration_config: 迭代配置
            user_id: 用户ID

        Returns:
            执行结果列表
        """
        results = []
        mode = iteration_config.get("mode", "sequential")

        # 根据迭代模式确定执行范围
        if mode == "range":
            start = iteration_config.get("start", 0)
            end = min(iteration_config.get("end", len(data)), len(data))
            indices = range(start, end)
        else:  # sequential
            indices = range(len(data))

        for index in indices:
            data_row = data[index]

            # 注入变量并执行
            result = await self._execute_single(
                api_id, data_row, environment_id, index, user_id
            )
            results.append(result)

        return results

    async def _execute_single(
        self,
        api_id: int,
        data_row: Dict[str, Any],
        environment_id: Optional[int],
        iteration_index: int,
        user_id: int
    ) -> Dict[str, Any]:
        """执行单次测试

        Args:
            api_id: 接口ID
            data_row: 数据行
            environment_id: 环境ID
            iteration_index: 迭代索引
            user_id: 用户ID

        Returns:
            单次执行结果
        """
        try:
            # 注入变量到VariableManager
            self._inject_variables(data_row)

            # 执行调试
            result = await self.debug_engine.execute(
                api_id=api_id,
                environment_id=environment_id,
                user_id=user_id
            )

            return {
                "iteration": iteration_index + 1,
                "data": data_row,
                "success": result.get("status_code") is not None and result.get("status_code") < 400,
                "status_code": result.get("status_code"),
                "elapsed_ms": result.get("elapsed_ms"),
                "error_message": result.get("error_message"),
                "response_body": result.get("body"),
                "assertion_summary": result.get("assertion_summary")
            }

        except Exception as e:
            return {
                "iteration": iteration_index + 1,
                "data": data_row,
                "success": False,
                "status_code": None,
                "elapsed_ms": None,
                "error_message": str(e),
                "response_body": None,
                "assertion_summary": None
            }

    def _inject_variables(self, data_row: Dict[str, Any]) -> None:
        """注入变量到测试上下文

        Args:
            data_row: 数据行（字段名作为变量名）
        """
        # 清除上一次的变量
        self.debug_engine.variable_manager.clear_scope("request")

        # 注入新变量
        for key, value in data_row.items():
            self.debug_engine.variable_manager.set(key, value, "request")

    def _aggregate_results(
        self,
        results: List[Dict[str, Any]],
        start_time: datetime
    ) -> Dict[str, Any]:
        """汇总执行结果

        Args:
            results: 执行结果列表
            start_time: 开始时间

        Returns:
            汇总统计信息
        """
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        total = len(results)
        passed = sum(1 for r in results if r.get("success"))
        failed = sum(1 for r in results if not r.get("success") and r.get("status_code") is not None)
        skipped = sum(1 for r in results if r.get("status_code") is None and not r.get("success"))

        pass_rate = round(passed / total, 4) if total > 0 else 0.0

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": pass_rate,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_ms": duration_ms
        }
