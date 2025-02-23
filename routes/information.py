from fastapi import APIRouter, Request, HTTPException, Depends
from models import ResponseAdvice, UserInput
from services import calculate_full
from config import settings
from limiter import limiter  # Assuming limiter is defined elsewhere
from cache import get_cache, set_cache, get_redis_client
import redis.asyncio as redis

router = APIRouter(prefix="/information", tags=["Financial Advice"])

@router.post(
    "",
    response_model=ResponseAdvice,
    summary="Calculate financial savings plan",
    description="Returns a savings plan based on income, expenses, and investment scenarios.",
)
@limiter.limit(settings.RATE_LIMIT)
async def get_financial_advice(
    request: Request,
    user_input: UserInput,
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """
    Calculate financial advice based on user input with caching.

    - **user_input**: Financial details including income, expenses, and goals.
    - Returns: Savings recommendations for optimistic, base, and pessimistic scenarios.
    """
    cache_key = f"advice:{hash(str(user_input))}"
    try:
        # Check cache using the injected redis_client
        cached_result = await get_cache(cache_key, redis_client)
        if cached_result:
            return ResponseAdvice.parse_raw(cached_result)

        # Calculate and cache
        result = await calculate_full(user_input)
        await set_cache(cache_key, result.json(), redis_client=redis_client)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except redis.RedisError as e:
        # Fallback to calculation if Redis fails
        result = await calculate_full(user_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")