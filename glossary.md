**2to3** — automated (but not fully automatic) tool for converting Python 2.x source to 3.0 syntax; some changes require programmer hints (Ch 1, 7).

**`__all__`** — module-level list restricting what names `from module import *` actually imports (Ch 2).

**`__bases__`** — a class's immediate parent classes, as a tuple, one level up only (Ch 4).

**`__call__()` on a metaclass** — intercepts instantiation itself (the class being called as a function); distinct from `__new__`/`__init__`, which run during that call (Ch 11).

**`__del__()`** — hook for custom cleanup before object destruction; unreliable in reference cycles since Python can't determine safe deletion order among cyclically-referencing objects with custom destructors (Ch 6).

**`__dict__`** — the per-instance namespace dictionary backing ordinary attribute access; readable, mutable, and replaceable at runtime (Ch 6).

**`__getitem__`-based iteration fallback** — lets a class be iterable via indexed access alone (no `__iter__`), used only when `__iter__` is absent; must raise `IndexError` to terminate (Ch 5).

**`__mro__`** — tuple giving a class's full, definitive method-lookup order (new-style classes only; use `inspect.getmro()` for old-style) (Ch 4).

**`__prepare__()`** — optional classmethod on a metaclass returning the namespace dict used while executing a class body, e.g. an `OrderedDict()` to preserve attribute declaration order (Ch 4, 11).

**`__subclasses__()`** — a class's immediate child classes, as a list, one level down only (Ch 4).

**AGPL (Affero GPL)** — GPL variant that also triggers source-disclosure via network interaction, not just distribution — closes the "SaaS loophole" (Ch 10).

**Annotations (function)** — arbitrary expressions attached to arguments/return values (`def f(x: int) -> str`); carry no built-in runtime behavior, purely metadata for third-party tooling (Ch 3).

**Borg pattern** — many instances sharing one namespace dictionary (shared state, distinct identities); implemented by replacing `self.__dict__` in `__new__` (preferred over `__init__` for mixin robustness) (Ch 6).

**BSD License (and variants)** — minimal-restriction open-source license family; original includes an advertising clause, New BSD drops it, Simplified BSD also drops non-endorsement (Ch 10).

**Bytes (`bytes` / `b'...'`)** — raw, meaning-agnostic byte sequences; distinct from `str` (Unicode text) in Python 3 (Ch 7).

**C3 linearization** — the algorithm Python uses to compute Method Resolution Order (MRO) from a multi-parent inheritance graph, guaranteeing consistent ordering or raising `TypeError` if inconsistent (Ch 4).

**Cached property (self-caching)** — a `@property` that stores its computed value directly into `self.__dict__` on first access, so subsequent reads bypass recomputation; do not cache values dependent on other mutable attributes (Ch 6).

**Cachedproperty memory leak variant** — an anti-pattern where a caching decorator keys a values-dict on the *instance* from within the decorator's own closure, permanently referencing every instance ever accessed — leaks memory for the life of the class (Ch 6).

**Closure** — a function object retaining access to its enclosing scope's variables after that scope has returned; requires the inner function be genuinely *defined inside* the outer one (Ch 3).

**Comparison protocol** — `==`/`!=`/`<`/`>`/`<=`/`>=` map to `__eq__`/`__ne__`/`__lt__`/`__gt__`/`__lte__`/`__gte__`; `__ne__` is NOT auto-derived from `__eq__` (Ch 5).

**Context manager** — object implementing `__enter__`/`__exit__`, usable in a `with` block for guaranteed setup/teardown (Ch 2).

**CounterMeta** — a metaclass overriding `__call__()` to track instantiation order on any class using it, fully isolated from user-overridable `__init__`/`__new__` (Ch 11).

**Decorator** — a function accepting a function and returning a function (usually a wrapper), applied via `@name` syntax (Ch 3).

**Declarative framework** — a framework where class declarations configure behavior rather than imperative setup calls; appropriate only with many known-in-advance configurations, many instances each, and meaningful instance actions (Ch 11).

**defaultdict** — dict subclass auto-creating a default value via a supplied callable for missing keys (Ch 2).

**Descriptor** — an object defining `__get__`/`__set__`/`__delete__` to control attribute access on another object; used for validation/type coercion in frameworks (Ch 11, referenced Ch 4/6).

**Dialect (options container pattern)** — a dedicated class (rather than a bare dict) for class-wide framework options, enabling validation and forwarding unknown options via `**kwargs` (Ch 11).

**Docstring** — a string literal as the first statement in a module/function/class, stored on `__doc__`, introspectable at runtime unlike comments (Ch 3, 8).

**Doctest** — tests written as literal interactive-interpreter transcripts inside docstrings, verified via `doctest.testmod()` (Ch 9).

**Dunder method** — Python's "double underscore" special methods (`__add__`, `__len__`, etc.) backing operators and built-in syntax (Ch 5).

