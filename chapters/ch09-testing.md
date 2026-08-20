# Chapter 9: Testing

## Core Idea
Python offers two complementary testing approaches — doctests (executable documentation, embedded directly in docstrings as interactive-interpreter-formatted examples) for simple, self-documenting checks, and the `unittest` module (a full object-oriented testing API with `TestCase`, `setUp()`, and dozens of specialized assertion methods) for anything more complex than doctest's input/output paradigm can cleanly express.

## Frameworks Introduced
- **Doctests**: tests written as literal interactive-interpreter transcripts inside docstrings (`>>>` for input lines, `...` for continuation lines, plain text for expected output). Run via `doctest.testmod()`. Because they double as documentation, they must read naturally as documentation while still being machine-verifiable.
  - When to use: simple, illustrative behavior that's naturally expressible as "call this, get that" — the test *is* the usage example.
  - How: write the exact interpreter session (including `repr()`-style output for expressions, or explicit `print()` calls for `str()`-style output); use `...` ellipsis in *output* to skip irrelevant/variable content (e.g. file paths in tracebacks).
- **`unittest.TestCase`**: subclass it to define a suite of test methods (any method name starting with `test`). `setUp()` runs before every individual test method, ensuring each test starts from a consistent state — store shared fixtures as instance attributes (`self.factor = 2`), since `setUp()` takes no arguments and returns nothing.
  - When to use: anything beyond simple input/output pairs — multi-step setup, comparing complex objects, numeric tolerance, exception-testing with more control, or large test suites needing structure/reporting.
- **Assertion method families**: `assertTrue`/`assertFalse` (general boolean checks), `assertEqual`/`assertNotEqual` (delegates to `==`, so benefits from custom `__eq__` per Ch. 5), `assertAlmostEqual`/`assertNotAlmostEqual` (numeric comparison with rounding tolerance, avoids floating-point equality pitfalls), type-specific equality checks (`assertSetEqual`, `assertDictEqual`, `assertListEqual`, `assertTupleEqual`, `assertSequenceEqual`), ordering checks (`assertGreater`, `assertGreaterEqual`, `assertLess`, `assertLessEqual`), and `fail(msg)` for custom failure conditions too complex for a canned assertion.
- **`addTypeEqualityFunc(type, comparison_func)`**: registers a custom comparison for `assertEqual()` to use with a specific type — call it from `__init__()` (not `setUp()`, which reruns per-test and would just re-register redundantly) so it applies once per test-case class instantiation.

## Key Concepts
- **Doctest ellipsis (`...` in output)**: skips matching of the surrounded content — essential for tracebacks (file paths vary by system) and any output with non-deterministic/irrelevant detail.
- **Doctest blank-line separation**: a doctest is separated from surrounding prose in a docstring purely by an extra blank line — no special delimiter syntax needed.
- **`setUp()`**: unusual camelCase naming (inherited stylistically from Java's JUnit, which Python's `unittest` was ported from) — deliberately breaks PEP 8 convention for historical/compatibility reasons.
- **Test discovery convention**: any method whose name starts with `test` on a `TestCase` subclass is treated as an individual test; `setUp()` runs fresh before each one.
- **`unittest.main()`**: the module-level entry point (analogous to `doctest.testmod()`) that discovers and runs all tests when a test file is executed directly.
- **Test output symbols**: `.` = pass, `F` = failure (an assertion didn't hold), `E` = error (an unexpected exception was raised) — each character in the summary line represents one test method run.

## Mental Models
- **Doctests are "documentation that happens to be verifiable"**: the design constraint is that they must read naturally as an example in prose — if a snippet doesn't look like something you'd want in the docs anyway, it doesn't belong in a doctest (use `unittest` instead).
- **`assertEqual` over `assertTrue(a == b)`**: not just style — `assertEqual` can report *both* values in its failure message ("10 != 42"), whereas a bare boolean assertion only tells you "False is not True," losing exactly the diagnostic information a failing test should surface.
- **`setUp()` guarantees a clean, consistent slate per test, not shared mutable state across tests**: because it reruns before every test method, tests should not assume ordering or leftover state from a previous test in the same class.

## Anti-patterns
- **Using `assertTrue(x == y)` instead of `assertEqual(x, y)`**: the failure message loses the actual compared values, making debugging harder for no benefit.
- **Registering `addTypeEqualityFunc()` inside `setUp()`**: since `setUp()` reruns before every test method, this needlessly re-registers the same comparison function repeatedly — put it in `__init__()` instead, which runs once per test-case instantiation.
- **Comparing floating-point values with plain `assertEqual`**: floating-point arithmetic accumulates rounding error; use `assertAlmostEqual`/`assertNotAlmostEqual` with an appropriate `places` tolerance instead.
- **Writing a doctest whose expected output includes non-deterministic content (file paths, memory addresses, timestamps) without ellipsis**: the test will spuriously fail across environments/runs — use `...` to mask the irrelevant portions.
- **Treating doctest as sufficient for complex application logic**: doctest's simple input/output paradigm "breaks down fairly quickly" (the book's own words) once tests need multi-step setup, fixtures, or nuanced comparisons — that's precisely the gap `unittest` fills.

