import time
import redis
import os
from fastapi import HTTPException, Request
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        self.rate_limit_per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
        
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Rate limiting will be disabled.")
            self.redis_client = None
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _get_user_identifier(self, request: Request) -> str:
        """Get user identifier for rate limiting"""
        # Try to get user from JWT token first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # For authenticated users, use token hash as identifier
            return f"user:{hash(auth_header)}"
        
        # For unauthenticated users, use IP address
        return f"ip:{self._get_client_ip(request)}"
    
    def check_rate_limit(self, request: Request) -> bool:
        """Check if request is within rate limits"""
        if not self.redis_client:
            return True  # Allow if Redis is not available
        
        try:
            identifier = self._get_user_identifier(request)
            current_time = int(time.time())
            
            # Check per-minute limit
            minute_key = f"rate_limit:{identifier}:minute:{current_time // 60}"
            minute_count = self.redis_client.get(minute_key)
            
            if minute_count and int(minute_count) >= self.rate_limit_per_minute:
                logger.warning(f"Rate limit exceeded for {identifier} (per minute)")
                return False
            
            # Check per-hour limit
            hour_key = f"rate_limit:{identifier}:hour:{current_time // 3600}"
            hour_count = self.redis_client.get(hour_key)
            
            if hour_count and int(hour_count) >= self.rate_limit_per_hour:
                logger.warning(f"Rate limit exceeded for {identifier} (per hour)")
                return False
            
            # Increment counters
            pipe = self.redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow if rate limiting fails

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting"""
    if not rate_limiter.check_rate_limit(request):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    response = await call_next(request)
    return response
