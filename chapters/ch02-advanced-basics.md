# Chapter 2: Advanced Basics

## Core Idea
This chapter covers lesser-known but essential Python techniques — iteration vs. materialized sequences, exception-handling control flow (`try`/`except`/`else`/`finally`, chained exceptions), the `with` statement, comprehensions/generators, useful collection types, and import mechanics — that later chapters build on.

## Frameworks Introduced
- **Iteration vs. whole-sequence use**: decide early whether code needs the full sequence (as an object with methods) or just needs each item once (an iterable). Iterables (like `range()`) don't materialize values in memory until iterated.
  - When to use pure iteration: infinite or large sequences, one-pass consumption, memory-sensitive code.
  - How: generator expressions, `itertools`, or custom iterables (Chapter 5).
- **Exception control-flow blocks (`try`/`except`/`else`/`finally`)**: `else` runs only if the `try` block raised nothing (and didn't itself `return`); `finally` always runs, used for guaranteed cleanup (e.g. closing a file) regardless of exceptions.
  - When to use `else`: code that must run only on success, distinct from cleanup.
  - When to use `finally`: mandatory cleanup (resource release) whether or not an exception occurred.
- **Exception chaining (`__context__` / `raise ... from`)**: preserves the original exception when a new one is raised during handling — implicit via `__context__` when a second exception occurs inside an `except` block; explicit via `raise NewError(...) from original_exception` when deliberately translating one exception type into another (e.g. validation wrapping).
- **The `with` statement / context manager protocol**: replaces manual `try`/`finally` boilerplate for setup/teardown (e.g. file open/close) by delegating to an object's context-manager behavior (`__enter__`/`__exit__`, covered fully in Ch. 5).
- **Comprehensions (list/set/dict) and generator expressions**: concise syntax for "value expression, for clause, optional if filter" — list/set/dict comprehensions materialize a collection immediately; generator expressions (parens instead of brackets) defer computation and are consumed once.
- **Fallback imports**: wrap an `import` in `try`/`except ImportError` to support a moved/renamed module across Python versions, or to make a third-party dependency optional (assign `None` on failure and check truthiness before use).

## Key Concepts
- **`else` clause on `try`**: executes only when no exception was raised in `try` AND the `try` block didn't already `return`.
- **`finally` clause**: always executes after `try`/`except`/`else`, used for cleanup.
- **Context manager**: an object implementing `__enter__`/`__exit__`, usable in a `with` block; e.g. file objects auto-close.
- **Generator**: a lazily-evaluated iterable; once exhausted it cannot be restarted — subsequent iterations yield nothing.
- **`itertools.chain()`**: iterates multiple iterables end-to-end without materializing a combined list.
- **`zip()`**: pairs up multiple iterables element-wise, stopping at the shortest one.
- **`namedtuple`**: factory (from `collections`) producing tuple subclasses with named field access (`point.x`) while still supporting index access (`point[0]`).
- **`OrderedDict`**: dict subclass preserving insertion order (note: pre-3.7 Python's plain `dict` did not guarantee order — this book predates dict ordering becoming a language guarantee in 3.7).
- **`defaultdict`**: dict subclass that auto-creates a default value (via a supplied callable, e.g. `int`, `list`) for missing keys, avoiding manual `get(key, default)` boilerplate.
- **`__all__`**: module-level list restricting what names `from module import *` actually imports; explicit `from module import name` still bypasses it.
- **Relative imports** (`from . import x`, `from .. import y`): resolve module paths relative to the current package rather than an absolute path.
- **`__import__()` vs `importlib.import_module()`**: `__import__('os.path')` returns the top-level `os` module (mirroring `import os.path` semantics); `import_module('os.path')` returns the actual `os.path` submodule directly — prefer `importlib.import_module()` for dynamic imports.

## Mental Models
- **and/or is not a safe ternary substitute**: `x and a or b` silently breaks when `a` itself is falsy (empty string, 0, etc.) — always prefer the real conditional expression `a if x else b`.
- **A cache is optional infrastructure, not a source of truth**: code using a cache must still be able to produce a correct result if the cache is empty/missing, just possibly slower.
- **Generators are "single-use tickets"**: think of iterating a generator as spending it — once exhausted, further iteration attempts return nothing, they don't restart.
- **`while True` + `break` beats a complex boolean condition**: when a loop's exit condition doesn't reduce cleanly to one expression, use `while True` and `break` explicitly — Python also optimizes `while True` by skipping the condition check entirely each iteration.

## Anti-patterns
- **Using bare `except:`**: catches everything including `SystemExit`/`KeyboardInterrupt`, which usually should propagate. Prefer catching specific exception types.
- **Using `and`/`or` chains to emulate a ternary**: breaks silently whenever the "true" branch value is itself falsy — a debugging trap because no exception is raised.
- **Assuming a dict passed to `OrderedDict()` preserves your intended order**: a plain `dict` or keyword arguments are themselves unordered before construction; only sequences (lists, generator expressions) reliably preserve order into `OrderedDict()`.
- **Manually splitting `__import__()`'s return value to reach a submodule**: use `importlib.import_module()` instead — it returns the target submodule directly and avoids re-deriving it via `sys.modules` lookups or attribute-walking.
- **Using asterisk imports (`from module import *`) outside of deliberate namespace-wrapping**: PEP 8 discourages it because it obscures where a name came from; acceptable only when intentionally re-exporting a curated `__all__` from a package's root module (as shown in Ch. 11).

## Code Examples
```python
def count_lines(filename):
    """Count the number of lines in a file."""
    with open(filename, 'r') as file:
        return len(file.readlines())
```
- **What it demonstrates**: the `with` statement replaces manual `try`/`finally` file-closing boilerplate — the context manager (the file object) handles opening and guaranteed closing.

```python
def validate(value, validator):
    try:
        return validator(value)
    except Exception as e:
        raise ValueError('Invalid value: %s' % value) from e
```
- **What it demonstrates**: explicit exception chaining with `raise ... from e` — translates any validator failure into a `ValueError` while preserving the original exception as the documented cause (visible in the traceback and accessible via `__context__`/`__cause__`).

```python
from collections import defaultdict

def count_words(text):
    count = defaultdict(int)
    for word in text.split(' '):
        count[word] += 1
    return count
```
- **What it demonstrates**: `defaultdict(int)` eliminates the manual `count.get(word, 0)` pattern for building frequency counts.

## Reference Tables
| Comprehension type | Syntax | Result |
|---|---|---|
| List | `[expr for x in seq if cond]` | list, eager |
| Set | `{expr for x in seq if cond}` | set, eager |
| Dict | `{k: v for x in seq if cond}` | dict, eager |
| Generator | `(expr for x in seq if cond)` | generator, lazy, single-use |

| Set operator | Method | Meaning |
|---|---|---|
| `\|` | `union()` | items in either set |
| `&` | `intersection()` | items in both sets |
| `-` | `difference()` | items in left set only |
| `^` | `symmetric_difference()` | items in exactly one set |

## Worked Example
The book incrementally builds up `count_lines()` to show the full exception-handling toolkit in context:
1. Bare `try`/`except:` returning 0 on any failure (too broad).
2. Narrowed to `except IOError:`, then generalized to `except EnvironmentError:` (parent of `IOError`/`OSError`).
3. Multiple exception types via a tuple: `except (EnvironmentError, TypeError):`.
4. Logging the caught exception via `except (...) as e: logging.error(e)`.
5. Splitting file-open exceptions from read exceptions using separate `except` clauses.
6. Adding an `else` clause so line-counting only happens if no exception occurred during `open()`.
7. Adding a `finally` block to guarantee `file.close()` runs even when `UnicodeDecodeError` is raised during `readlines()`.
8. Final simplification: replacing the entire `try`/`except`/`finally` scaffold with a single `with open(filename, 'r') as file:` block, since the context manager handles cleanup automatically.

## Key Takeaways
1. Choose between materializing a sequence and pure iteration based on whether you need the whole collection or just one-at-a-time access — iteration is far more memory-efficient for large/infinite sequences.
2. `try`/`except`/`else`/`finally` each have distinct roles: `except` handles specific failures, `else` runs only on success, `finally` always runs for cleanup.
3. Never use `and`/`or` chains as a ternary substitute — use `a if cond else b`, which doesn't break on falsy values.
4. `with` blocks (context managers) are almost always preferable to manual `try`/`finally` for resource cleanup.
5. Generator expressions defer computation and are exhausted after one full iteration; don't expect them to restart.
6. `defaultdict` and `OrderedDict` (from `collections`) solve common dictionary pain points (missing-key defaults, key ordering) without manual boilerplate.
7. Prefer `importlib.import_module()` over raw `__import__()` for dynamic imports — it returns the actual target module, not the top-level package.
8. Use `__all__` to control what an asterisk import exposes, but avoid asterisk imports yourself except when deliberately re-exporting a package's public API.

## Connects To
- **Ch 1 (Principles and Philosophy)**: "errors should never pass silently" underlies the whole exception-handling discussion here; DRY motivates the introspection note.
- **Ch 3 (Functions)**: sequence unpacking here (`domain, *path = ...`) is extended to function argument unpacking; `lambda` is introduced as a `defaultdict` factory argument.
- **Ch 5 (Common Protocols)**: custom iterables/generators, context managers, and dict `get()`/`__getitem__()` distinctions are covered in full there.
- **Ch 7 (Strings)**: Unicode/encoding handling (`UnicodeDecodeError`) is expanded there.
- **Ch 9 (Testing)**: DRY-driven code factoring (isolating utility functions) ties into testability.
- **Ch 11 (Sheets: A CSV Framework)**: the `__all__` re-export pattern for a package root namespace is used there.
