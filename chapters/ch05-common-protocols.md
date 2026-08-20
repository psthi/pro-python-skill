# Chapter 5: Common Protocols

## Core Idea
Python's built-in syntax (operators, `for` loops, indexing, `len()`, boolean checks) is powered entirely by dunder methods that any custom class can implement — mimicking these existing, familiar interfaces on your own objects (rather than inventing new APIs) is more Pythonic and immediately usable with the language's existing tools.

## Frameworks Introduced
- **Arithmetic operator protocol**: `+`, `-`, `*`, `/`, `//`, `%`, `**`, `divmod()` map to `__add__`/`__sub__`/`__mul__`/`__truediv__`/`__floordiv__`/`__mod__`/`__pow__`/`__divmod__`. Each has a right-hand variant (`__radd__` etc., used when the left operand doesn't know how to handle the right one — e.g. `10 + Example(20)`) and an in-place variant (`__iadd__` etc., used for `+=` and similar augmented assignment).
- **Bitwise operator protocol**: `<<`/`>>`/`&`/`|`/`^`/`~` map to `__lshift__`/`__rshift__`/`__and__`/`__or__`/`__xor__`/`__invert__` (the last is unary — no right-hand or in-place variant exists for it).
- **Comparison protocol**: `==`/`!=`/`<`/`>`/`<=`/`>=` map to `__eq__`/`__ne__`/`__lt__`/`__gt__`/`__lte__`/`__gte__`. Crucially, `__ne__` is NOT automatically derived from `__eq__` — implement both explicitly. `is`/`is not` test identity directly and cannot be overridden.
- **Number coercion protocol**: `__index__()` (integer coercion for use as a sequence index/slice — raises `TypeError` if absent or non-integer), `__int__()`/`__float__()`/`__complex__()` (explicit type conversion for `int()`/`float()`/`complex()`), `__floor__()`/`__ceil__()`/`__round__()` (for `math.floor()`/`math.ceil()`/`round()`).
- **Sign protocol**: `__neg__` (unary `-`), `__pos__` (unary `+`, a no-op for ordinary numbers), `__abs__` (`abs()`).
- **Iterable / Iterator protocol**: an object is iterable if `iter(obj)` returns an iterator. `iter()` looks for `__iter__()` first; if absent, falls back to `__getitem__()` called with increasing integer indices starting at 0 until `IndexError` is raised. An iterator must implement `__next__()` (raising `StopIteration` when exhausted) and its own `__iter__()` (conventionally `return self`) so the iterator is itself iterable.
  - When to use a full iterator class (vs. a generator): when the sequence must support being iterated multiple times independently (generators exhaust after one pass; a proper `__iter__()`-returning-a-fresh-iterator object can be iterated repeatedly).

## Key Concepts
- **`__truediv__` vs `__floordiv__`**: true division (`/`) can return a non-integer from two integers; floor division (`//`) always rounds down to an integer. (Historically `/` meant floor division pre-3.0 via `__div__`, since removed.)
- **`__divmod__`**: backs the `divmod()` builtin, returning `(floor_division_result, modulo_result)` in one call — can be implemented more efficiently than calling both operations separately.
- **`__pow__(self, power, modulo=None)`**: backs both `**` (2-arg call) and `pow(base, exp, mod)` (3-arg call, used for efficient modular exponentiation, e.g. in cryptography).
- **Right-hand (`__r*__`) methods**: invoked when the left operand's own dunder method returns `NotImplemented` (or doesn't exist) and the right operand is a *different* type than the left — lets a custom type work as the right-hand operand too (e.g. `10 + Example(20)`).
- **In-place (`__i*__`) methods**: back augmented assignment (`+=` etc.); allow modifying a value in place instead of always constructing a new one.
- **`StopIteration`**: the sentinel exception an iterator's `__next__()` raises to signal exhaustion — necessary because `None` is a legitimate value an iterator might otherwise yield.
- **`__getitem__`-based iteration fallback**: lets a class be iterable just by supporting indexed access (`obj[0]`, `obj[1]`, ...) without writing a full `__iter__`/`__next__` iterator, as long as it raises `IndexError` at the end. Only used when `__iter__` is absent.

