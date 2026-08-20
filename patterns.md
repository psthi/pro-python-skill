## Flat Conditional Structure
**When to use**: replacing a nested pyramid of `if`/`else` blocks with equivalent logic.
**How**: rewrite `if x: if y: ... else: ... else: if...` as a flat `if x and y: ... elif x: ... elif ...: ... else: ...` chain.
**Trade-offs**: more readable at a glance, but may re-evaluate a shared condition (e.g. `x > 0`) multiple times — a problem only if that test is expensive (e.g. a DB query).

## Fallback Import
**When to use**: supporting a module that moved/renamed across Python versions, or an optional third-party dependency.
**How**: `try: from new_location import X except ImportError: from old_location import X as X` (check newer location first); for optional deps, `except ImportError: docutils = None` and check truthiness before use.
**Trade-offs**: adds a try/except at import time; keep the fallback chain short and well-commented.

## Exception Chaining
**When to use**: translating a low-level exception into a more meaningful one without losing the original cause.
**How**: `raise ValueError('Invalid value: %s' % value) from e` — implicit chaining also happens automatically via `__context__` when a second exception occurs during handling of a first.
**Trade-offs**: none significant; strictly improves debuggability over swallowing or blindly re-raising.

## Context Manager Cleanup (`with`)
**When to use**: any setup/teardown pair that must run regardless of exceptions (file handles, locks, connections).
**How**: implement `__enter__`/`__exit__` on the resource object, or simply use an existing one (`with open(path) as f:`).
**Trade-offs**: replaces `try`/`finally` boilerplate entirely; prefer over manual try/finally whenever the resource supports it.

## Memoization
**When to use**: caching results of a deterministic function with a small, low-cardinality, hashable argument space.
**How**: a decorator with a closure-captured `cache = {}` dict keyed by the positional argument tuple; `functools.wraps` to preserve metadata.
**Trade-offs**: unsafe for non-deterministic functions or huge/varied argument spaces (memory growth, stale results).

## Optional-Argument Decorator
**When to use**: a decorator that should work both bare (`@deco`) and with arguments (`@deco(option=val)`).
**How**: make the outer function's first positional arg `func=None`; if `func is None`, return an inner `decorator` closure; else call `decorator(func)` immediately. Require all decorator options be passed by keyword — never positionally.
**Trade-offs**: adds an extra layer of nesting (outer → decorator → wrapper); a positional non-keyword argument can silently mistake itself for the decorated function.

## Decorator-Generating Decorator
**When to use**: many custom decorators in an app repeat the same optional-args/wrapper boilerplate.
**How**: a `decorator()` meta-decorator that accepts a declared function `(func, args, kwargs, **options)` and handles all the wrapping/argument-distinguishing logic once, centrally.
**Trade-offs**: adds an abstraction layer; only worth it once you have several similar decorators.

## Self-Caching Property
**When to use**: expensive-to-compute or expensive-to-fetch attributes (e.g. ORM relationship lookups) read more than once per object lifetime.
**How**: `@property` getter that checks `if name not in self.__dict__: self.__dict__[name] = compute(); return self.__dict__[name]`.
**Trade-offs**: never cache a value dependent on other mutable attributes unless you also invalidate on change; do NOT key the cache on the instance from a dict living in the decorator's own closure (memory leak — keeps every instance alive for the class's lifetime).

## Borg Pattern (Shared-State Mixin)
**When to use**: many instances of a class should share the same state while remaining distinct objects (`is` still returns False between them).
**How**: replace `self.__dict__` in `__new__` (not `__init__`, for mixin robustness) with a dict owned by the class; key per-subclass via `cls._namespace.setdefault(cls, {})` to avoid unintended cross-subclass sharing.
**Trade-offs**: fragile as a mixin if combined with unrelated base classes that don't call `super()` consistently.

## Plugin Mount Point / Registry
**When to use**: a framework needs to auto-discover all subclasses implementing a documented interface.
**How**: a metaclass's `__init__` checks `hasattr(cls, 'plugins')`; if absent, this is the mount point (`cls.plugins = []`); if present, it's a plugin (`cls.plugins.append(cls)`).
**Trade-offs**: requires importing plugin modules somewhere for registration to actually happen; minimal code (~6 lines) for a lot of leverage.

