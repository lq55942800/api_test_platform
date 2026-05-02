from app.core.logging import get_logger
from typing import Any, Dict, List
from app.services.engines.variable_manager import VariableManager
from app.services.extractors.extractor_engine import ExtractorEngine
from app.services.assertions.base_assertion import AssertionResult
from app.services.assertions.status_code_assertion import StatusCodeAssertion
from app.services.assertions.header_assertion import HeaderAssertion
from app.services.assertions.response_time_assertion import ResponseTimeAssertion
from app.services.assertions.body_assertion import BodyAssertion
from app.services.assertions.json_schema_assertion import JSONSchemaAssertion
from app.services.assertions.script_assertion import ScriptAssertion

logger = get_logger(__name__)


class AssertionEngine:
    ASSERTION_MAP = {
        "status_code": StatusCodeAssertion,
        "header": HeaderAssertion,
        "response_time": ResponseTimeAssertion,
        "body": BodyAssertion,
        "json_schema": JSONSchemaAssertion,
        "script": ScriptAssertion,
    }

    def __init__(self, variable_manager: VariableManager, extractor_engine: ExtractorEngine):
        self.variable_manager = variable_manager
        self.extractor_engine = extractor_engine

    async def execute(self, assertions: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"AssertionEngine executing: assertion_count={len(assertions)}")
        sorted_assertions = sorted(
            [a for a in assertions if a.get("enabled", True)],
            key=lambda a: a.get("order", 0),
        )
        logger.debug(f"Enabled assertions after filtering: {len(sorted_assertions)}")
        results: List[AssertionResult] = []
        for assertion in sorted_assertions:
            assertion_type = assertion.get("type", "")
            assertion_cls = self.ASSERTION_MAP.get(assertion_type)
            if not assertion_cls:
                logger.warning(f"Unknown assertion type: {assertion_type}")
                results.append(AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type=assertion_type,
                    passed=False,
                    message=f"未知断言类型: {assertion_type}",
                ))
                continue
            assertion_handler = assertion_cls(self.variable_manager, self.extractor_engine)
            try:
                result = await assertion_handler.execute(assertion, context)
                results.append(result)
                if result.passed:
                    logger.debug(f"Assertion passed: name={result.name}, type={result.type}, message={result.message}")
                else:
                    logger.warning(f"Assertion failed: name={result.name}, type={result.type}, message={result.message}")
            except Exception as e:
                logger.error(f"Assertion execution error for '{assertion.get('name', '')}': {e}", exc_info=True)
                results.append(AssertionResult(
                    id=assertion.get("id", ""),
                    name=assertion.get("name", ""),
                    type=assertion_type,
                    passed=False,
                    message=f"断言执行异常: {str(e)}",
                ))

        summary = self._compute_summary(results)
        logger.info(f"Assertion summary: total={summary['total']}, passed={summary['passed']}, failed={summary['failed']}, all_passed={summary['all_passed']}")
        return {
            "results": [r.model_dump() for r in results],
            "summary": summary,
        }

    def _compute_summary(self, results: List[AssertionResult]) -> Dict[str, Any]:
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        critical_failed = sum(1 for r in results if not r.passed and r.severity == "critical")
        warning_failed = sum(1 for r in results if not r.passed and r.severity == "warning")
        info_failed = sum(1 for r in results if not r.passed and r.severity == "info")
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "critical_failed": critical_failed,
            "warning_failed": warning_failed,
            "info_failed": info_failed,
            "all_passed": failed == 0,
            "critical_passed": critical_failed == 0,
        }
