from typing import Any

from google import genai
from google.genai import types, errors

from app.core.config import settings
from app.core.logging import get_logger
from app.models.reconcile import (
    ReconcileMedicationRequest,
    ReconcileMedicationResponse,
)
from app.models.data_quality import (
    DataQualityRequest,
    DataQualityResponse,
)
from app.services.prompts import (
    build_reconcile_prompt,
    build_data_quality_prompt,
)
from app.services.cache import SimpleCache, hash_request

logger = get_logger(__name__)


g_client = genai.Client(api_key=settings.GEMINI_API_KEY)

GEMINI_MODELS = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
]

_cache = SimpleCache(
    ttl=settings.CACHE_TTL,
    max_size=settings.CACHE_MAX_SIZE
) if settings.CACHE_ENABLED else None


class RateLimitError(Exception):
    """Raised when Gemini rate limit is hit."""
    pass


class GeminiError(Exception):
    """Raised when Gemini API call fails."""
    pass


def _generate_with_model(prompt: str, schema: dict[str, Any], model: str, temperature: float = 0.2) -> str:
    logger.debug(f"Calling Gemini model: {model}")
    try:
        response = g_client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=temperature,
            ),
        )
    except errors.ClientError as exc:
        if exc.status_code == 429:
            logger.warning(f"Rate limit exceeded for model {model}")
            raise RateLimitError(f"Rate limit exceeded for model {model}") from exc
        logger.error(f"Gemini client error for model {model}: {str(exc)}")
        raise GeminiError(f"Gemini client error: {str(exc)}") from exc
    except errors.ServerError as exc:
        logger.error(f"Gemini server error for model {model}: {str(exc)}")
        raise GeminiError(f"Gemini service unavailable: {str(exc)}") from exc
    except errors.APIError as exc:
        logger.error(f"Gemini API error for model {model}: {str(exc)}")
        raise GeminiError(f"Gemini API error: {str(exc)}") from exc
    except Exception as exc:
        logger.error(f"Unexpected error for model {model}: {str(exc)}")
        raise GeminiError(f"Unexpected error: {str(exc)}") from exc

    raw_json = getattr(response, "text", None)
    if not raw_json:
        logger.error(f"Gemini returned empty response for model {model}")
        raise GeminiError(f"Gemini returned empty response for model {model}")

    logger.debug(f"Successfully received response from {model}")
    return raw_json


def _generate_with_fallback_models(prompt: str, schema: dict[str, Any], temperature: float = 0.2) -> str:
    last_error: Exception | None = None

    for model_name in GEMINI_MODELS:
        try:
            return _generate_with_model(prompt, schema, model=model_name, temperature=temperature)
        except RateLimitError as exc:
            last_error = exc
            continue
        except GeminiError:
            raise

    if last_error:
        raise RateLimitError("All Gemini models rate limited") from last_error

    raise GeminiError("All models failed without specific error")


def reconcile_with_gemini(
    payload: ReconcileMedicationRequest,
    temperature: float = 0.2,
) -> ReconcileMedicationResponse:
    logger.info("Starting medication reconciliation")
    if _cache:
        cache_key = hash_request(payload.model_dump())
        cached = _cache.get(cache_key)
        if cached:
            logger.info("Cache hit for reconciliation request")
            return ReconcileMedicationResponse.model_validate_json(cached)

    logger.debug("Cache miss, calling Gemini API")
    prompt = build_reconcile_prompt(payload)
    raw_json = _generate_with_fallback_models(
        prompt,
        schema=ReconcileMedicationResponse.model_json_schema(),
        temperature=temperature,
    )

    if _cache:
        cache_key = hash_request(payload.model_dump())
        _cache.set(cache_key, raw_json)
        logger.debug("Response cached")

    logger.info("Medication reconciliation completed successfully")
    return ReconcileMedicationResponse.model_validate_json(raw_json)


def evaluate_data_quality_with_gemini(
    payload: DataQualityRequest,
    temperature: float = 0.2,
) -> DataQualityResponse:
    logger.info("Starting data quality evaluation")
    if _cache:
        cache_key = hash_request(payload.model_dump())
        cached = _cache.get(cache_key)
        if cached:
            logger.info("Cache hit for data quality request")
            return DataQualityResponse.model_validate_json(cached)

    logger.debug("Cache miss, calling Gemini API")
    prompt = build_data_quality_prompt(payload)
    raw_json = _generate_with_fallback_models(
        prompt,
        schema=DataQualityResponse.model_json_schema(),
        temperature=temperature,
    )

    if _cache:
        cache_key = hash_request(payload.model_dump())
        _cache.set(cache_key, raw_json)
        logger.debug("Response cached")

    logger.info("Data quality evaluation completed successfully")
    return DataQualityResponse.model_validate_json(raw_json)
