# Chapter 3: Functions

## Core Idea
Python functions are full-fledged objects with rich argument-handling flexibility (positional, keyword, variable `*args`/`**kwargs`, keyword-only), and this flexibility underlies two of Python's most powerful techniques covered here: closures (which enable decorators and partial application) and function annotations (which enable runtime introspection-based validation).

## Frameworks Introduced
- **Argument ordering rule**: required → optional → variable positional (`*args`) → variable keyword (`**kwargs`); Python 3.0+ also allows explicit keyword-only arguments after `*args`, which must then be passed by keyword.
  - When to use `*args`: a function accepts an arbitrary number of positional items (e.g. `add_to_cart(*items)`).
  - When to use `**kwargs`: a function accepts arbitrary named configuration (e.g. `__init__(self, **options)`).
- **Partial application** (`functools.partial`): preloads some arguments of a function now, returning a new callable that fills in the rest later. Distinct from true currying — a partial always attempts to execute when called, raising `TypeError` if still missing required args; a curried function keeps returning new partially-applied functions until fully satisfied.
- **Closures**: an inner function defined inside an outer function that captures ("closes over") the outer function's variables, and is then returned/used outside that outer function. Requires the inner function to be *defined inside* the outer scope — passing a function in as an argument does not create a closure.
- **Decorators**: functions that accept a function and return a function (usually a wrapper). Applied with `@decorator_name` syntax above a function definition, equivalent to `func = decorator_name(func)`.
  - How to build a basic decorator: define an outer function taking `func`, define an inner `wrapper(*args, **kwargs)` that calls `func(*args, **kwargs)` with added behavior, `return wrapper`.
  - Use `functools.wraps(func)` on the wrapper to preserve `__name__`/`__doc__` (though not the argument list) of the original function.
- **Decorators with optional arguments**: to support both `@my_decorator` and `@my_decorator(option=value)`, make the outer function's first positional argument `func=None`; if `func is None` the call supplied only keyword arguments, so return the inner `decorator` closure; otherwise the function itself was passed directly, so call `decorator(func)` immediately. Any decorator arguments must be passed by keyword — there is no reliable way to distinguish "decorator argument" from "the function being decorated" positionally.
- **Function annotations** (`def f(x: int) -> str:`): attach an arbitrary expression to any argument or the return value; Python attaches no built-in meaning — the intent is to let third-party libraries (type checkers, doc generators, validators) interpret them.
- **Introspection via `inspect`**: `inspect.getfullargspec(func)` returns a named tuple (`args`, `varargs`, `varkw`, `defaults`, `kwonlyargs`, `kwonlydefaults`, `annotations`) describing a function's full signature — used to build generic argument-inspecting/validating utilities.

## Key Concepts
- **Variable positional arguments (`*args`)**: collects any extra positional arguments into a tuple.
- **Variable keyword arguments (`**kwargs`)**: collects any extra keyword arguments into a dict (mutable — unlike the immutable tuple from `*args`).
- **Keyword-only arguments**: arguments declared after a bare `*` (or after `*args`) that can only be supplied by keyword, never positionally.
- **Closure**: a function object that retains access to variables from its enclosing scope after that enclosing function has returned.
- **Wrapper**: the inner function returned by a decorator; typically accepts `*args, **kwargs` so it can stand in for any function signature.
- **`functools.wraps`**: a decorator-on-a-decorator that copies `__name__`/`__doc__`/other metadata from the original function onto the wrapper.
- **Memoization**: caching a deterministic function's return value keyed by its (positional) argument tuple, so repeat calls with the same arguments skip recomputation.
- **`__name__`, `__doc__`, `__module__`**: introspectable attributes on every function object — name, docstring, and defining module path respectively. Lambdas report `__name__` as `'<lambda>'`.
- **`inspect.getdoc()`**: retrieves and normalizes a docstring's indentation (unlike raw `__doc__`, which preserves the original whitespace/indentation verbatim).
- **`isinstance(obj, type)`**: preferred over `type(obj) == type` for checking whether an object is of an expected type, since it also accounts for subclasses.

## Mental Models
- **Think of `*args`/`**kwargs` as "the leftovers bucket"**: any positional/keyword values that don't match an explicit named argument fall through into these.
- **A decorator chain is "a function factory that returns a function factory"**: for decorators with optional arguments, there are up to three layers — the outer function (accepts decorator args), the `decorator` closure (accepts the function to wrap), and the `wrapper` closure (executes with the real call args).
- **Closures capture variables, not values, by reference to the enclosing scope**: the classic pitfall (not covered verbatim in this chapter but implied by the `multiply_by`/`custom_operator` contrast) is that a function only closes over a variable if it's genuinely nested inside the scope that defines that variable — passing a function in as an argument does not grant it access to the caller's locals.
- **Annotations are "documentation the interpreter doesn't act on by default"**: unlike statically-typed languages, Python attaches zero built-in behavior to annotations; any enforcement (like a `typesafe` decorator) must be built by a library that reads `__annotations__` itself.