**Encoding (text)** — a mapping from Unicode text to a specific byte representation (e.g. UTF-8, ASCII); must be tracked explicitly, never guessed (Ch 7).

**Endianness** — byte order of a multi-byte value; big-endian stores the most significant byte first, little-endian the least significant (Ch 7).

**Exception chaining** — preserving an original exception when a new one is raised during handling, via implicit `__context__` or explicit `raise ... from e` (Ch 2).

**Fallback import** — wrapping an `import` in `try`/`except ImportError` to support a moved/renamed module or optional third-party dependency (Ch 2).

**Generator** — a lazily-evaluated, single-use iterable; exhausted after one full pass, does not restart (Ch 2, 5).

**GPL (GNU General Public License)** — copyleft license requiring derivative works stay GPL and disclose source when distributed (Ch 10).

**Iterable / Iterator protocol** — `iter(obj)` looks for `__iter__()`, falling back to `__getitem__()`; an iterator must implement `__next__()` (raising `StopIteration` when exhausted) and its own `__iter__()` (Ch 5).

**LGPL (GNU Lesser GPL)** — GPL variant removing the static-linking trigger, letting a library be used by proprietary host applications (Ch 10).

**Lambda** — an anonymous, single-expression function (`lambda x: x.price`); no control-flow statements allowed in its body (Ch 3).

**Memoization** — caching a deterministic function's return value keyed by its positional argument tuple (Ch 3).

**Metaclass** — a class whose instances are classes (a `type` subclass); overriding `__init__`/`__new__`/`__call__` customizes every class created with it (Ch 4, 11).

**MRO (Method Resolution Order)** — the definitive, linearized class-lookup order for a given class, computed via C3 (Ch 4).

**Named tuple** — a tuple subclass (via `collections.namedtuple`) with named field access alongside index access (Ch 2).

**OrderedDict** — dict subclass preserving insertion order (Ch 2, relevant pre-3.7).

**Partial application** (`functools.partial`) — preloads some arguments of a function now, returning a callable that fills in the rest later; always attempts execution when called, unlike true currying (Ch 3).

**PEP (Python Enhancement Proposal)** — formal mechanism for documenting Python changes/conventions; PEP 8 = style guide, PEP 20 = Zen of Python, PEP 257 = docstring conventions (Ch 1, 8).

**Plugin mount point** — a base class documenting a subclass contract, with a metaclass auto-registering all subclasses into a `plugins` list (Ch 4).

**Property** (`@property`) — exposes a method as attribute-style access; pair with `@name.setter` for write support (Ch 4).

**PyPI (Python Package Index)** — centralized, standardized package registry; `python setup.py register`/`upload` publish a package (Ch 10).

**Reference counting** — Python's primary memory-management mechanism; every reference increments a count, every removal decrements it, zero makes an object collectible (Ch 6).

**Reference cycle** — a set of objects referencing only each other, invisible to reference counting alone, requiring the cyclic garbage collector (Ch 6).

**reStructuredText (RST/ReST)** — a WYSIWYM markup language for technical documentation, provided by `docutils` (Ch 8).

**`sdist`** — `distutils` command building a source distribution archive from `setup.py`/`MANIFEST.in` (Ch 10).

**setup.py / `distutils.core.setup()`** — declarative package metadata function; required args `name`/`version`/`url` (Ch 10).

**Sphinx** — documentation tool managing a linked collection of reStructuredText documents as a whole (Ch 8).

**`struct` module** — format-string-driven conversion between Python values and byte sequences, supporting multi-byte integers, floats, fixed-width strings, explicit endianness (Ch 7).

**`super()`** — returns a proxy bound to the *instance's* MRO, starting lookup just after the class passed as its first argument; enables cooperative multiple inheritance (Ch 4).

**TestCase (unittest)** — base class for defining test suites; `setUp()` runs before every test method; assertion methods (`assertEqual`, etc.) report diagnostic detail on failure (Ch 9).

**type()** — the built-in metaclass; `type(name, bases, namespace)` is what a `class` statement compiles down to (Ch 4).

**Unicode** — a standard covering the vast majority of world languages' characters via multi-byte "code points"; Python 3's default `str` type (Ch 7).

**UTF-8** — variable-length Unicode encoding (1-4 bytes/char), backward-compatible with ASCII, space-efficient for mostly-ASCII text (Ch 7).

**Variable positional/keyword arguments (`*args`/`**kwargs`)** — collect extra positional arguments into a tuple / extra keyword arguments into a dict (Ch 3).

**Wrapper** — the inner function returned by a decorator, typically accepting `*args, **kwargs` to stand in for any wrapped function's signature (Ch 3).

**Zen of Python** — the 19 aphorisms (PEP 20, `import this`) condensing Python's design philosophy (Ch 1).
