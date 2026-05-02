from typing import Any
from jsonpath_ng import parse as jsonpath_parse
from app.core.logging import get_logger
from app.services.extractors.base_extractor import BaseExtractor, ExtractConfig, ExtractResult

logger = get_logger(__name__)


class JSONPathExtractor(BaseExtractor):
    def extract(self, source_data: Any, config: ExtractConfig) -> ExtractResult:
        logger.info(f"JSONPath extraction: expression={config.expression}")
        try:
            if isinstance(source_data, str):
                import json
                try:
                    source_data = json.loads(source_data)
                    logger.debug(f"Parsed source data from string to JSON for JSONPath extraction")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse source data as JSON: {str(e)}")
                    default = config.default_value
                    if default:
                        logger.warning(f"JSONPath extraction failed, using default value: {default}")
                        return ExtractResult(success=True, value=default, match_count=0)
                    return ExtractResult(success=False, error=f"Invalid JSON source data: {str(e)}", match_count=0)
            expr = jsonpath_parse(config.expression)
            matches = [m.value for m in expr.find(source_data)]
            if not matches:
                default = config.default_value
                if default:
                    logger.warning(f"JSONPath found no matches, using default value: expression={config.expression}, default={default}")
                    return ExtractResult(success=True, value=default, match_count=0)
                logger.warning(f"JSONPath found no matches and no default value: expression={config.expression}")
                return ExtractResult(success=False, match_count=0)
            value = matches[0] if len(matches) == 1 else matches
            logger.debug(f"JSONPath extraction result: expression={config.expression}, match_count={len(matches)}, value={value}")
            return ExtractResult(
                success=True,
                value=value,
                all_matches=matches,
                match_count=len(matches),
            )
        except Exception as e:
            logger.error(f"JSONPath extraction error: expression={config.expression}, error={str(e)}")
            default = config.default_value
            if default:
                logger.warning(f"JSONPath extraction error, using default value: {default}")
                return ExtractResult(success=True, value=default, match_count=0)
            return ExtractResult(success=False, error=str(e))
