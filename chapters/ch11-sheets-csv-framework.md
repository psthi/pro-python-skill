# Chapter 11: Sheets: A CSV Framework

## Core Idea
This capstone chapter builds a real declarative CSV-handling framework ("sheets") from scratch, synthesizing nearly every advanced technique from the book — metaclasses, `__prepare__()`, duck typing, `__new__()`/`__call__()` object-lifecycle hooks — to demonstrate the concrete decisions and trade-offs involved in framework design, not just the individual techniques in isolation.

## Frameworks Introduced
- **Declarative framework decision criteria**: before building one, verify you actually have (1) many potential configurations, (2) each known in advance, (3) many instances per configuration, and (4) meaningful actions performable on instances. If your data format is singular or determined only at runtime, a declarative class-based approach adds complexity without benefit — just write a direct solution.
- **The three components of a declarative framework**: a base class (with an attached metaclass that hooks into class creation), field/column types (individual declared attributes, each needing to know its own instantiation order), and an options container (class-wide settings that don't belong on every individual field, avoiding DRY violations).
- **Options/Dialect container pattern**: rather than a plain dict, a dedicated class (here `Dialect`) can validate option values/combinations and provide descriptive error messages — impossible with a bare dictionary. Unknown options passed as `**kwargs` are captured generically and can be forwarded transparently to underlying library code (here, Python's own `csv` module) so the framework doesn't need to track that library's option set as it evolves.
- **Field/Column base class with `attach_to_class(cls, name, dialect)`**: the hook that connects a declared attribute to its owning class, giving it the attribute name it was assigned (which Python doesn't otherwise expose to the object itself), the class it lives on, and shared dialect/options context.
- **Metaclass-driven field registration (`RowMeta.__init__`)**: iterates the class's declared attributes, and for any attribute exposing an `attach_to_class` method (duck typing — no `isinstance` check required), calls it to complete the field's setup and register it into the `Dialect`'s column list.
- **Field ordering, three implementation strategies** (in order of the book's own recommendation, from most to least modern-Python-idiomatic):
  1. **`__prepare__()` returning an `OrderedDict`** (Python 3.0+ only) — the namespace itself preserves declaration order, no extra bookkeeping needed.
  2. **A `counter` attribute set in `Column.__init__()`** — works on older Python, but silently breaks if a subclass overrides `__init__()` without calling `super()`.
  3. **A `counter` attribute set in `Column.__new__()`** — reduces (but doesn't eliminate) the same subclass-override risk, since `__new__()` overrides are rarer than `__init__()` overrides.
  4. **A separate `CounterMeta` metaclass overriding `__call__()`** — fully isolates the counting logic from `Column` itself, reusable by any class needing instantiation-order tracking, immune to subclasses forgetting `super()` in their own `__init__`/`__new__`.

## Key Concepts
- **`RowMeta`**: the framework's metaclass (subclasses `type`), pulling an inner `Dialect` class (if present) out of the class namespace, building a `Dialect` instance from it, and driving field registration.
- **Inner `Dialect` class as a private declaration namespace**: nesting an inner class named `Dialect` inside a `Row` subclass avoids polluting the main class namespace with option names that could collide with legitimate field names (e.g. a column literally named `encoding`).
- **`hasattr(attr, 'attach_to_class')`**: the duck-typing check the metaclass uses instead of `isinstance(attr, Column)` — deliberately open-ended so any object (not just `Column` subclasses) implementing the same protocol can participate as a field.
- **`__call__()` on a metaclass**: intercepts *instantiation itself* (calling the class as if it were a function) — distinct from `__new__()`/`__init__()`, which run *during* that call but are defined on the class being instantiated, not on the metaclass.
- **Explicit `None`-check for optional string arguments** (`if self.title is None:` rather than `if not self.title:`): preserves the ability to pass an empty string as a meaningfully different value from "not provided" — a deliberate deviation from the more common Python idiom of testing truthiness.

## Mental Models
- **A declarative framework's job is "translate advanced techniques into a simple class declaration"**: the framework absorbs metaclass/descriptor complexity internally so the end user just writes `class EmployeeSheet(sheets.Row): first_name = sheets.StringColumn()` — the API surface should look almost boring even though powerful machinery sits behind it.
- **Field ordering is a "count at instantiation time" problem, not a "sort by name" problem**: since field names carry no inherent order, the framework must capture instantiation sequence explicitly (via `__prepare__`'s ordered namespace, or an incrementing counter) — the choice of *where* to increment that counter is really about minimizing collision risk with user-overridden lifecycle methods.
- **Duck typing in a metaclass is a deliberate flexibility choice**: checking for a protocol method (`attach_to_class`) rather than a specific base class (`Column`) is exactly the kind of design decision Ch. 5's protocol philosophy anticipates — it leaves room for other objects (custom descriptors, even certain methods) to participate in the same declarative mechanism.

## Anti-patterns
- **Building a declarative framework for a single, fixed data format**: if there's only ever one configuration and it won't change, the metaclass/field machinery is pure overhead — "just write a solution for your type of data and use it."
- **Storing class-wide options as ordinary class attributes alongside fields**: risks name collisions (e.g. an `encoding` option vs. a legitimately named `encoding` column) and makes it harder to validate options as a distinct, coherent group — use a nested namespace (inner class) instead.
- **Assuming `Column.__init__()` is "safe" to override without calling `super()`**: many programmers expect `__init__()` overrides to be inert with respect to unrelated framework bookkeeping, but if ordering logic lives there, skipping `super()` silently breaks field ordering with no visible error — this exact fragility is why the chapter progressively migrates the counter logic to `__new__()` and finally to a dedicated metaclass, each step reducing (not eliminating) how easily a user can break it by accident.
- **Resetting the ordering counter per-class "for cleanliness"**: the book explicitly rejects this — a single global counter shared across all `Column` instantiations is simpler, doesn't need special-casing "when did we switch to a new class," and works fine because sorting only cares about relative order within each class's own field list, not absolute counter values.
- **Sorting the field list incrementally on every `add_column()` call** (e.g. via `bisect.insort()`): technically possible but requires implementing `__lt__()` on `Column` and adds an import/method purely to support an ordering guarantee that isn't actually useful until *all* columns are registered anyway — sorting once after the fact is simpler and just as effective ("Simple is better than complex").

## Code Examples
```python
class RowMeta(type):
    def __init__(cls, name, bases, attrs):
        if 'Dialect' in attrs:
            items = attrs.pop('Dialect').__dict__.items()
            items = {k: v for k, v in items if not k.startswith('__')}
        else:
            items = {}
        cls._dialect = options.Dialect(**items)

        for key, attr in attrs.items():
            if hasattr(attr, 'attach_to_class'):
                attr.attach_to_class(cls, key, cls._dialect)

        cls._dialect.columns.sort(key=lambda column: column.counter)
```
- **What it demonstrates**: the complete metaclass driving the framework — extracting a nested `Dialect` declaration, building the options object, duck-typed field registration via `attach_to_class`, and final ordering by instantiation counter.

```python
class CounterMeta(type):
    """A simple metaclass that keeps track of the order that each instance
    of a given class was instantiated."""
    counter = 0
    def __call__(cls, *args, **kwargs):
        obj = super(CounterMeta, cls).__call__(*args, **kwargs)
        obj.counter = CounterMeta.counter
        CounterMeta.counter += 1
        return obj

class Column(metaclass=CounterMeta):
    def __init__(self, title=None, required=True):
        self.title = title
        self.required = required
```
- **What it demonstrates**: the most robust ordering-tracking approach — isolating the counter entirely in a reusable metaclass via `__call__()`, so `Column` (and any other class needing the same tracking) can't accidentally break ordering by overriding its own `__init__`/`__new__` without `super()`.

```python
class EmployeeSheet(sheets.Row):
    first_name = sheets.StringColumn()
    last_name = sheets.StringColumn()
    hire_date = sheets.DateColumn()
    salary = sheets.CurrencyColumn(decimal_places=2)
```
- **What it demonstrates**: the end-user-facing API the entire framework exists to enable — a plain, declarative class definition with zero visible metaclass/descriptor complexity.

## Reference Tables
| Ordering strategy | Where implemented | Robustness to missing `super()` |
|---|---|---|
| `__prepare__()` + `OrderedDict` | metaclass | N/A — no counter needed (Py 3.0+ only) |
| Counter in `Column.__init__()` | field base class | Fragile — broken by subclass omitting `super().__init__()` |
| Counter in `Column.__new__()` | field base class | Better — `__new__` overrides are rarer |
| Counter via `CounterMeta.__call__()` | separate metaclass | Most robust — isolated from user-overridable methods entirely |

## Worked Example
The chapter's full build sequence, in order:
1. **Options/Dialect**: start with a simple `Options` class holding `has_header_row` (default `False`); rename to `Dialect` and add `**kwargs` passthrough so any of Python's own `csv` module's dialect options (present or future) are supported without the framework needing to enumerate them.
2. **Column base class**: `__init__(self, title=None, required=True)` — `title` deferred (filled in later from the attribute name if not given), `required` defaults `True`.
3. **`attach_to_class(cls, name, dialect)`**: fills in the missing pieces a field object can't know about itself — its class, its attribute name, and shared dialect context; also resolves the deferred title (`name.replace('_', ' ')`) using an explicit `is None` check so an intentionally empty title string is preserved.
4. **`RowMeta` metaclass**: extracts a nested `Dialect` class declaration (if present) from the new class's namespace, builds the real `Dialect` object, then iterates all class attributes calling `attach_to_class()` on anything duck-typed as a field.
5. **`Row` base class**: `class Row(metaclass=RowMeta): pass` — the actual public base class end-users subclass.
6. **Public API consolidation**: `sheets/__init__.py` does `from sheets.base import *` (and similarly for `options`, `columns`) so users only ever need `import sheets`.
7. **Field ordering problem**: fields are stored in declaration order via one of the three (four, counting `__prepare__`) strategies above — the chapter walks through each, explaining exactly why it progressively migrates from `__init__()` to `__new__()` to a dedicated `CounterMeta`, driven entirely by robustness against a subclass author forgetting to call `super()`.

## Key Takeaways
1. Only build a declarative framework when you genuinely have many configurations, known in advance, with many instances each, and meaningful per-instance behavior — otherwise it's needless complexity.
2. Separate concerns into three components: a metaclass-backed base class, field/column types, and an options container — each solving a distinct part of the declaration-processing problem.
3. Use a nested inner class (like `Dialect`) to give class-wide options their own namespace, avoiding collisions with legitimately-named fields.
4. Use duck typing (`hasattr(attr, 'attach_to_class')`) rather than `isinstance` checks in a metaclass to keep the framework open to any object implementing the right protocol.
5. Field/instantiation ordering is a real problem needing an explicit solution — prefer `__prepare__()` with an `OrderedDict` on modern Python; fall back to a counter, and prefer placing that counter's logic in a dedicated metaclass (`__call__()`) over `__init__()`/`__new__()` to make it robust against subclasses that forget `super()`.
6. Favor simplicity over incremental cleverness: sort the field list once after full registration rather than trying to maintain sorted order incrementally with `bisect.insort()` — the added complexity buys nothing of real use here.
7. A good declarative framework's end-user-facing API should look almost trivially simple — all the metaclass/descriptor complexity is the framework's problem to hide, not the user's problem to understand.

## Connects To
- **Ch 1 (Principles and Philosophy)**: DRY motivates the options-container design (avoid repeating settings on every field); "Simple is better than complex" is invoked explicitly, twice, to justify not over-engineering the counter-reset and incremental-sort alternatives.
- **Ch 4 (Classes)**: metaclasses, `__prepare__()`, and `type` subclassing — introduced there conceptually — are applied here in a full real framework; the plugin-mount-point pattern from Ch. 4 is the direct ancestor of this chapter's field-registration mechanism.
- **Ch 5 (Common Protocols)**: duck typing (checking for a method rather than a specific type) and the general philosophy of protocol-based design underlie the `hasattr(attr, 'attach_to_class')` check.
- **Ch 6 (Object Management)**: `__new__()` vs. `__init__()` distinction, and object lifecycle hooks generally, are exercised directly in the field-ordering-counter discussion.
- **Ch 10 (Distribution)**: this framework, once complete, is exactly the kind of package that chapter's packaging/distribution guidance (setup.py, PyPI) would apply to.
