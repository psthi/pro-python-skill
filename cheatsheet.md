## Decision Rules

**When to raise vs. return `None` on failure**
→ Raise an exception. Never return `None`/an ambiguous sentinel to signal an error (Samurai Principle) — it forces every caller to remember to check, and `None` may itself be a valid legitimate value in other contexts.

**When to use `*args`/`**kwargs` vs. an explicit list/dict argument**
→ Use `*args`/`**kwargs`. A raw list/dict argument sabotages the common single-value call case and breaks existing calls when a function's argument count later changes.

**When ambiguous input data arrives (e.g. unknown string encoding)**
→ Refuse to guess. Require the caller to be explicit (accept only Unicode, not byte strings of unknown provenance) rather than picking a "likely" default.

**When choosing between `and`/`or` chains and a real conditional expression**
→ Always use `a if cond else b`. The `x and a or b` idiom silently breaks whenever `a` itself is falsy (empty string, 0, `[]`).

**When a decorator needs optional arguments**
→ Make the first positional argument `func=None`; check `if func is None` to distinguish "called bare" from "called with kwargs." Require all decorator options to be passed by keyword, never positionally — a positional logger/callback argument can be silently mistaken for the function being decorated.

**When implementing `__eq__`**
→ Always also implement `__ne__`. Python does NOT derive one from the other automatically.

**When comparing floating-point values in tests**
→ Use `assertAlmostEqual(a, b, places=N)`, never plain `assertEqual` — floating-point arithmetic accumulates rounding error.

**When choosing `assertTrue(a == b)` vs `assertEqual(a, b)`**
→ Always `assertEqual`. Same check, but the failure message reports both actual values ("10 != 42") instead of the uninformative "False is not True."

**When deciding whether to build a declarative framework**
→ Only if you have ALL four: many potential configurations, each known in advance, many instances per configuration, and meaningful actions performable on instances. Missing any one → just write a direct solution.

**When choosing where to put an instantiation-order counter in a framework's field class**
→ Prefer, in order of robustness: `__prepare__()` + `OrderedDict` (Py 3.0+, no counter needed) > counter in `__new__` > counter in `__init__`. Best of all: isolate it in a dedicated metaclass's `__call__()` so a subclass forgetting `super()` in its own `__init__`/`__new__` can't silently break ordering.

**When a metaclass needs to identify "is this attribute a field"**
→ Use duck typing (`hasattr(attr, 'attach_to_class')`), not `isinstance(attr, Column)`. Keeps the framework open to any object implementing the protocol, not just a specific base class.

**When choosing a license for a library meant for broad (including proprietary) adoption**
→ LGPL (removes the static-linking trigger) or a BSD variant (minimal restrictions, attribution only). Use GPL/AGPL only when protecting end-user freedoms outweighs adoption breadth.

**When choosing between `super(SpecificClass, self)` and `super(ThisClass, self)`**
→ Always pass the class you're *currently in*, not some other class in the hierarchy. Passing a different class skips MRO entries unpredictably and can raise `TypeError` if `self` isn't a subtype of the class given.

**When a `with`-block resource is available vs. manual `try`/`finally`**
→ Always prefer `with`. It replaces the boilerplate entirely and the cleanup logic lives with the resource, not scattered across call sites.

**When caching a computed property**
→ Only if the value doesn't depend on other mutable attributes. If it does (e.g. a computed full name from first/last name), caching freezes a stale value the moment a dependency changes.

**When you need multi-pass (repeatable) iteration over a custom sequence**
→ Implement a real `__iter__()` that returns a *fresh* iterator object each call — never rely on a plain generator function for this, since generators exhaust after one pass.

## Thresholds & Defaults

- **Version numbering**: major.minor.patch — major = compatibility promise, minor = features/fixes without breaking compatibility, patch = security/bugfix only.
- **`round()` without a second argument**: returns an int. With a second argument (even `0`): returns the same type passed in.
- **`__pow__(self, power, modulo=None)`**: default `modulo=None` for standard exponentiation; supply an integer for efficient modular exponentiation.
- **UTF-8 byte cost**: 1 byte for ASCII-range characters, up to 4 bytes for the full Unicode range — the single practical default encoding for mixed/unknown-language content.
- **Struct format sizes**: `B`/`b` = 1 byte (0-255 / -128-127), `H`/`h` = 2 bytes, `I`/`i` = 4 bytes, `Q`/`q` = 8 bytes; uppercase = unsigned, lowercase = signed.

## Tells & Smells

- **"Simulated Worked Example based on description" or similar hedge language in generated content** → a sure sign the source wasn't actually read; treat as fabricated and re-derive from the real text.
- **A function signature with vague names** (`def action(var1, var2)`) → the cheapest documentation win (accurate naming) is being skipped; fix before adding comments/docstrings.
- **`except:` (bare, no exception type)** → catches `SystemExit`/`KeyboardInterrupt` too, which usually should propagate; always name specific exception types.
- **A decorator's wrapper missing `functools.wraps`** → the decorated function silently loses its `__name__`/`__doc__`, which breaks introspection and documentation tooling downstream.
- **A `cachedproperty`-style decorator keying its cache dict on the instance from within its own closure** → memory leak; the closure's dict outlives individual instances for the life of the class.
- **A multiple-inheritance base-class order that contradicts an already-established order from one base's own parents** (e.g. `class C(A, B)` when `B` already extends `A`) → Python's C3 algorithm will reject this with `TypeError: Cannot create a consistent method resolution order`; don't fight it, fix the declared order.
- **A doctest with unmasked non-deterministic output** (raw tracebacks with file paths, memory addresses) → will spuriously fail across environments; wrap the variable parts in `...` ellipsis.
- **Reading raw `__doc__` when normalized text is wanted** → use `inspect.getdoc()` instead, which strips source-indentation artifacts that raw `__doc__` preserves verbatim.

## Modern Python (3.10–3.13+) Decision Rules

**When to use `__init_subclass__` vs a full `type` Metaclass**
→ Use `__init_subclass__` for plugin registration, hook execution, and simple subclass configuration (PEP 487). Use a Metaclass only when you must customize class creation itself, intercept `__prepare__` for namespace control, or dynamically construct class types at runtime.

**When to use `typing.Protocol` vs manual dunder duck typing**
→ Use `typing.Protocol` with `@runtime_checkable` (PEP 544). It gives you both static type safety in IDEs/Mypy and runtime `isinstance()` validation without requiring base class inheritance.

**When caching computed properties**
→ Use the standard library `@functools.cached_property` (Python 3.8+). It is thread-locked and stores results directly in the instance `__dict__`, eliminating closure-based memory leaks.

**When typing decorator wrappers**
→ Use `typing.ParamSpec` and `typing.Concatenate` (PEP 612) alongside `@functools.wraps` to prevent wrappers from stripping argument names and type signatures in IDE autocomplete.

**When building modern declarative data classes**
→ Use `@dataclass(slots=True)` (Python 3.10+). It produces fast, low-memory, attribute-locked models out-of-the-box.