## Metaclass-Based Field Registration (Declarative Framework)
**When to use**: many known-in-advance data-shape configurations, many instances of each, meaningful per-instance behavior — the classic "declarative framework" criteria.
**How**: a `Column`/field base class with `attach_to_class(cls, name, options)`; a metaclass iterating class attributes via duck typing (`hasattr(attr, 'attach_to_class')`) rather than `isinstance` checks, calling that hook to complete field setup and register it into an options/dialect container.
**Trade-offs**: real complexity investment — only justified when the four declarative-framework criteria are actually met; overkill for a single fixed data format.

## Field/Instantiation Ordering
**When to use**: a declarative framework needs to know the order fields were declared in a class body (to line up with e.g. CSV columns).
**How** (in order of robustness): (1) `__prepare__()` returning an `OrderedDict` (Python 3.0+, no counter needed); (2) counter set in `__init__` (fragile — breaks if a subclass skips `super()`); (3) counter set in `__new__` (less fragile); (4) counter set via a separate `CounterMeta.__call__()` (most robust, fully isolated from user-overridable methods).
**Trade-offs**: sort the collected list once after full registration rather than maintaining sorted order incrementally (e.g. via `bisect.insort`) — simpler, and incremental order isn't useful until registration is complete anyway.

## C3 Linearization (MRO Computation)
**When to use**: understanding/debugging why `super()` resolves to a particular class in multiple-inheritance hierarchies.
**How**: iteratively promote the first candidate from each parent's MRO list that doesn't appear in any non-first position across all lists (including the raw base-class list itself, to detect ordering violations); raise `TypeError` if a full pass finds no valid candidate.
**Trade-offs**: you rarely implement this yourself — Python does it — but understanding it demystifies `super()`'s "which class comes next" behavior in complex hierarchies.

## Cooperative `super()` Chaining
**When to use**: overriding a method in a class that participates in multiple inheritance, where multiple ancestors might implement the same method.
**How**: always call `super(ThisClass, self).method(...)` rather than naming a specific parent class directly; relies on the instance's full MRO, not the calling class's isolated parent chain.
**Trade-offs**: requires all classes in the hierarchy to cooperate (call `super()` themselves) or the chain breaks silently.

## Struct-Based Binary Packing
**When to use**: interoperating with binary file formats or network protocols with a fixed byte layout.
**How**: `struct.pack(format, *values)` / `struct.unpack(format, bytes)` with an explicit endianness prefix (`<`/`>`) and correctly-ordered type codes.
**Trade-offs**: format string must exactly match the argument count/order/types on both pack and unpack sides.

## Doctest-as-Documentation
**When to use**: simple, illustrative function behavior that's naturally expressible as "call this, get that."
**How**: write the exact interactive-interpreter transcript inside the docstring; use `...` ellipsis in output to mask non-deterministic content (file paths, addresses).
**Trade-offs**: breaks down for anything needing multi-step setup or nuanced comparison — switch to `unittest` at that point.

## Explicit-Name Assertion Testing
**When to use**: any unit test comparing two values.
**How**: `self.assertEqual(a, b)` rather than `self.assertTrue(a == b)`.
**Trade-offs**: none — strictly better failure diagnostics for the same check.

## Zero-Metaclass Plugin Registry (`__init_subclass__`)
**When to use**: Auto-registering subclasses without introducing metaclass conflicts.
**How**: Define `@classmethod def __init_subclass__(cls, **kwargs): super().__init_subclass__(**kwargs); cls._registry.append(cls)` on the base class.
**Trade-offs**: Clean, standard Python 3.6+ feature; avoids metaclass inheritance friction.

## Structural Subtyping (`typing.Protocol`)
**When to use**: Defining formal interface contracts while keeping classes completely decoupled from base classes.
**How**: Inherit from `typing.Protocol` and decorate with `@runtime_checkable` to support both static analysis and runtime `isinstance()` checks.
**Trade-offs**: Slightly more verbose than raw dunder conventions, but adds complete Mypy/Pyright type safety.

## Type-Preserving Decorator (`ParamSpec`)
**When to use**: Writing decorators without losing IDE signature hints or breaking static type checkers.
**How**: Use `P = ParamSpec("P")` and `R = TypeVar("R")` to annotate `Callable[P, R]`.
**Trade-offs**: Requires Python 3.10+ (or `typing_extensions` on older versions).
