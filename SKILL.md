---
name: pro-python
description: "Comprehensive knowledge base and design pattern manual from \"Pro Python\" by Marty Alchin (Apress), fully modernized for Python 3.10–3.13+. Use when applying advanced OOP frameworks (Metaclasses, __init_subclass__, Descriptors, MRO/super(), Dunder Protocols vs typing.Protocol, Decorator architecture, Memory Management, and Declarative Framework Design)."
license: Apache-2.0
metadata:
  book_title: "Pro Python"
  author: "Marty Alchin"
  publisher: "Apress"
  modernized_for: "Python 3.10 - 3.13+"
  compiled: "2026-08-19"
---

# Pro Python (Modernized Knowledge Base) 🐍✨

**Author**: Marty Alchin | **Scope**: Foundational Python OOP + Modern Python 3.10–3.13+ Bridges | **Chapters**: 12

---

## 🧭 How to Use This Skill

- **General Architectural Guidance**: Query core Python OOP principles, MRO resolution, or decorator mechanics.
- **Topic-Specific Retrieval**: Ask about `decorators`, `metaclasses`, `__init_subclass__`, `protocols`, `descriptors`, `caching`, or `MRO`; the relevant chapter file is pulled on-demand.
- **Direct Chapter Inspection**: Request specific chapters (e.g. `ch04` for Classes/MRO, `ch11` for Declarative CSV Framework, `ch12` for Modern Python 3.10–3.13 Bridge).

---

## 🧠 Core Frameworks & Mental Models

1. **Zen of Python (Ch 1)**: 19 design aphorisms (`import this`, PEP 20) used as an engineering checklist. Key principles: *"Errors should never pass silently"*, *"In the face of ambiguity, refuse the temptation to guess"*, and *"Simple is better than complex"*.
2. **The Samurai Principle**: Functions must raise explicit exceptions rather than returning ambiguous sentinels (e.g. `None`) on failure when `None` could be a legitimate return value.
3. **Closures, Decorators & Type Preservation (Ch 3 & 12)**: Optional-argument decorator pattern (`func=None`, keyword-only options) combined with `functools.wraps` and `typing.ParamSpec` for complete runtime and static type preservation.
4. **Method Resolution Order & Cooperative `super()` (Ch 4)**: C3 linearization flattens multiple-inheritance graphs. `super()` resolves dynamically against the *instance's* full runtime MRO, not the defining class's parent chain in isolation.
5. **Class Customization: Metaclasses vs `__init_subclass__` (Ch 4 & 12)**: Use `__init_subclass__` (PEP 487) for clean, zero-metaclass subclass registries; reserve custom `type` metaclasses for class namespace interception (`__prepare__`) and declarative attribute transformation.
6. **Protocols over Inheritance (Ch 5 & 12)**: Combine runtime dunder implementations (`__iter__`, `__enter__/__exit__`) with structural static subtyping (`typing.Protocol` + `@runtime_checkable`).
7. **Object Identity, `__dict__`, & Self-Caching (Ch 6 & 12)**: Understand identity vs value; replace manual `__dict__` caching patterns with `@functools.cached_property` to avoid closure memory leaks.
8. **Explicit Encoding Discipline (Ch 7 & 12)**: Strict distinction between agnostic `bytes` transport and `str` Unicode; UTF-8 default standard throughout.
9. **Declarative Framework Architecture (Ch 11 & 12)**: Build declarative models when configuration is known in advance with many instances. Modernize with `@dataclass(slots=True)` and `typing.Annotated`.
10. **Modern Build Systems (Ch 10 & 12)**: Replace deprecated `setup.py` / `MANIFEST.in` workflows with standard declarative `pyproject.toml` (PEP 517/518/621).

---

## 📚 Chapter Index

| Chapter | Title | Core Frameworks & Concepts |
| :--- | :--- | :--- |
| **[ch01](chapters/ch01-principles-and-philosophy.md)** | Principles and Philosophy | Zen of Python, DRY, Samurai Principle, Pareto & Robustness Principles |
| **[ch02](chapters/ch02-advanced-basics.md)** | Advanced Basics | `try/except/else/finally`, Exception Chaining, Context Managers (`with`), Generators |
| **[ch03](chapters/ch03-functions.md)** | Functions | `*args`/`**kwargs`, Closures, Optional-Arg Decorators, `functools.partial` |
| **[ch04](chapters/ch04-classes.md)** | Classes & Metaclasses | Inheritance, C3 Linearization, `super()`, Metaclasses, `__prepare__()`, Plugin Mounts |
| **[ch05](chapters/ch05-common-protocols.md)** | Common Protocols | Operator Overloading, Comparison Protocols (`__eq__` + `__ne__`), Iterables |
| **[ch06](chapters/ch06-object-management.md)** | Object Management | Identity/Type/Value, Borg Pattern, Reference Counting, GC, Caching Properties |
| **[ch07](chapters/ch07-strings.md)** | Strings & Encodings | `bytes` vs `str`, `struct` binary packing, Unicode Encodings, UTF-8 |
| **[ch08](chapters/ch08-documentation.md)** | Documentation | Naming discipline, Docstring conventions, reStructuredText, Sphinx |
| **[ch09](chapters/ch09-testing.md)** | Testing | `doctest` vs `unittest.TestCase`, Assertion specificity (`assertEqual` vs `assertTrue`) |
| **[ch10](chapters/ch10-distribution.md)** | Distribution & Packaging | Licensing (MIT/BSD/LGPL/GPL), Packaging history, PyPI standards |
| **[ch11](chapters/ch11-sheets-csv-framework.md)** | Sheets CSV Framework | Capstone Declarative Framework, Metaclass field registration, Instantiation ordering |
| **[ch12](chapters/ch12-modern-python-bridge.md)** | **Modern Python Bridge (3.10–3.13+)** | `__init_subclass__`, `typing.Protocol`, `@functools.cached_property`, `ParamSpec`, `@dataclass(slots=True)`, `match/case`, `pyproject.toml` |

---

## 🗂️ Supporting References

- **[cheatsheet.md](cheatsheet.md)** — Actionable decision rules, thresholds, smells, and anti-patterns.
- **[patterns.md](patterns.md)** — Architectural design patterns with implementation recipes and trade-offs.
- **[glossary.md](glossary.md)** — Definitive cross-indexed terminology dictionary.
