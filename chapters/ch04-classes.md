# Chapter 4: Classes

## Core Idea
Python classes are themselves created at runtime by `type` (the base metaclass), which makes class creation, inheritance resolution (MRO/`super()`), and even class *behavior itself* programmable — via custom metaclasses — rather than fixed language syntax.

## Frameworks Introduced
- **Vertical inheritance (specialization)**: build a hierarchy where each subclass is a more specific example of its parent (e.g. `Contact` → `Person` → `Employee`). Use when relationships are genuinely "is-a-more-specific-version-of."
- **Horizontal inheritance / Mixins**: multiple inheritance used to bolt on small, independent behaviors (e.g. a `NoneAttributes` mixin overriding `__getattr__`) rather than building a full class hierarchy from many small components.
- **C3 linearization (Method Resolution Order / MRO)**: the algorithm Python uses to flatten a multi-parent inheritance graph into one consistent, ordered list determining attribute/method lookup order. Guarantees: a class always precedes its parents; base-class relative ordering is preserved across subclasses; an inconsistent ordering request (e.g. `class C(A, B)` when `B` already extends `A`) raises `TypeError: Cannot create a consistent method resolution order`.
- **`super()`**: returns a proxy object bound to the *instance's* MRO (not necessarily the calling class's own MRO), starting the lookup just after the class passed as `super()`'s first argument. This is what makes cooperative multiple inheritance work correctly — `super(B, self).test()` inside `class D(B, C)` resolves to `C.test()`, not `A.test()`, because D's actual MRO is `[D, B, C, A, object]`.
- **Dynamic class creation via `type(name, bases, namespace)`**: classes are ordinary objects produced by calling `type` (or a `type` subclass) with three pieces of information — name, base classes tuple, and namespace dict. `class Foo(Base): x = 1` is sugar for `Foo = type('Foo', (Base,), {'x': 1})`.
- **Metaclasses**: a class whose instances are classes (a subclass of `type`) — override `__init__` (or `__new__`) to intercept and customize every class created with that metaclass. Declared via `class Foo(metaclass=MyMeta):`.
  - When to use: frameworks that need to inspect/transform a class's declared attributes at creation time (plugin registration, field/ORM-style frameworks — see Ch. 11).
- **`__prepare__()`**: an optional classmethod on a metaclass that returns the namespace dict used while executing the class body — e.g. returning an `OrderedDict()` to preserve declaration order of class attributes (relevant pre-3.7, before dicts guaranteed insertion order).
- **Properties (`@property` / `.setter`)**: expose a method as if it were a plain attribute; `@property` defines the getter, `@name.setter` defines the setter for the same logical attribute.

## Key Concepts
- **New-style vs. old-style classes**: pre-Python-3 distinction (all classes are new-style in Python 3, inheriting implicitly from `object`).
- **MRO (`__mro__`)**: the tuple giving the definitive class-lookup order for a given class; `Cls.__mro__` (new-style only; use `inspect.getmro()` for old-style compatibility).
- **`__bases__`**: immediate parent classes only (one level), as a tuple.
- **`__subclasses__()`**: immediate child classes only (one level), as a list.
- **`isinstance(obj, cls)`**: True if `cls` is anywhere in `type(obj)`'s MRO. Equivalent identity: `isinstance(obj, cls) == issubclass(type(obj), cls)`.
- **`issubclass(cls1, cls2)`**: True if `cls2` is anywhere in `cls1`'s MRO (a class is always considered a subclass of itself).
- **`getattr()`/`setattr()`/`delattr()`**: functional (name-as-string) equivalents of attribute dot-syntax — needed when the attribute name is only known at runtime.
- **Plugin mount point pattern**: a base class documents an interface contract (e.g. "subclasses must implement `validate(self, input)`"); a metaclass automatically collects all subclasses into a `plugins` list for later iteration — no manual registration required.

## Mental Models
- **Class body execution is just running code in a fresh namespace**: `if`/`try` blocks, imports, and function calls all work normally inside a `class:` body; whatever names end up in that namespace become class attributes.
- **`super()` follows the instance's MRO, not the defining class's MRO**: this is the single most misunderstood behavior — always think "where does the *actual runtime instance's* MRO put this class, and what's next after it" rather than "what does this class's own parent chain look like in isolation."
- **A metaclass is "a class for classes"**: just as a class's `__init__` customizes instance creation, a metaclass's `__init__`/`__new__` customizes *class* creation — anything you'd do to an instance at construction time, you can do to a class at definition time.
- **MRO ordering is `[self_class, ...parents_in_linearized_order..., object]`**: always starts with the class itself, always ends with `object`.

## Anti-patterns
- **Misusing multiple inheritance to model relationships that aren't really "is-a"**: e.g. making `FamilyMember` inherit from `Friend` just because both have a `relationship` field — introspection code that trusts the inheritance hierarchy will then draw wrong conclusions.
- **Requesting an inconsistent base-class order** (e.g. `class C(A, B)` where `B` already subclasses `A`): Python's C3 algorithm will raise `TypeError` rather than silently pick an order that violates base-class-ordering consistency.
- **Calling `super()` with a different class than the one it's used in** (e.g. `super(C, self)` inside `B`'s method): technically legal but dangerous — creates surprising MRO-skipping behavior and raises `TypeError` if `self` isn't actually a subtype of the class passed in.
- **Assuming `super()`-called methods always share the same signature across the MRO**: a method overridden differently in different mixins/parents can silently break if `super()` is called with mismatched arguments — protocols (Ch. 5) are the safe convention precisely because their signatures are standardized.
- **Overusing `type()`-created classes with dynamic module/name spoofing**: setting a fake `__module__` on a dynamically created class can fool introspection tools and create name collisions that are hard to trace.
- **Metaclass/namespace magic that's too clever**: overriding `__prepare__` or namespace behavior can make class bodies behave in surprising, "wildly inconsistent"-looking ways to users unfamiliar with the metaclass — document heavily or avoid unless the framework genuinely needs it.

