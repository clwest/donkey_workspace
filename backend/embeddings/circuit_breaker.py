"""
Circuit Breaker Pattern Implementation

This module implements the circuit breaker pattern to prevent system
overloading when services are failing. It monitors for failures and
temporarily disables a service when it exceeds a failure threshold.

The circuit breaker has three states:
- CLOSED: Service is operating normally
- OPEN: Service is disabled due to too many failures
- HALF_OPEN: After a timeout, service is tested again to see if it recovered
"""

import time
import logging
import threading
import functools
from enum import Enum
from typing import Callable, Any, Dict, Optional

logger = logging.getLogger("django")


class CircuitState(Enum):
    """Possible states for the circuit breaker."""

    CLOSED = 0  # Normal operation
    OPEN = 1  # Service disabled temporarily
    HALF_OPEN = 2  # Testing if service is recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for services.

    This class implements the circuit breaker pattern to prevent repeated
    calls to failing services. It tracks failures and temporarily disables
    a service when it exceeds a failure threshold.

    Attributes:
        name (str): Name of the service being protected
        failure_threshold (int): Number of failures before opening the circuit
        reset_timeout (float): Time in seconds to wait before trying service again
        state (CircuitState): Current state of the circuit
        failure_count (int): Current count of consecutive failures
        last_failure_time (float): Timestamp of the last failure
    """

    # Class-level registry of circuit breakers
    _registry: Dict[str, "CircuitBreaker"] = {}
    _lock = threading.RLock()

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        initial_state: CircuitState = CircuitState.CLOSED,
    ):
        """
        Initialize a new circuit breaker.

        Args:
            name: Unique name for the service being protected
            failure_threshold: Number of failures before tripping circuit
            reset_timeout: Time in seconds to wait before trying again
            initial_state: Initial state for the circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = initial_state
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.success_threshold = 2  # Successes needed in HALF-OPEN to close
        self.half_open_successes = 0

        # Register this circuit breaker in class registry
        with self._lock:
            self._registry[name] = self

    @classmethod
    def get(cls, name: str) -> Optional["CircuitBreaker"]:
        """Get a circuit breaker by name from the registry."""
        return cls._registry.get(name)

    @classmethod
    def get_or_create(
        cls, name: str, failure_threshold: int = 5, reset_timeout: float = 60.0
    ) -> "CircuitBreaker":
        """Get a circuit breaker by name or create a new one if it doesn't exist."""
        with cls._lock:
            if name not in cls._registry:
                cls._registry[name] = cls(name, failure_threshold, reset_timeout)
            return cls._registry[name]

    def on_success(self) -> None:
        """Handle a successful call through the circuit."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                # Normal operation - reset failure count
                self.failure_count = 0
            elif self.state == CircuitState.HALF_OPEN:
                # In testing phase - count successful calls
                self.half_open_successes += 1
                if self.half_open_successes >= self.success_threshold:
                    # Service has recovered - close the circuit
                    self.close()

    def on_failure(self) -> None:
        """Handle a failed call through the circuit."""
        with self._lock:
            self.last_failure_time = time.time()

            if self.state == CircuitState.CLOSED:
                # Normal operation - increment failure count
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    # Too many failures - open the circuit
                    self.open()
            elif self.state == CircuitState.HALF_OPEN:
                # Failed during testing - reopen the circuit
                self.open()

    def open(self) -> None:
        """Open the circuit to prevent more calls."""
        self.state = CircuitState.OPEN
        self.half_open_successes = 0
        logger.warning(
            f"🔌 Circuit {self.name} OPENED after {self.failure_count} consecutive failures"
        )

    def close(self) -> None:
        """Close the circuit to resume normal operation."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_successes = 0
        logger.info(f"🔌 Circuit {self.name} CLOSED - service recovered")

    def half_open(self) -> None:
        """Half-open the circuit to test if service recovered."""
        self.state = CircuitState.HALF_OPEN
        self.half_open_successes = 0
        logger.info(f"🔌 Circuit {self.name} HALF-OPEN - testing service")

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed through the circuit.

        Returns:
            bool: True if request should be allowed, False otherwise
        """
        with self._lock:
            if self.state == CircuitState.CLOSED:
                # Normal operation - allow all requests
                return True
            elif self.state == CircuitState.OPEN:
                # Circuit is open - check if timeout expired
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.reset_timeout:
                    # Timeout expired - try half-open state
                    self.half_open()
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                # Testing mode - allow limited requests
                return True

            # Default safety
            return False


def circuit_protected(
    circuit_name: str,
    failure_threshold: int = 5,
    reset_timeout: float = 60.0,
    fallback: Optional[Callable] = None,
):
    """
    Decorator to protect a function with a circuit breaker.

    This decorator wraps a function with circuit breaker protection.
    When the circuit is open, calls to the function will be prevented
    and either raise an exception or call a fallback function.

    Args:
        circuit_name: Name of the circuit breaker to use
        failure_threshold: Number of failures before opening circuit
        reset_timeout: Time in seconds before trying service again
        fallback: Optional function to call when circuit is open

    Returns:
        callable: Decorated function

    Example:
        @circuit_protected("embedding-service", fallback=lambda *args, **kwargs: None)
        def generate_embedding(text):
            # Implementation
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create the circuit breaker
            breaker = CircuitBreaker.get_or_create(
                circuit_name, failure_threshold, reset_timeout
            )

            # Check if we should allow the request
            if not breaker.allow_request():
                logger.warning(
                    f"🔌 Circuit {circuit_name} is OPEN - "
                    f"blocking call to {func.__name__}"
                )

                # Handle blocked request
                if fallback:
                    return fallback(*args, **kwargs)
                else:
                    raise CircuitOpenError(
                        f"Circuit {circuit_name} is open - "
                        f"service {func.__name__} is unavailable"
                    )

            # Execute the protected function
            try:
                result = func(*args, **kwargs)
                breaker.on_success()
                return result
            except Exception as e:
                breaker.on_failure()
                raise

        return wrapper

    return decorator


class CircuitOpenError(Exception):
    """Exception raised when a circuit is open and a fallback is not provided."""

    pass
