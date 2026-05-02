from typing import Any, Dict
from app.core.logging import get_logger
from app.services.processors.base_processor import BaseProcessor, ActionResult
from app.services.extractors.base_extractor import ExtractConfig

logger = get_logger(__name__)


class ExtractProcessor(BaseProcessor):
    async def execute(self, action: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        import time
        start = time.monotonic()
        config = self._get_config(action)
        logger.info(f"ExtractProcessor executing: action_id={action.get('id')}, action_name={action.get('name')}")
        try:
            extractors = config.get("extractors", [])
            output = {}
            errors = []
            response_data = context.get("response_data", {})
            logger.debug(f"ExtractProcessor: processing {len(extractors)} extractors")
            for ext in extractors:
                source = ext.get("source", "response_json")
                extract_type = ext.get("type", "jsonpath")
                expression = ext.get("expression", "")
                default_value = ext.get("default_value", "")
                target_variable = ext.get("target_variable", "")
                target_scope = ext.get("target_scope", "temp")
                if not target_variable:
                    logger.warning(f"Extractor missing target_variable, skipping: source={source}, expression={expression}")
                    continue
                if source == "elapsed_time":
                    value = response_data.get("elapsed_ms", 0)
                    if self.variable_manager:
                        self.variable_manager.set(target_variable, value, target_scope)
                    output[target_variable] = value
                    logger.debug(f"Extracted elapsed_time: variable={target_variable}, value={value}, scope={target_scope}")
                    continue
                if not expression and source != "elapsed_time":
                    if default_value and self.variable_manager:
                        self.variable_manager.set(target_variable, default_value, target_scope)
                        output[target_variable] = default_value
                        logger.warning(f"Extractor missing expression, using default: variable={target_variable}, default={default_value}")
                    continue
                extract_config = ExtractConfig(
                    extract_type=extract_type,
                    expression=expression,
                    default_value=default_value,
                )
                result = self.extractor_engine.extract_from_response(
                    response_data, source, extract_config
                )
                value = result.value if result.success else None
                if self.variable_manager and target_variable:
                    self.variable_manager.set(target_variable, value, target_scope)
                output[target_variable] = value
                logger.debug(f"Extraction result: variable={target_variable}, source={source}, expression={expression}, success={result.success}, value={value}")
                if not result.success:
                    errors.append(f"Extract failed: {expression} -> {result.error}")
                    logger.warning(f"Extraction failed: variable={target_variable}, expression={expression}, error={result.error}")
            success = len(errors) == 0 or len(output) > 0
            logger.info(f"ExtractProcessor completed: action_id={action.get('id')}, success={success}, extracted_count={len(output)}, error_count={len(errors)}")
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="extract",
                success=success,
                duration_ms=int((time.monotonic() - start) * 1000),
                output=output,
                error="; ".join(errors) if errors else None,
            )
        except Exception as e:
            logger.error(f"ExtractProcessor error: action_id={action.get('id')}, error={str(e)}", exc_info=True)
            return ActionResult(
                id=action.get("id", ""),
                name=action.get("name", ""),
                type="extract",
                success=False,
                error=str(e),
                duration_ms=int((time.monotonic() - start) * 1000),
            )
