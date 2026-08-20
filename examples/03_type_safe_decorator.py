#!/usr/bin/env python3
"""
Example 3: Modern Type-Safe Decorator with ParamSpec (PEP 612)
"""

from functools import wraps
from typing import Callable, ParamSpec, TypeVar
import time

P = ParamSpec("P")
R = TypeVar("R")

def timing(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"[{func.__name__}] executed in {duration:.6f}s")
        return result
    return wrapper

@timing
def compute_squares(n: int) -> int:
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    res = compute_squares(100000)
    print(f"Result: {res}")
