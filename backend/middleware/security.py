import re
import html
from fastapi import Request, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self):
        # Patterns for potentially malicious input
        self.sql_injection_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(and|or)\b\s+\d+\s*[=<>])",
            r"(\b(union|select)\b.*\bfrom\b)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
        ]
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not text:
            return text
        
        # HTML escape
        sanitized = html.escape(text)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    def validate_input(self, text: str, input_type: str = "general") -> bool:
        """Validate input for potential security threats"""
        if not text:
            return True
        
        text_lower = text.lower()
        
        # Check for SQL injection patterns
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected in {input_type}: {text[:50]}...")
                return False
        
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential XSS detected in {input_type}: {text[:50]}...")
                return False
        
        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential path traversal detected in {input_type}: {text[:50]}...")
                return False
        
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        if not password or len(password) < 8:
            return False
        
        # Check for at least one uppercase, lowercase, digit, and special character
        has_upper = re.search(r'[A-Z]', password)
        has_lower = re.search(r'[a-z]', password)
        has_digit = re.search(r'\d', password)
        has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        
        return bool(has_upper and has_lower and has_digit and has_special)

# Global security middleware instance
security_middleware = SecurityMiddleware()

async def security_middleware_func(request: Request, call_next):
    """FastAPI middleware for security validation"""
    try:
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response
        
    except Exception as e:
        logger.error(f"Security middleware error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