## Code Examples
```python
def times2(value):
    """
    Multiplies the provided value by two. Because input objects can override
    the behavior of multiplication, the result can be different depending on
    the type of object passed in.

    >>> times2(5)
    10
    >>> times2('test')
    'testtest'
    >>> times2(('a', 1))
    ('a', 1, 'a', 1)
    """
    return value * 2

if __name__ == '__main__':
    import doctest
    doctest.testmod()
```
- **What it demonstrates**: doctests embedded directly in a function's docstring, doubling as both usage documentation and an automatically verifiable test — running the module directly (`python times2.py`) executes all its doctests silently unless something fails.

```python
import unittest
import times2

class MultiplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.factor = 2

    def testNumber(self):
        self.assertEqual(times2.times2(5), 42)

if __name__ == '__main__':
    unittest.main()
```
- **What it demonstrates**: a basic `unittest.TestCase` — `setUp()` establishes shared fixture state (`self.factor`), and `testNumber()` (auto-discovered by its `test` prefix) uses `assertEqual` so a failure clearly reports `AssertionError: 10 != 42` rather than the less informative `False is not True`.

## Reference Tables
| Assertion method | Checks |
|---|---|
| `assertTrue(expr)` / `assertFalse(expr)` | boolean truthiness |
| `assertEqual(a, b)` / `assertNotEqual(a, b)` | `==` comparison, reports both values on failure |
| `assertAlmostEqual(a, b, places=7)` | numeric equality with rounding tolerance |
| `assertSetEqual` / `assertDictEqual` / `assertListEqual` / `assertTupleEqual` / `assertSequenceEqual` | type-specific equality with tailored diff output |
| `assertGreater` / `assertGreaterEqual` / `assertLess` / `assertLessEqual` | ordering comparisons |
| `fail(msg)` | explicit unconditional failure for complex conditions |

| Doctest marker | Meaning |
|---|---|
| `>>> ` | a line of input code |
| `... ` | continuation of a multi-line statement |
| plain output lines | expected `repr()` or `print()` output |
| `...` inside output | ellipsis — skip/ignore this content when matching |

## Worked Example
The book converts a single doctest into a growing `unittest` test case to illustrate why `assertEqual` beats `assertTrue`:
1. Start with `self.assertTrue(times2.times2(5) == 10)` — passes, uninteresting.
2. Deliberately break it (`== 42`) to see the failure output: `AssertionError: False is not True` — technically correct but uninformative; you can't tell what the function actually returned.
3. Switch to `self.assertEqual(times2.times2(5), 42)` — the failure now reports `AssertionError: 10 != 42`, immediately showing both the actual and expected values.
4. This motivates the broader `assert*Equal` family (`assertSetEqual`, `assertDictEqual`, etc.) — each is tailored to produce a more useful, type-appropriate diff on failure than a generic boolean check ever could.

## Key Takeaways
1. Use doctests for simple, self-documenting behavior where the test doubles as usage documentation; switch to `unittest` once setup, fixtures, or nuanced comparisons are needed.
2. Prefer `assertEqual`/type-specific assertions over `assertTrue(a == b)` — the failure messages carry far more diagnostic value.
3. `setUp()` runs fresh before every test method in a `TestCase` — don't assume shared mutable state or ordering between tests.
4. Register custom type-equality functions (`addTypeEqualityFunc`) in `__init__()`, not `setUp()`, to avoid redundant re-registration.
5. Use doctest's `...` ellipsis to mask non-deterministic output (file paths, addresses) rather than letting environment differences cause spurious failures.
6. `assertAlmostEqual` (with a `places` tolerance) is the correct tool for floating-point comparisons — plain equality is unreliable due to rounding.
7. Test-driven development (writing failing tests before the implementing code) sharpens the specification of desired behavior before you get absorbed in implementation details — but it's not mandatory; doctests written alongside code still deliver most of the benefit.

## Connects To
- **Ch 1 (Principles and Philosophy)**: DRY's testability benefit (isolating code into small, testable functions) is realized directly through this chapter's unit-testing practices.
- **Ch 5 (Common Protocols)**: `assertEqual()` delegates to `==`, meaning custom `__eq__` implementations from Ch. 5 directly affect how equality-based assertions behave on custom objects.
- **Ch 8 (Documentation)**: doctests are explicitly framed as a continuation of the docstring discipline from that chapter — tests that keep documentation accurate by construction.
