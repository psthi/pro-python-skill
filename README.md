# Pro Python Universal Agentic AI Skill 🐍✨

[![skills.sh](https://img.shields.io/badge/skills.sh-pro--python-000000.svg?logo=vercel&logoColor=white)](https://skills.sh)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%2B-blue.svg)](https://python.org)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Compatible Agents](https://img.shields.io/badge/Agents-Antigravity%20%7C%20Claude%20%7C%20Gemini%20%7C%20PicoClaw%20%7C%20Nanobot%20%7C%20Hermes-purple.svg)](SKILL.md)

> **The definitive universal agent skill distilling Marty Alchin's classic *"Pro Python"* (Apress), fully modernized for Python 3.10–3.13+. Equips AI coding assistants with deep object model reasoning, advanced OOP patterns, C3 linearization, and declarative framework architecture.**

---

## ⚡ Instant Install via `skills.sh` / `npx skills`

Install this skill instantly into **any** agentic coding harness (**Claude Code**, **Cursor**, **Windsurf**, **Gemini CLI**, **PicoClaw**, **Nanobot**, **Hermes**, **OpenClaw**, **OpenHands**, **Roo Code**, **Goose**, etc.):

```bash
# 🚀 Universal 1-command install (interactive)
npx skills add psthi/pro-python-skill

# 🌐 Install globally across all current and future workspaces
npx skills add psthi/pro-python-skill -g

# 🎯 Install specifically for a target agent (e.g. Claude Code)
npx skills add psthi/pro-python-skill -g --agent claude-code

# 📋 Preview available skills without installing
npx skills add psthi/pro-python-skill --list
```

---

## 📑 Table of Contents
- [Instant Install (`skills.sh`)](#-instant-install-via-skillssh--npx-skills)
- [Executive Overview](#-executive-overview)
- [Why This Skill?](#-why-this-skill)
- [Quickstart for Novices](#-quickstart-for-novices)
- [Deep Dive for Advanced Developers](#-deep-dive-for-advanced-developers)
  - [1. C3 Linearization & Cooperative `super()`](#1-c3-linearization--cooperative-super)
  - [2. Class Customization: `__init_subclass__` vs Metaclasses](#2-class-customization-__init_subclass__-vs-metaclasses)
  - [3. Type-Preserving Decorators with `ParamSpec`](#3-type-preserving-decorators-with-paramspec)
  - [4. Structural Subtyping with `typing.Protocol`](#4-structural-subtyping-with-typingprotocol)
- [Chapter & Reference Index (12 Chapters)](#-chapter--reference-index-12-chapters)
- [Executable Code Examples](#-executable-code-examples)
- [Contributing & License](#-contributing--license)

---

## 🌟 Executive Overview

While most developer AI prompts rely on generic syntax rules, **`pro-python`** embeds the foundational mental models and architectural design patterns that separate amateur scripts from professional Python frameworks.

Synthesized from Marty Alchin's *Pro Python* and bridged with modern Python 3.10–3.13+ language primitives (PEPs 487, 544, 557, 593, 612, 634, 654), this skill provides:
1. **Deterministic OOP Decisions**: When to use Metaclasses vs `__init_subclass__`, how MRO resolves in multiple inheritance, and how to write cooperative `super()` chains.
2. **Negative Constraints & Anti-Patterns**: "Tells & Smells" rules that stop LLMs from introducing subtle bugs (e.g. keying caches on instances inside decorator closures, bare `except:`, or omitting `functools.wraps`).
3. **Declarative Framework Engineering**: Architectural runbook for designing ORMs, schema validators, and data pipelines.

---

## 🆚 Why This Skill?

```
┌───────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Typical LLM Behavior          │ Behavior with Pro Python Skill                              │
├───────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ Uses fragile `isinstance`     │ Employs `typing.Protocol` + duck typing for loose coupling  │
│ Writes monolithic `if/elif`   │ Uses Structural Pattern Matching (`match / case`)           │
│ Leaks memory in closures      │ Implements thread-safe `@functools.cached_property`         │
│ Breaks cooperative MRO chains │ Enforces C3-linearized cooperative `super()` calls          │
│ Guesses text encodings        │ Enforces strict `bytes` vs UTF-8 `str` transport discipline │
└───────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart for Novices

### 1. Install to Local Agents
```bash
npx skills add psthi/pro-python-skill -g
```
*Or clone and run the local multi-agent installer:*
```bash
git clone https://github.com/psthi/pro-python-skill.git
cd pro-python-skill
bash scripts/install.sh
```

### 2. How to Prompt Your AI Agent
Once installed, your agents will automatically reference these frameworks whenever designing Python architectures. You can also query specific chapters or patterns explicitly:
- *"Using the pro-python skill, design a plugin system for our data loaders using `__init_subclass__`."*
- *"Check our class hierarchy against the C3 MRO linearization rules in ch04."*
- *"Refactor this decorator using `ParamSpec` to preserve type hints as described in ch12."*

---

## 💻 Deep Dive for Advanced Developers

### 1. C3 Linearization & Cooperative `super()`
Python flattens multiple-inheritance graphs using the C3 linearization algorithm. `super()` does not call the literal immediate parent in source code; it resolves dynamically against the **runtime instance's MRO**:

```python
class Base:
    def action(self):
        print("Base.action")

class MixinA(Base):
    def action(self):
        print("MixinA start")
        super().action()

class MixinB(Base):
    def action(self):
        print("MixinB start")
        super().action()

class Combined(MixinA, MixinB):
    def action(self):
        super().action()

# MRO: Combined -> MixinA -> MixinB -> Base -> object
# Calling Combined().action() correctly chains through both mixins!
```

---

### 2. Class Customization: `__init_subclass__` vs Metaclasses
- Use **`__init_subclass__`** (PEP 487) for zero-metaclass subclass registries without metaclass conflict issues:
```python
class Exporter:
    registry = {}
    @classmethod
    def __init_subclass__(cls, format_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if format_name:
            cls.registry[format_name] = cls

class HTMLExporter(Exporter, format_name="html"): pass
```
- Reserve **Metaclasses** (`type.__new__` / `__prepare__`) for inspecting/altering the class namespace dictionary before class instantiation occurs.

---

### 3. Type-Preserving Decorators with `ParamSpec`
Never lose argument types or autocomplete when wrapping functions:
```python
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def retry(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
    return wrapper
```

---

### 4. Structural Subtyping with `typing.Protocol`
Define explicit interface contracts decoupled from class inheritance:
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializer(Protocol):
    def serialize(self) -> dict[str, str]: ...
```

---

## 📚 Chapter & Reference Index (12 Chapters)

| # | Chapter | Key Frameworks |
|---|---|---|
| 1 | [ch01: Principles & Philosophy](chapters/ch01-principles-and-philosophy.md) | Zen of Python, Samurai Principle, DRY, Pareto & Robustness Rules |
| 2 | [ch02: Advanced Basics](chapters/ch02-advanced-basics.md) | `try/except/else/finally`, Exception Chaining, Context Managers (`with`), Generators |
| 3 | [ch03: Functions & Decorators](chapters/ch03-functions.md) | `*args`/`**kwargs`, Closures, Optional-Argument Decorator Pattern, Partial Application |
| 4 | [ch04: Classes & Metaclasses](chapters/ch04-classes.md) | Inheritance, C3 Linearization, Cooperative `super()`, Metaclasses, `__prepare__()` |
| 5 | [ch05: Common Protocols](chapters/ch05-common-protocols.md) | Operator Overloading, Comparison Protocols (`__eq__` + `__ne__`), Iterables |
| 6 | [ch06: Object Management](chapters/ch06-object-management.md) | Identity/Type/Value, Borg Pattern, Reference Counting, GC, Caching Descriptors |
| 7 | [ch07: Strings & Encodings](chapters/ch07-strings.md) | `bytes` vs `str`, `struct` Binary Packing, Unicode Encodings, UTF-8 |
| 8 | [ch08: Documentation](chapters/ch08-documentation.md) | Naming discipline, Docstring standards, reStructuredText, Sphinx |
| 9 | [ch09: Testing](chapters/ch09-testing.md) | `doctest` vs `unittest.TestCase`, Assertion specificity (`assertEqual` vs `assertTrue`) |
| 10 | [ch10: Distribution & Packaging](chapters/ch10-distribution.md) | Licensing (MIT/BSD/LGPL/GPL), Packaging history, PyPI standards |
| 11 | [ch11: Sheets CSV Framework](chapters/ch11-sheets-csv-framework.md) | Capstone Declarative Framework, Metaclass field registration, Instantiation ordering |
| 12 | [ch12: Modern Python Bridge](chapters/ch12-modern-python-bridge.md) | `__init_subclass__`, `typing.Protocol`, `@functools.cached_property`, `ParamSpec`, `@dataclass(slots=True)`, `match/case`, `pyproject.toml` |

---

## 🧪 Executable Code Examples

Located in [`examples/`](examples/):
- [`examples/01_cooperative_multiple_inheritance.py`](examples/01_cooperative_multiple_inheritance.py): Verified C3 MRO resolution demo.
- [`examples/02_plugin_registry_init_subclass.py`](examples/02_plugin_registry_init_subclass.py): Zero-metaclass plugin registration.
- [`examples/03_type_safe_decorator.py`](examples/03_type_safe_decorator.py): Modern `ParamSpec` type-preserving wrapper.
- [`examples/04_structural_protocol.py`](examples/04_structural_protocol.py): Runtime & static structural protocol verification.

---

## 📄 Contributing & License

- **Skill Wrapper License**: [Apache-2.0](LICENSE)
- **Source Attribution**: Based on *"Pro Python"* by Marty Alchin (Apress, 2010), synthesized and modernized for Python 3.10–3.13+ coding agents.
- **Framework & Tooling Credit**: Structured and generated using the [book-to-skill](https://github.com/virgiliojr94/book-to-skill) framework by [@virgiliojr94](https://github.com/virgiliojr94).
