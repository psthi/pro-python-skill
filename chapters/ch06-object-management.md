# Chapter 6: Object Management

## Core Idea
Every Python object is composed of three components — identity (memory address, immutable), type (shared class behavior), and value (an instance-specific namespace dictionary) — and understanding how that namespace dictionary works, plus how Python's reference-counting garbage collector identifies and reclaims unreachable objects, is essential for building patterns like shared-state classes and cached properties without introducing memory leaks.

## Frameworks Introduced
- **Object identity/type/value model**: identity = unique memory address, retrievable via `id()`, never changes and can't be overridden; type = shared behavior from the class; value = the object's own `__dict__` namespace dictionary, holding its individual attribute values.
- **The Borg pattern**: many instances sharing a single namespace dictionary (so all instances reflect the same state) while retaining distinct identities. Implemented by replacing `self.__dict__` (in `__init__` or `__new__`) with a dictionary owned by the class rather than the instance.
  - When to use: applications where a class may be instantiated many times but all instances should observe and mutate the same shared state (an alternative to the Singleton pattern that still permits multiple identities).
  - How (robust version): in `__new__`, use `cls._namespace.setdefault(cls, {})` so each *subclass* using the mixin gets its own private shared namespace rather than all Borg-derived classes colliding into one.
- **Self-caching properties**: a `@property` that computes an expensive value once and stores it directly in `self.__dict__` under the same name as the property, so future *attribute* lookups bypass the descriptor and property function entirely (since instance `__dict__` lookups take priority... practically achieved here by writing directly into `__dict__` from within the property getter).
  - When to use: expensive-to-compute or expensive-to-fetch attributes (e.g. ORM relationship lookups hitting a database) that are read more than once but shouldn't be computed eagerly at object construction.
  - Pitfall: don't cache a value that should change when *other* attributes change (e.g. a computed full name depending on first/last name) — caching would freeze it stale.
- **Reference counting**: Python's primary memory-management mechanism — every reference to an object (variable assignment, container membership, closure capture) increments its count; every removal (`del`, reassignment, container removal) decrements it; an object with a reference count of zero is immediately eligible for collection.
- **Cyclic garbage collection**: a secondary mechanism that detects groups of objects referencing only each other (unreachable from any live code) and reclaims them even though their mutual reference counts never hit zero — necessary because plain reference counting alone can't detect cycles.

