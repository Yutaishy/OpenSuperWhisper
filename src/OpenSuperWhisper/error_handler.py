"""
Comprehensive error handling for OpenSuperWhisper
"""

import sys
import traceback
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import logging
from functools import wraps
from enum import Enum


class ErrorLevel(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    NETWORK = "network"
    API = "api"
    AUDIO = "audio"
    FILE = "file"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


class OpenSuperWhisperError(Exception):
    """Base exception for OpenSuperWhisper"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        level: ErrorLevel = ErrorLevel.ERROR,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.category = category
        self.level = level
        self.details = details or {}
        self.user_message = user_message or message
        self.timestamp = datetime.now()


class NetworkError(OpenSuperWhisperError):
    """Network-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            **kwargs
        )


class APIError(OpenSuperWhisperError):
    """API-related errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        details = kwargs.get('details', {})
        details['status_code'] = status_code
        kwargs['details'] = details
        super().__init__(
            message,
            category=ErrorCategory.API,
            **kwargs
        )


class AudioError(OpenSuperWhisperError):
    """Audio processing errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUDIO,
            **kwargs
        )


class ConfigurationError(OpenSuperWhisperError):
    """Configuration errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            level=ErrorLevel.CRITICAL,
            **kwargs
        )


class ErrorHandler:
    """Centralized error handling and recovery"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_history: list = []
        self.recovery_strategies: Dict[ErrorCategory, Callable] = {}
        self.error_callbacks: Dict[ErrorLevel, list] = {
            level: [] for level in ErrorLevel
        }
        
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        raise_after: bool = False
    ) -> Optional[Any]:
        """
        Handle an error with logging and optional recovery
        
        Args:
            error: The exception to handle
            context: Additional context information
            raise_after: Whether to re-raise the error after handling
            
        Returns:
            Recovery result if applicable
        """
        # Classify error
        if isinstance(error, OpenSuperWhisperError):
            category = error.category
            level = error.level
            user_message = error.user_message
            details = error.details
        else:
            category = self._classify_error(error)
            level = ErrorLevel.ERROR
            user_message = "An unexpected error occurred"
            details = {}
            
        # Add context
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'category': category.value,
            'level': level.value,
            'message': str(error),
            'user_message': user_message,
            'type': type(error).__name__,
            'context': context or {},
            'details': details,
            'traceback': traceback.format_exc()
        }
        
        # Log error
        self._log_error(error_info)
        
        # Store in history
        self.error_history.append(error_info)
        if len(self.error_history) > 100:  # Keep last 100 errors
            self.error_history.pop(0)
            
        # Execute callbacks
        self._execute_callbacks(level, error_info)
        
        # Attempt recovery
        recovery_result = self._attempt_recovery(category, error, context)
        
        # Re-raise if requested
        if raise_after:
            raise error
            
        return recovery_result
        
    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classify an error into a category"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Network errors
        if any(keyword in error_str for keyword in [
            'connection', 'network', 'timeout', 'refused', 'unreachable'
        ]) or any(keyword in error_type for keyword in [
            'connection', 'timeout', 'urlerror'
        ]):
            return ErrorCategory.NETWORK
            
        # API errors
        if any(keyword in error_str for keyword in [
            'api', 'unauthorized', 'forbidden', 'rate limit', 'quota'
        ]):
            return ErrorCategory.API
            
        # Audio errors
        if any(keyword in error_str for keyword in [
            'audio', 'microphone', 'recording', 'sample rate'
        ]):
            return ErrorCategory.AUDIO
            
        # File errors
        if any(keyword in error_str for keyword in [
            'file', 'path', 'directory', 'not found', 'access denied'
        ]) or any(keyword in error_type for keyword in [
            'filenotfound', 'ioerror', 'oserror'
        ]):
            return ErrorCategory.FILE
            
        # Permission errors
        if any(keyword in error_str for keyword in [
            'permission', 'denied', 'unauthorized', 'admin'
        ]):
            return ErrorCategory.PERMISSION
            
        return ErrorCategory.UNKNOWN
        
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error based on level"""
        level = error_info['level']
        message = f"[{error_info['category']}] {error_info['message']}"
        
        if level == ErrorLevel.CRITICAL.value:
            self.logger.critical(message, extra=error_info)
        elif level == ErrorLevel.ERROR.value:
            self.logger.error(message, extra=error_info)
        elif level == ErrorLevel.WARNING.value:
            self.logger.warning(message, extra=error_info)
        else:
            self.logger.info(message, extra=error_info)
            
    def _execute_callbacks(self, level: ErrorLevel, error_info: Dict[str, Any]):
        """Execute registered callbacks for error level"""
        for callback in self.error_callbacks.get(level, []):
            try:
                callback(error_info)
            except Exception as e:
                self.logger.error(f"Error in callback: {e}")
                
    def _attempt_recovery(
        self,
        category: ErrorCategory,
        error: Exception,
        context: Optional[Dict[str, Any]]
    ) -> Optional[Any]:
        """Attempt to recover from error"""
        strategy = self.recovery_strategies.get(category)
        if strategy:
            try:
                return strategy(error, context)
            except Exception as e:
                self.logger.error(f"Recovery failed: {e}")
        return None
        
    def register_recovery_strategy(
        self,
        category: ErrorCategory,
        strategy: Callable
    ):
        """Register a recovery strategy for error category"""
        self.recovery_strategies[category] = strategy
        
    def register_callback(
        self,
        level: ErrorLevel,
        callback: Callable
    ):
        """Register a callback for error level"""
        self.error_callbacks[level].append(callback)
        
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        if not self.error_history:
            return {'total': 0, 'by_category': {}, 'by_level': {}}
            
        summary = {
            'total': len(self.error_history),
            'by_category': {},
            'by_level': {},
            'recent': self.error_history[-5:]  # Last 5 errors
        }
        
        for error in self.error_history:
            category = error['category']
            level = error['level']
            
            summary['by_category'][category] = \
                summary['by_category'].get(category, 0) + 1
            summary['by_level'][level] = \
                summary['by_level'].get(level, 0) + 1
                
        return summary


def with_error_handling(
    handler: ErrorHandler,
    category: Optional[ErrorCategory] = None,
    user_message: Optional[str] = None,
    raise_after: bool = False
):
    """
    Decorator for automatic error handling
    
    Args:
        handler: ErrorHandler instance
        category: Default error category
        user_message: User-friendly error message
        raise_after: Whether to re-raise after handling
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args)[:100],  # Truncate for logging
                    'kwargs': str(kwargs)[:100]
                }
                
                if isinstance(e, OpenSuperWhisperError):
                    # Already classified error
                    return handler.handle_error(e, context, raise_after)
                else:
                    # Create wrapped error
                    wrapped_error = OpenSuperWhisperError(
                        str(e),
                        category=category or ErrorCategory.UNKNOWN,
                        user_message=user_message or "Operation failed"
                    )
                    return handler.handle_error(wrapped_error, context, raise_after)
                    
        return wrapper
    return decorator


# Global error handler instance
_global_handler = None


def get_global_error_handler() -> ErrorHandler:
    """Get or create global error handler"""
    global _global_handler
    if _global_handler is None:
        _global_handler = ErrorHandler()
        _setup_default_strategies(_global_handler)
    return _global_handler


def _setup_default_strategies(handler: ErrorHandler):
    """Setup default recovery strategies"""
    
    def network_recovery(error: Exception, context: Dict[str, Any]):
        """Simple network error recovery"""
        return {
            'recovered': False,
            'message': 'Please check your internet connection',
            'retry_after': 5
        }
        
    def api_recovery(error: Exception, context: Dict[str, Any]):
        """API error recovery"""
        if 'rate limit' in str(error).lower():
            return {
                'recovered': False,
                'message': 'Rate limit exceeded. Please wait before retrying.',
                'retry_after': 60
            }
        return {
            'recovered': False,
            'message': 'API error occurred. Please check your API key.',
            'retry_after': 10
        }
        
    handler.register_recovery_strategy(ErrorCategory.NETWORK, network_recovery)
    handler.register_recovery_strategy(ErrorCategory.API, api_recovery)