## Anti-patterns
- **Accepting a raw dict for configuration instead of `**kwargs`**: forces callers to write out full dict literals (`ShoppingCart({'currency': 'USD'})`) instead of clean keyword syntax (`ShoppingCart(currency='USD')`), and breaks any code relying on prior explicit keyword arguments.
- **Positional-only decorator arguments**: if a decorator's first optional positional argument could itself be a function (e.g. a logger callback) and is passed positionally, the decorator can silently mistake it for the function being decorated — the function being decorated then "vanishes" (the decorator call returns the logger's return value, typically `None`). Always require decorator options to be passed by keyword.
- **Passing a function as an argument and expecting closure behavior**: closures only work when the inner function is *defined inside* the outer function's body — merely receiving a function as a parameter (as in the `custom_operator` counter-example) does not grant access to the outer scope's variables and raises `NameError`.
- **Memoizing non-deterministic functions, or functions with highly varied arguments**: memoization assumes the same arguments always produce the same result; using it on a function with side effects or huge argument variety wastes memory and produces stale/incorrect cached results.
- **Reading raw `__doc__` when you want normalized text**: raw docstrings retain source-file indentation and leading/trailing whitespace; use `inspect.getdoc()` for library/doc-generation use cases.

## Code Examples
```python
def suppress_errors(func=None, log_func=None):
    """Automatically silence any errors that occur within a function"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_func is not None:
                    log_func(str(e))
        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)
```
- **What it demonstrates**: a decorator usable both as `@suppress_errors` (no parens, function passed positionally) and `@suppress_errors(log_func=print_logger)` (keyword-argument form) — the `func is None` check distinguishes which call pattern was used.

```python
def memoize(func):
    """Cache the results of the function so it doesn't need to be called
    again, if the same arguments are provided a second time."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrapper
```
- **What it demonstrates**: memoization via a closure over a `cache` dict keyed by the positional argument tuple — only works for deterministic functions called with hashable positional arguments.

```python
@memoize
def factorial(x):
    result = 1
    for i in range(x):
        result *= i + 1
    return result
```
- **What it demonstrates**: applying `memoize` to a real recursive-style computation; repeat calls with the same `x` skip recomputation entirely.

## Worked Example
The book builds a generic argument-inspection utility (`get_arguments()`) step by step using `inspect.getfullargspec()`:
1. Start with just keyword arguments: `arguments = kwargs.copy()`.
2. Add positional-argument names via `zip(spec.args, args)` and `arguments.update(...)`.
3. Fill in unspecified default values for optional positional arguments by zipping `reversed(spec.args)` with `reversed(spec.defaults)` (defaults always align to the end of the positional list).
4. Fill in keyword-only defaults directly from `spec.kwonlydefaults` (already a dict).
5. Final concise version builds the defaults dict *first*, then overlays explicit call-time values on top — mirroring how defaults conceptually work (provided first, then overridden), rather than checking "is this already set" repeatedly.
6. Extends into `validate_arguments()`: cross-references `declared_args` (explicit + keyword-only names) against the resolved `arguments` dict to flag both missing required arguments and unexpected/unknown ones — with the caveat that variable positional arguments (`*args`) can't be validated this way since they have no names.

This progression illustrates a real Pythonic refactoring instinct: get something working simply first, then simplify once the shape of the problem is clear.

## Key Takeaways
1. Prefer `*args`/`**kwargs` over accepting raw lists/dicts for variable arguments — it keeps the common single-argument call clean and doesn't break existing calls when extended.
2. Closures require the inner function to be defined *inside* the outer function's scope — passing a function in as a parameter does not create the same effect.
3. Always use `functools.wraps(func)` inside a decorator's wrapper to preserve the original function's `__name__`/`__doc__`.
4. To support a decorator with optional arguments, distinguish "called with the function directly" from "called with keyword configuration" by defaulting the first positional argument to `func=None` and always requiring decorator options to be passed by keyword.
5. `functools.partial()` differs from currying: a partial always tries to execute when called (raising `TypeError` if arguments are still missing), whereas a truly curried function keeps returning new partial functions until fully satisfied.
6. Function annotations (`def f(x: int) -> str`) carry no built-in runtime behavior — they're metadata for third-party tooling to interpret (type checkers, validators, doc generators).
7. Use `inspect.getfullargspec()` to build generic, signature-aware utilities (argument loggers, validators) rather than hardcoding assumptions about a function's parameters.
8. Memoization is a powerful but narrow optimization — safe only for deterministic functions with a small, hashable, low-cardinality argument space.

## Connects To
- **Ch 2 (Advanced Basics)**: sequence unpacking (`*path`) is the same asterisk mechanism as variable positional arguments; `defaultdict`'s callable-factory argument pattern connects to lambdas as inline factories.
- **Ch 4 (Classes)**: `isinstance()`/`type()` introspection introduced here is expanded fully into classes, metaclasses, and type systems.
- **Ch 5 (Common Protocols)**: iterator restart behavior, and the underlying protocol that makes decorators/wrappers work with arbitrary callables, is covered there.
- **Ch 6 (Object Management)**: this chapter's `__module__`/`__name__`/`__doc__` introspection groundwork is built on further for object identity/lifecycle discussion.
- **Ch 11 (Sheets: A CSV Framework)**: decorator-based field registration and metaclass patterns introduced conceptually here (function-as-object, wrapping) are the direct precursor to that chapter's descriptor-based framework.
