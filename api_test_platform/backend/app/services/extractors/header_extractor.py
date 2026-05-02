from typing import Any, Dict
from app.core.logging import get_logger
from app.services.extractors.base_extractor import BaseExtractor, ExtractConfig, ExtractResult

logger = get_logger(__name__)


class HeaderExtractor(BaseExtractor):
    def extract(self, source_data: Any, config: ExtractConfig) -> ExtractResult:
        logger.info(f"Header extraction: expression={config.expression}")
        try:
            headers = source_data
            if isinstance(headers, str):
                import json
                try:
                    headers = json.loads(headers)
                    logger.debug(f"Parsed header source data from string to dict")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse header source data as JSON: {str(e)}")
                    return ExtractResult(success=False, error=f"Invalid JSON header data: {str(e)}")
            if not isinstance(headers, dict):
                logger.error(f"Header source data is not a dict: type={type(headers).__name__}")
                return ExtractResult(success=False, error="Source data is not a dict")
            header_name = config.expression
            matches = []
            for key, value in headers.items():
                if key.lower() == header_name.lower():
                    matches.append(value)
            if not matches:
                default = config.default_value
                if default:
                    logger.warning(f"Header not found, using default value: header_name={header_name}, default={default}")
                    return ExtractResult(success=True, value=default, match_count=0)
                logger.warning(f"Header not found and no default value: header_name={header_name}")
                return ExtractResult(success=False, match_count=0)
            value = matches[0] if len(matches) == 1 else matches
            logger.debug(f"Header extraction result: header_name={header_name}, match_count={len(matches)}, value={value}")
            return ExtractResult(
                success=True,
                value=value,
                all_matches=matches,
                match_count=len(matches),
            )
        except Exception as e:
            logger.error(f"Header extraction error: header_name={config.expression}, error={str(e)}")
            default = config.default_value
            if default:
                logger.warning(f"Header extraction error, using default value: {default}")
                return ExtractResult(success=True, value=default, match_count=0)
            return ExtractResult(success=False, error=str(e))