## Mental Models
- **Protocols are "duck typing with a contract"**: implementing `__len__` and `__getitem__` makes an object behave like a sequence to any code that expects one, without inheriting from an actual sequence base class.
- **An iterable is a factory; an iterator is the thing being consumed**: `__iter__()` on the iterable returns a *fresh* iterator each time, which is why an object with proper `__iter__()` (unlike a plain generator) can be iterated over multiple times independently — each call gets its own `RangeIter`-style counter starting fresh.
- **Right-hand methods exist to avoid position bias**: without `__radd__`, a custom numeric type only works as the *left* operand of `+`; symmetric operations can often reuse the same implementation for both sides, but asymmetric ones (subtraction, division) need genuinely different logic on each side.

## Anti-patterns
- **Implementing `__eq__` without `__ne__`**: Python does not derive `!=` from `==` automatically — omitting `__ne__` leaves inequality checks using default identity-based behavior, which is usually wrong once `__eq__` is customized.
- **Blindly copying a left-hand operator method to the right-hand slot**: only safe for commutative operations (like addition); doing this for subtraction/division without adjusting operand order produces wrong results.
- **Forgetting `raise IndexError` in a `__getitem__`-based iterable fallback**: without it, the implicit iterator created by Python for `__getitem__`-only classes will loop forever trying successive indices.
- **Using a plain generator when repeatable iteration is required**: generators are single-use — once exhausted, an object needing multi-pass iteration (like `range()`) needs a real `__iter__()` that returns a fresh iterator object each call, not a memoized generator.
- **Relying on `__cmp__`**: removed in Python 3.0; must implement the specific rich comparison methods (`__lt__`, `__eq__`, etc.) individually.

## Code Examples
```python
class Example:
    def __init__(self, value):
        self.value = value
    def __add__(self, other):
        return self.value + other
    def __radd__(self, other):
        return self.value + other

Example(20) + 10   # 30 — uses __add__
10 + Example(20)    # 30 — uses __radd__ (int doesn't know how to add an Example)
```
- **What it demonstrates**: without `__radd__`, `10 + Example(20)` raises `TypeError: unsupported operand type(s) for +: 'int' and 'Example'` — the right-hand method is what makes the operation symmetric.

```python
class Range:
    def __init__(self, count):
        self.count = count
    def __iter__(self):
        return RangeIter(self.count)

class RangeIter:
    def __init__(self, count):
        self.count = count
        self.current = 0
    def __iter__(self):
        return self
    def __next__(self):
        value = self.current
        self.current += 1
        if self.current > self.count:
            raise StopIteration
        return value
```
- **What it demonstrates**: a repeatable iterable (unlike a generator function, `list(r)` called twice on the same `Range` instance both times returns `[0, 1, 2, 3, 4]`, because each `__iter__()` call constructs a fresh `RangeIter`).

```python
class Range:
    def __init__(self, count):
        self.count = count
    def __getitem__(self, index):
        if index < self.count:
            return index
        raise IndexError
```
- **What it demonstrates**: the same repeatable-range behavior achieved via the `__getitem__` fallback protocol instead of an explicit iterator class — Python auto-generates the iteration logic by calling `__getitem__(0)`, `__getitem__(1)`, ... until `IndexError`.