## Key Concepts
- **`__dict__`**: the per-instance namespace dictionary backing ordinary attribute access; can be read, mutated, or wholesale replaced at runtime.
- **`id()`**: returns an object's identity (its memory address in standard CPython); two objects can never share an identity while both are alive, but a destroyed object's identity may be reused by a later object.
- **`__new__()` vs `__init__()`**: both run during instantiation; `__new__` actually constructs the object (and is the safer place for mixins like Borg to intervene, since it's less commonly overridden and thus less prone to ordering collisions with other classes' `__init__`).
- **Reference cycle**: a set of objects referencing only each other, with no path back to any live/root reference — invisible to plain reference counting, requires the cyclic collector to detect and reclaim.
- **`__del__()`**: a hook for custom cleanup when an object is about to be destroyed; becomes genuinely problematic in reference cycles because Python cannot determine a safe order to call `__del__()` across mutually-referencing objects, and (per this book, describing pre-3.4 behavior) may simply leave such objects in memory rather than guess.
- **Memory leak (descriptor-cache variant)**: storing per-instance cached values keyed by the *instance itself* in a dict living on the descriptor/class (rather than in the instance's own `__dict__`) keeps every instance alive forever, since the descriptor's dict holds a permanent reference to each instance it has ever cached a value for.

## Mental Models
- **Identity, type, value = "address, blueprint, and contents"**: identity never changes and isn't behavior-related; type is shared and defines what an object *can* do; value is what makes one instance different from its siblings.
- **Reference counting as a strict ledger**: every reference is a line item; the object survives exactly as long as the ledger balance is above zero. Cycles are the ledger's blind spot — two objects can keep each other's balance above zero indefinitely with no outside line items at all.
- **The Borg pattern is "shared value, distinct identity"**: unlike a true Singleton (one identity, enforced), Borg lets you create as many instances as you want, but every one of them reads and writes through the *same* underlying dictionary — so behavior converges even though `is` comparisons between instances still return `False`.
- **A self-caching property is "lazy, then permanent"**: the first read pays the cost (database hit, computation); every subsequent read is a plain dictionary lookup once the value lives in `__dict__`.

## Anti-patterns
- **Implementing Borg via `__init__` without disciplined `super()` use**: when combined as a mixin with unrelated base classes, base-class ordering (`class Testing(Borg, Base)` vs `class Testing(Base, Borg)`) can silently exclude one class's initialization entirely — using `__new__` instead reduces (but doesn't eliminate) this risk since `__new__` overrides are rarer.
- **A single shared `_namespace` dict on the Borg class itself**: causes *every* subclass using the mixin to share one global namespace, defeating the purpose if you wanted per-subclass shared state — fix by keying a dict-of-dicts on the class object (`cls._namespace.setdefault(cls, {})`).
- **Caching descriptor values in a dict keyed by instance, living on the descriptor itself** (rather than the instance's own `__dict__`): creates a silent memory leak — the descriptor (which typically lives for the life of the class) holds a permanent reference to every instance that ever accessed the cached property, preventing any of them from ever being garbage collected.
- **Caching a computed property whose correctness depends on other mutable attributes**: freezes a stale value in place the moment any of its dependencies change.
- **Relying on `__del__()` for critical cleanup when the object might participate in a reference cycle**: cleanup order across cyclically-referencing objects with `__del__()` is undefined; Python may simply choose to leave such objects in memory rather than guess an unsafe order.

## Code Examples
```python
class Borg:
    _namespace = {}
    def __new__(cls, *args, **kwargs):
        obj = super(Borg, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._namespace.setdefault(cls, {})
        return obj
```
- **What it demonstrates**: the robust Borg implementation — using `__new__` (safer as a mixin than `__init__`) and keying `_namespace` per-subclass via `setdefault(cls, {})`, so `TestOne` and `TestTwo` instances get independent shared namespaces instead of colliding into one.

```python
def cachedproperty(name):
    def decorator(func):
        @property
        @functools.wraps(func)
        def wrapper(self):
            if name not in self.__dict__:
                self.__dict__[name] = func(self)
            return self.__dict__[name]
        return wrapper
    return decorator
```
- **What it demonstrates**: a decorator that turns any method into a self-caching property — first access computes and stores the value directly in the instance's own `__dict__`; subsequent accesses find it there and skip recomputation. Requires the attribute name to be passed explicitly (`@cachedproperty('attr')`) because descriptors don't automatically know the name they're assigned to.

```python
>>> a = [1, 2, 3]
>>> b = {'example': a}
>>> b['example'].append(b)   # creates a cycle: b -> a -> b
```
- **What it demonstrates**: constructing a genuine reference cycle by hand — after `del b`, the dict and list still reference each other and would never reach a reference count of zero without the cyclic collector.

## Worked Example
The book iterates through three versions of a caching-property decorator to expose a subtle memory-leak trap:
1. **Named-attribute version** (`cachedproperty(name)`): stores the cached value in `self.__dict__[name]` — correct, but requires passing the attribute's name twice (once as the decorator argument, once as the method name), violating DRY.
2. **Instance-keyed dict version** (`cachedproperty(func)` with `values = {}` closed over inside the decorator): avoids repeating the name by keying a dict on the object instance itself (`values[self]`). This looks clean and avoids name duplication, but the `values` dict lives inside the decorator's closure for the *lifetime of the class* — so every instance that ever accessed the cached property remains referenced by `values` forever, even after all other references to it are gone. This is a genuine memory leak.
3. **Resolution**: go back to the explicit-name version, or (for frameworks that already use a metaclass for other reasons, as in Ch. 11) use the metaclass to inject the attribute name automatically so it doesn't need to be typed twice.

## Key Takeaways
1. Every object is identity + type + value; only value (`__dict__`) is instance-specific and mutable at runtime.
2. The Borg pattern shares a namespace dict across instances for shared-state behavior while preserving distinct object identities — prefer implementing it via `__new__` over `__init__` to reduce mixin-ordering conflicts, and key the shared dict per-subclass to avoid unintended cross-class sharing.
3. Self-caching properties trade a name-repetition DRY violation for correctness — don't "fix" the repetition by keying a cache dict on the instance from within a descriptor/decorator closure, since that leaks instances for the life of the class.
4. Reference counting handles ordinary object lifecycle correctly and immediately; cyclic garbage collection exists specifically to catch mutually-referencing object groups that reference counting alone can never zero out.
5. `__del__()` becomes unreliable in reference cycles because Python cannot safely determine cleanup order among cyclically-referencing objects with custom destructors.
6. Never cache a computed value that depends on other mutable attributes unless you also invalidate the cache when those dependencies change.

## Connects To
- **Ch 3 (Functions)**: `functools.wraps` (used in `cachedproperty`) and decorator-with-arguments patterns are direct applications of Ch. 3's decorator techniques.
- **Ch 4 (Classes)**: `__new__()` vs `__init__()` (introduced but deferred there) is resolved here; `super()`/MRO discipline required for the Borg pattern as a mixin builds directly on Ch. 4's multiple-inheritance material.
- **Ch 5 (Common Protocols)**: iterator garbage collection (what happens to an abandoned, not-fully-consumed iterator) referenced there is explained by this chapter's reference-counting mechanics.
- **Ch 11 (Sheets: A CSV Framework)**: the metaclass-based alternative to explicit-name caching properties (avoiding the "pass the name twice" DRY violation) is realized fully in that chapter's descriptor/metaclass framework.
