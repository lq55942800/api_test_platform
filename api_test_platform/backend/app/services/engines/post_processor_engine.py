from typing import Any, Dict, List
from app.core.logging import get_logger
from app.services.engines.variable_manager import VariableManager
from app.services.extractors.extractor_engine import ExtractorEngine
from app.services.processors.base_processor import ActionResult
from app.services.processors.extract_processor import ExtractProcessor
from app.services.processors.script_processor import ScriptProcessor
from app.services.processors.database_processor import DatabaseProcessor

logger = get_logger(__name__)


class PostProcessorEngine:
    PROCESSOR_MAP = {
        "extract": ExtractProcessor,
        "script": ScriptProcessor,
        "database": DatabaseProcessor,
    }

    def __init__(self, variable_manager: VariableManager, extractor_engine: ExtractorEngine):
        self.variable_manager = variable_manager
        self.extractor_engine = extractor_engine

    async def execute(self, actions: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"PostProcessorEngine executing: action_count={len(actions)}")
        sorted_actions = sorted(
            [a for a in actions if a.get("enabled", True)],
            key=lambda a: a.get("order", 0),
        )
        logger.debug(f"PostProcessorEngine: enabled actions after filtering: {len(sorted_actions)}")
        results: List[ActionResult] = []
        for action in sorted_actions:
            action_type = action.get("type", "")
            action_id = action.get("id", "")
            action_name = action.get("name", "")
            processor_cls = self.PROCESSOR_MAP.get(action_type)
            if not processor_cls:
                logger.warning(f"Unknown post-processor type: {action_type}, action_id={action_id}")
                results.append(ActionResult(
                    id=action_id,
                    name=action_name,
                    type=action_type,
                    success=False,
                    error=f"Unknown processor type: {action_type}",
                ))
                continue
            logger.debug(f"Executing post-processor: type={action_type}, action_id={action_id}, action_name={action_name}")
            processor = processor_cls(self.variable_manager, self.extractor_engine)
            result = await processor.execute(action, context)
            results.append(result)
            logger.debug(f"Post-processor result: type={action_type}, action_id={action_id}, success={result.success}, duration_ms={result.duration_ms}")
            config = action.get("config", {})
            on_error = config.get("on_error", "abort")
            if not result.success and on_error == "abort":
                logger.warning(f"Post-processor failed, aborting: action_id={action_id}, error={result.error}")
                break
        all_success = all(r.success for r in results)
        logger.info(f"PostProcessorEngine completed: total={len(results)}, success={all_success}")
        return {
            "success": all_success,
            "results": [r.model_dump() for r in results],
        }