## Reference Tables
| Operation | Operator | Left-hand | Right-hand | In-place |
|---|---|---|---|---|
| Addition | `+` | `__add__` | `__radd__` | `__iadd__` |
| Subtraction | `-` | `__sub__` | `__rsub__` | `__isub__` |
| Multiplication | `*` | `__mul__` | `__rmul__` | `__imul__` |
| True division | `/` | `__truediv__` | `__rtruediv__` | `__itruediv__` |
| Floor division | `//` | `__floordiv__` | `__rfloordiv__` | `__ifloordiv__` |
| Modulo | `%` | `__mod__` | `__rmod__` | `__imod__` |
| Div+mod | `divmod()` | `__divmod__` | `__rdivmod__` | N/A |
| Exponent | `**` | `__pow__` | `__rpow__` | `__ipow__` |
| Left shift | `<<` | `__lshift__` | `__rlshift__` | `__ilshift__` |
| Right shift | `>>` | `__rshift__` | `__rrshift__` | `__irshift__` |
| Bitwise AND | `&` | `__and__` | `__rand__` | `__iand__` |
| Bitwise OR | `\|` | `__or__` | `__ror__` | `__ior__` |
| Bitwise XOR | `^` | `__xor__` | `__rxor__` | `__ixor__` |
| Bitwise invert | `~` | `__invert__` | N/A | N/A |

## Worked Example
The book builds up a `Range` class in two parallel implementations to illustrate both halves of the iteration protocol:
1. **Explicit iterator approach**: `Range.__iter__()` returns a new `RangeIter(count)` instance each call. `RangeIter` tracks its own `current` counter, implements `__next__()` to yield the next value or raise `StopIteration` once `current > count`, and implements `__iter__()` returning `self`. Because each call to `Range.__iter__()` creates a brand-new `RangeIter`, calling `list(r)` twice on the same `Range` object both times yields the full sequence — unlike a generator function, which would return `[]` the second time.
2. **`__getitem__` fallback approach**: the same repeatable behavior is achieved far more tersely by defining only `__getitem__(self, index)` that returns `index` while `index < self.count`, else raises `IndexError`. Python's `iter()` detects the absence of `__iter__` and synthesizes an iterator that calls `__getitem__(0)`, `__getitem__(1)`, etc., until `IndexError` — giving the same repeatable-iteration behavior with far less code, at the cost of being a Python-internal special case rather than an explicit protocol implementation.

## Key Takeaways
1. Implementing the right dunder methods lets custom objects work naturally with Python's built-in operators, `for` loops, and functions — without inventing new APIs.
2. `__eq__` and `__ne__` must both be implemented explicitly; Python does not derive one from the other.
3. Right-hand (`__r*__`) methods make an operator symmetric across operand types; in-place (`__i*__`) methods optimize augmented assignment.
4. An iterable's `__iter__()` should return a *fresh* iterator object each call if the sequence needs to support independent, repeatable iteration — generators, by contrast, are single-pass.
5. An iterator must raise `StopIteration` from `__next__()` to signal exhaustion, since `None` is itself a valid value that could otherwise be yielded.
6. The `__getitem__`-based iteration fallback lets a class be iterable with minimal code, but only kicks in when `__iter__` is absent — and requires raising `IndexError` at the end or it will loop forever.
7. `__pow__` accepting an optional `modulo` argument enables efficient modular exponentiation via 3-argument `pow()`, useful in cryptographic contexts.

## Connects To
- **Ch 1 (Principles and Philosophy)**: dictionary `get()` vs. `__getitem__()` (introduced there as the "one obvious way" example) is the same underlying protocol expanded here.
- **Ch 2 (Advanced Basics)**: generator expressions and the `for`/iteration discussion there are formalized here into the full iterator protocol; `StopIteration`'s role in generators connects directly to this chapter's iterator `__next__()` contract.
- **Ch 4 (Classes)**: `__getattr__` (used in the mixin example) and namespace/`__prepare__` customization connect to this chapter's protocol-implementation approach; `isinstance()`-based introspection underlies `__index__`/number-protocol coercion checks.
- **Ch 6 (Object Management)**: iterator garbage collection (what happens to an abandoned iterator) is covered in the object lifecycle discussion there.
- **Ch 11 (Sheets: A CSV Framework)**: descriptor-based field access (a related but distinct protocol, `__get__`/`__set__`) builds on the dunder-method mindset introduced in this chapter.
