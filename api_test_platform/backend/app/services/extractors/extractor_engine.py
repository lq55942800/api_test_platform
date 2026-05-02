from typing import Any, Dict, Optional
from app.core.logging import get_logger
from app.services.extractors.base_extractor import BaseExtractor, ExtractConfig, ExtractResult
from app.services.extractors.jsonpath_extractor import JSONPathExtractor
from app.services.extractors.regex_extractor import RegexExtractor
from app.services.extractors.header_extractor import HeaderExtractor
from app.services.extractors.cookie_extractor import CookieExtractor

logger = get_logger(__name__)


class DirectExtractor(BaseExtractor):
    def extract(self, source_data: Any, config: ExtractConfig) -> ExtractResult:
        return ExtractResult(success=True, value=source_data)


class ExtractorEngine:
    EXTRACTOR_MAP: Dict[str, BaseExtractor] = {
        "jsonpath": JSONPathExtractor(),
        "regex": RegexExtractor(),
        "header": HeaderExtractor(),
        "cookie": CookieExtractor(),
        "direct": DirectExtractor(),
    }

    SOURCE_MAP = {
        "response_json": "body",
        "response_text": "body",
        "response_header": "header",
        "response_cookie": "cookie",
        "elapsed_time": "elapsed_ms",
    }

    SOURCE_TYPE_MAP = {
        "response_json": "jsonpath",
        "response_text": "regex",
        "response_header": "header",
        "response_cookie": "cookie",
        "elapsed_time": "direct",
    }

    def extract(self, source_data: Any, config: ExtractConfig) -> ExtractResult:
        logger.info(f"Extracting data: extract_type={config.extract_type}, expression={config.expression}")
        extractor = self.EXTRACTOR_MAP.get(config.extract_type)
        if not extractor:
            logger.error(f"Unknown extract type: {config.extract_type}")
            return ExtractResult(
                success=False,
                error=f"Unknown extract type: {config.extract_type}",
            )
        result = extractor.extract(source_data, config)
        logger.debug(f"Extraction result: extract_type={config.extract_type}, success={result.success}, value={result.value}, match_count={result.match_count}")
        if not result.success and not config.default_value:
            logger.warning(f"Extraction failed and no default value: extract_type={config.extract_type}, expression={config.expression}, error={result.error}")
        return result

    def extract_from_response(
        self,
        response_data: Dict[str, Any],
        source: str,
        config: ExtractConfig,
    ) -> ExtractResult:
        logger.info(f"Extracting from response: source={source}, extract_type={config.extract_type}, expression={config.expression}")
        backend_source = self.SOURCE_MAP.get(source, source)
        extract_type = self.SOURCE_TYPE_MAP.get(source, config.extract_type)

        source_data_map = {
            "body": response_data.get("body", ""),
            "header": response_data.get("headers", {}),
            "cookie": response_data.get("cookies", {}),
            "status_code": str(response_data.get("status_code", "")),
            "url": response_data.get("url", ""),
            "elapsed_ms": response_data.get("elapsed_ms", 0),
        }
        source_data = source_data_map.get(backend_source, response_data.get("body", ""))

        if backend_source not in source_data_map:
            logger.warning(f"Unknown source '{source}' (mapped to '{backend_source}'), falling back to body")

        logger.debug(f"Response extraction: source={source}, backend_source={backend_source}, extract_type={extract_type}")

        if extract_type != config.extract_type:
            config = config.model_copy(update={"extract_type": extract_type})
            logger.debug(f"Extract type overridden by source mapping: {config.extract_type} -> {extract_type}")

        result = self.extract(source_data, config)
        logger.debug(f"Response extraction completed: source={source}, success={result.success}")
        return result

    def get_supported_types(self) -> list:
        return list(self.EXTRACTOR_MAP.keys())
