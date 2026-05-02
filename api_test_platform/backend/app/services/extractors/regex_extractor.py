import re
from typing import Any
from app.core.logging import get_logger
from app.services.extractors.base_extractor import BaseExtractor, ExtractConfig, ExtractResult

logger = get_logger(__name__)


class RegexExtractor(BaseExtractor):
    def extract(self, source_data: Any, config: ExtractConfig) -> ExtractResult:
        logger.info(f"Regex extraction: expression={config.expression}, template={config.template}")
        try:
            source_str = str(source_data) if not isinstance(source_data, str) else source_data
            pattern = re.compile(config.expression, re.DOTALL)
            all_matches = list(pattern.finditer(source_str))
            if not all_matches:
                default = config.default_value
                if default:
                    logger.warning(f"Regex found no matches, using default value: expression={config.expression}, default={default}")
                    return ExtractResult(success=True, value=default, match_count=0)
                logger.warning(f"Regex found no matches and no default value: expression={config.expression}")
                return ExtractResult(success=False, match_count=0)
            template = config.template or "$1$"
            matches = []
            for m in all_matches:
                if m.groups():
                    result = template
                    for i, group in enumerate(m.groups(), 1):
                        result = result.replace(f"${i}$", group or "")
                    matches.append(result)
                else:
                    matches.append(m.group(0))
            value = matches[0] if len(matches) == 1 else matches
            logger.debug(f"Regex extraction result: expression={config.expression}, match_count={len(matches)}, value={value}")
            return ExtractResult(
                success=True,
                value=value,
                all_matches=matches,
                match_count=len(matches),
            )
        except re.error as e:
            logger.error(f"Regex pattern error: expression={config.expression}, error={str(e)}")
            default = config.default_value
            if default:
                logger.warning(f"Regex pattern error, using default value: {default}")
                return ExtractResult(success=True, value=default, match_count=0)
            return ExtractResult(success=False, error=f"Regex error: {e}")
        except Exception as e:
            logger.error(f"Regex extraction error: expression={config.expression}, error={str(e)}")
            default = config.default_value
            if default:
                logger.warning(f"Regex extraction error, using default value: {default}")
                return ExtractResult(success=True, value=default, match_count=0)
            return ExtractResult(success=False, error=str(e))
