# Chapter 12: Modern Python Bridge (Python 3.10 – 3.13+)

## Core Idea
While Marty Alchin's *Pro Python* established the foundational mechanics of Python's object model (MRO, Metaclasses, Descriptors, Dunder Protocols), modern Python (3.10+) introduced clean language-level primitives that replace or simplify legacy boilerplate while preserving the exact same underlying architectural principles.

---

## Direct Evolution Matrix

| Pro Python Legacy Pattern (2010) | Modern Python Primitives (3.10 – 3.13) | Why It's Better |
| :--- | :--- | :--- |
| **Metaclass for Plugin Registration** (`PluginMount(type)`) | `__init_subclass__(cls, **kwargs)` (PEP 487) | No metaclass required; subclasses auto-register cleanly without metaclass conflict issues. |
| **Duck-Typing Dunder Protocols** | `typing.Protocol` + `@runtime_checkable` (PEP 544) | Static type checking (Mypy/Pyright) + runtime `isinstance()` structural checking. |
| **Custom Self-Caching Property** | `@functools.cached_property` (Built-in since 3.8) | Thread-locked, standard descriptor; zero manual `__dict__` manipulation or closure leak risks. |
| **Untyped Decorators / Metadata Loss** | `ParamSpec` + `Concatenate` + `@functools.wraps` (PEP 612) | Exact argument and return type preservation in IDEs and type checkers. |
| **Manual Declarative CSV/ORM Field Registries** | `@dataclass(slots=True)` + `typing.Annotated` (PEP 557/593) | High performance (C-speed `__slots__`), declarative fields, validation metadata via `Annotated`. |
| **Nested `if/elif isinstance` Ladders** | Structural Pattern Matching (`match / case`) (PEP 634) | High-speed, declarative destructuring of objects, sequences, and mappings. |
| **`setup.py` / `MANIFEST.in` Packaging** | `pyproject.toml` (PEP 517/518/621) + `build` / `uv` / `hatch` | Declarative, standardized build specification; no executable Python required during metadata discovery. |
| **Multi-Exception Handling** | `ExceptionGroup` + `except*` (PEP 654 in 3.11+) + `e.add_note()` | First-class handling of concurrent/nested errors (e.g. `asyncio.TaskGroup`). |

---

## Key Modern Frameworks & Code Recipes

### 1. Zero-Metaclass Plugin Registry via `__init_subclass__`
```python
class PluginBase:
    registry: list[type["PluginBase"]] = []

    @classmethod
    def __init_subclass__(cls, plugin_name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_name is not None:
            cls.plugin_name = plugin_name
            cls.registry.append(cls)

# Subclasses auto-register on import:
class JSONExporter(PluginBase, plugin_name="json"):
    pass
```

### 2. Static + Runtime Structural Protocols (`typing.Protocol`)
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Exportable(Protocol):
    def export(self) -> dict[str, str]: ...

# Any object implementing export() satisfies the protocol:
class Report:
    def export(self) -> dict[str, str]:
        return {"title": "Sales Report"}

assert isinstance(Report(), Exportable)  # True at runtime + Type-safe in IDE
```

### 3. Type-Safe Decorators with `ParamSpec`
```python
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def logged(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

### 4. High-Performance Declarative Models (`dataclasses(slots=True)`)
```python
from dataclasses import dataclass, field

@dataclass(slots=True, frozen=True)
class Column:
    name: str
    dtype: str
    nullable: bool = False
```

### 5. Modern `pyproject.toml` Standard
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-library"
version = "1.0.0"
description = "Modern Python Library"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []
```
