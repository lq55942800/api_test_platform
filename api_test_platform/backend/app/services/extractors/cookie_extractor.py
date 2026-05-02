from typing import Any, Dict
from http.cookiejar import Cookie
from app.core.logging import get_logger
from app.services.extractors.base_extractor import BaseExtractor, ExtractConfig, ExtractResult

logger = get_logger(__name__)


class CookieExtractor(BaseExtractor):
    def extract(self, source_data: Any, config: ExtractConfig) -> ExtractResult:
        logger.info(f"Cookie extraction: expression={config.expression}")
        try:
            cookies = source_data
            if isinstance(cookies, str):
                import json
                try:
                    cookies = json.loads(cookies)
                    logger.debug(f"Parsed cookie source data from string to dict")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse cookie source data as JSON: {str(e)}")
                    return ExtractResult(success=False, error=f"Invalid JSON cookie data: {str(e)}")
            if not isinstance(cookies, dict):
                logger.error(f"Cookie source data is not a dict: type={type(cookies).__name__}")
                return ExtractResult(success=False, error="Source data is not a dict")
            cookie_name = config.expression
            matches = []
            for key, value in cookies.items():
                if key.lower() == cookie_name.lower():
                    matches.append(value)
            if not matches:
                default = config.default_value
                if default:
                    logger.warning(f"Cookie not found, using default value: cookie_name={cookie_name}, default={default}")
                    return ExtractResult(success=True, value=default, match_count=0)
                logger.warning(f"Cookie not found and no default value: cookie_name={cookie_name}")
                return ExtractResult(success=False, match_count=0)
            value = matches[0] if len(matches) == 1 else matches
            logger.debug(f"Cookie extraction result: cookie_name={cookie_name}, match_count={len(matches)}, value={value}")
            return ExtractResult(
                success=True,
                value=value,
                all_matches=matches,
                match_count=len(matches),
            )
        except Exception as e:
            logger.error(f"Cookie extraction error: cookie_name={config.expression}, error={str(e)}")
            default = config.default_value
            if default:
                logger.warning(f"Cookie extraction error, using default value: {default}")
                return ExtractResult(success=True, value=default, match_count=0)
            return ExtractResult(success=False, error=str(e))