## Code Examples
```python
class NoneDictionary(dict):
    def __getitem__(self, name):
        try:
            return super(NoneDictionary, self).__getitem__(name)
        except KeyError:
            return None
```
- **What it demonstrates**: the standard, safe `super()` pattern — call the base implementation, customize behavior around it (here, swallowing `KeyError` to return `None` instead).

```python
class PluginMount(type):
    """Place this metaclass on any standard Python class to turn it into a
    plugin mount point. All subclasses will be automatically registered."""
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []          # This is the mount point itself
        else:
            cls.plugins.append(cls)   # This is an individual plugin

class InputValidator(metaclass=PluginMount):
    """A plugin mount for input validation."""
    def validate(self, input):
        raise NotImplementedError
```
- **What it demonstrates**: a complete, minimal plugin-registration framework in ~6 lines — the metaclass distinguishes "mount point" (no `plugins` attribute yet) from "plugin subclass" (inherits `plugins` from the mount) purely via `hasattr`.

```python
class Person:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
    @property
    def name(self):
        return '%s, %s' % (self.last_name, self.first_name)
```
- **What it demonstrates**: a read-only computed property; assigning to `p.name` raises `AttributeError: can't set attribute` until a `@name.setter` method is added.

## Reference Tables
| Introspection tool | Scope | Returns |
|---|---|---|
| `isinstance(obj, cls)` | instance vs class | bool, True if `cls` in `type(obj)`'s MRO |
| `issubclass(c1, c2)` | class vs class | bool, True if `c2` in `c1`'s MRO (or `c1 is c2`) |
| `cls.__bases__` | one level up | tuple of immediate parents |
| `cls.__subclasses__()` | one level down | list of immediate children |
| `cls.__mro__` | full chain | tuple, full linearized MRO (new-style only; use `inspect.getmro()` otherwise) |

## Worked Example
The book implements the C3 linearization algorithm itself as a `C3(cls, *mro_lists)` function to demystify how Python computes MRO:
1. Copy input MRO lists defensively (so the algorithm doesn't mutate caller data); seed the result with `[cls]`.
2. Loop: for each candidate (`mro_list[0]` of each list), check whether it appears in any *non-first* position across all lists (via `itertools.chain`). If so, it's not yet safe to promote — skip to the next list's candidate.
3. Once a valid candidate is found, append it to the result MRO and remove it from the front of every list it headed.
4. Repeat until all lists are empty (success) or a full pass finds no valid candidate (raise `TypeError("Inconsistent MRO")`, mirroring Python's real behavior for e.g. `class C(A, B)` when `B` already extends `A`).
5. Critically, the base classes themselves (not just their full MROs) must also be passed in as one of the lists — otherwise C3 can't detect ordering violations like `C(A, B)` where the user's explicit order contradicts an implied order from `B`'s own inheritance.

This demystifies `super()`'s behavior: because C3 guarantees consistent, predictable ordering, `super()` can reliably walk "everything after the given class in the *instance's* MRO" regardless of how deep or tangled the multiple-inheritance graph is.

## Key Takeaways
1. Use vertical inheritance for genuine specialization hierarchies; use mixins (horizontal/multiple inheritance) for small, independent, bolt-on behaviors.
2. `super()` resolves against the *instance's* full MRO, not the calling class's own isolated parent chain — this is what makes cooperative multi-inheritance method chains work correctly.
3. All classes are created by calling `type(name, bases, namespace)` (or a subclass of it) — class statements are syntactic sugar for this call.
4. A metaclass (a `type` subclass) lets you intercept and customize every class created with it — the standard use case is frameworks that need to process a class's declared attributes at definition time (plugin registries, field-mapping frameworks).
5. `__prepare__()` lets a metaclass control the very dictionary used to execute a class body, enabling attribute-order preservation or other declaration-time interception.
6. Prefer `@property`/`@x.setter` over ad hoc getter/setter methods when you want attribute-style access with computed behavior.
7. Use `isinstance()`/`issubclass()` for inheritance-aware type checks rather than `type(obj) == cls`, which misses subclasses.
8. An inconsistent multiple-inheritance base-class order (contradicting an implied order from a parent's own bases) is a real error Python detects and rejects — not just a style preference.

## Connects To
- **Ch 1 (Principles and Philosophy)**: DRY is explicitly invoked regarding `type('Example', ...)` naming duplication and its resolution.
- **Ch 3 (Functions)**: `isinstance()`/`type()` introspection basics introduced there are the foundation for this chapter's deeper inheritance introspection.
- **Ch 5 (Common Protocols)**: `__getattr__`/`__getitem__` (used in the mixin and `NoneDictionary` examples) are protocol methods covered fully there; extending namespace dictionaries (via `__prepare__`) connects to custom iterable/descriptor protocols there too.
- **Ch 6 (Object Management)**: `__new__()` vs `__init__()` distinction (mentioned but deferred here) is explained fully in the object lifecycle discussion.
- **Ch 11 (Sheets: A CSV Framework)**: the metaclass-based plugin/registration pattern shown here is the direct conceptual ancestor of the declarative field-registration framework built there.
