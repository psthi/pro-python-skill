# Chapter 10: Distribution

## Core Idea
Distributing a Python application well requires three deliberate choices — a license (which balances programmer freedom against user freedom differently depending on which you choose), a package structure with `setup.py`/`MANIFEST.in` metadata (built on `distutils`), and a distribution channel (self-hosted, or the standardized/discoverable Python Package Index).

## Frameworks Introduced
- **Open-source license spectrum**: GPL (strong copyleft — distributing GPL-derived code requires distributing its source, but only triggered by *distribution*, not network use), AGPL (closes the "network use" loophole — even interacting with AGPL software over a network triggers the source-disclosure requirement), LGPL (removes the static-linking trigger, letting a library be used by proprietary host applications without binding them to GPL terms), BSD/New BSD/Simplified BSD (minimal restrictions — attribution only, decreasing in scope from original → New (no advertising clause) → Simplified (no non-endorsement clause either)).
  - When to use GPL/AGPL: preserving user freedoms is the priority, even at the cost of restricting downstream commercial/proprietary use.
  - When to use LGPL: a library meant for broad integration, including into proprietary applications, while still requiring that modifications to the library itself stay open.
  - When to use BSD variants: maximizing adoption is the priority, including commercial/proprietary adoption, with minimal obligations beyond attribution.
- **Package directory structure**: separates the actual code (`app_name/` with `__init__.py`), `docs/`, `tests/`, plus `LICENSE.txt`, `README.txt`, `setup.py`, and `MANIFEST.in` at the top level — "package" here means the whole distributable bundle, distinct from Python's own `package` concept (a directory with `__init__.py`).
- **`distutils.core.setup()`**: declarative metadata function describing a distributable package. Required args: `name`, `version` (dot-separated, major.minor.patch convention — major = compatibility promise, minor = features/fixes without breaking compatibility, patch = security/bugfix only), `url`. Optional: `author`/`author_email`, `maintainer`/`maintainer_email`, `description` (one-line), `long_description` (often just the contents of `README.txt`). File-inclusion args: `license` (path to license text), `packages` (list of importable package paths), `package_dir` (maps package name → filesystem location, empty-string key = root fallback), `package_data` (non-Python data files, glob patterns allowed).
- **`MANIFEST.in`**: plain-text file of `distutils` commands controlling which *non-code* files (docs, etc.) get bundled into the distribution archive. Commands: `include`/`exclude` (pattern match, current dir), `recursive-include`/`recursive-exclude` (pattern match, given dir + subdirs), `global-include`/`global-exclude` (pattern match, anywhere in the tree), `graft`/`prune` (whole directories, unconditionally).
- **`sdist` command**: `python setup.py sdist` builds a source distribution archive (format depends on OS by default — `zip` on Windows, `gztar` on Unix/macOS; explicit formats via `--format=zip,gztar,bztar,ztar,tar`), placing the result in a `dist/` directory named `<name>-<version>.<ext>`.
- **PyPI (Python Package Index)**: a centralized, standardized, discoverable package registry. `python setup.py register` creates/updates a project's PyPI page from `setup.py` metadata (three registration flows: use existing account, create one interactively, or auto-generate from OS username); `python setup.py sdist ... upload` builds and uploads a distribution in one step. PyPI rejects re-uploading the same distribution format for an already-published version — a new upload requires bumping the version number.

## Key Concepts
- **Copyleft**: a license property requiring derivative works to carry the same license terms and remain open — the defining feature of the GPL family.
- **Static linking trigger (GPL) vs. network-use trigger (AGPL)**: GPL's source-disclosure obligation is triggered by *distributing* the compiled/combined software; AGPL additionally triggers it when users merely *interact* with the software over a network (closing the "SaaS loophole").
- **Version numbering convention**: major.minor.patch — major = compatibility contract, minor = new features/fixes without breaking compatibility, patch = security/bugfix-only releases.
- **`package_data` vs `package_dir`**: `package_dir` maps package *names* to filesystem *locations* (a location remapping); `package_data` maps package names to lists of *non-Python file patterns* to include (glob-style, e.g. `*.json`) — solving two different problems (where code lives vs. what extra files ship with it).
- **Free software vs. open source (philosophical distinction)**: free software licensing prioritizes preserving user freedoms; open source licensing prioritizes the software development model — not every license qualifies as both, and the distinction can matter for license selection.

## Mental Models
- **Think of the license choice as "whose freedom are you protecting"**: GPL-family licenses protect the *end user's* freedom to inspect/modify, at the cost of restricting what downstream developers can build without disclosing their own source; BSD-family licenses protect the *downstream developer's* freedom to do whatever they want, at the cost of any user-freedom guarantees on derivative works.
- **`setup.py` is a declarative manifest, not an installer script you hand-write**: nearly everything about the package (name, files, metadata) is expressed as keyword arguments to one `setup()` call — the actual install/build/upload logic lives in `distutils`, not in your code.
- **MANIFEST.in vs. `packages`/`package_data` in setup.py**: `setup.py`'s `packages`/`package_data` control what gets *installed* onto a user's system; `MANIFEST.in` controls what gets *bundled into the distribution archive* in the first place (docs, license text, etc.) — related but distinct concerns.

## Anti-patterns
- **Assuming GPL's terms are settled law for Python specifically**: the book notes GPL's "object form"/"statically linked" vocabulary was written for compiled languages like C/C++ and has not been tested in court for dynamic languages like Python — don't treat GPL applicability to Python code as unambiguous.
- **Using the original (advertising-clause) BSD license without understanding its maintenance burden**: every organization that ever contributed must be named in advertising material — a real practical headache as a codebase changes hands, which is precisely why "New BSD" (no advertising clause) exists and is preferred today.
- **Conflating "package" (Python's `__init__.py`-based namespace) with "package" (a distributable bundle)**: the chapter explicitly flags this terminology collision — a distribution package contains one or more Python packages, plus docs/tests/license/setup files.
- **Re-uploading the same version's distribution to PyPI after a change**: PyPI will reject it — always bump the version number before re-uploading, even for a small fix.

## Code Examples
```python
from distutils.core import setup

setup(name='MyApp',
      version='0.1',
      author='Marty Alchin',
      author_email='marty@propython.com',
      url='http://propython.com/',
      packages=['my_app', 'my_app.utils'],
)
```
- **What it demonstrates**: a minimal but complete `setup.py` — the three required fields (`name`, `version`, `url`) plus author metadata and the list of importable packages to install.

```
include docs/*.txt
```
- **What it demonstrates**: a `MANIFEST.in` entry bundling all `.txt` files from the `docs/` directory into the source distribution, without installing them as executable code.

```bash
$ python setup.py sdist --format=zip,gztar upload
```
- **What it demonstrates**: building both a `.zip` (Windows-friendly) and `.tar.gz` (Unix-friendly) source distribution and uploading both to PyPI in a single command.

## Reference Tables
| License family | Source-disclosure trigger | Downstream restriction |
|---|---|---|
| GPL | distribution | derivative works must also be GPL |
| AGPL | distribution OR network interaction | same as GPL, plus network-use case |
| LGPL | distribution of the *library's own* modifications | host application unrestricted |
| BSD / New BSD / Simplified BSD | none (attribution only) | minimal to none |

| `MANIFEST.in` command | Scope | Effect |
|---|---|---|
| `include` / `exclude` | current dir | add / remove matching files |
| `recursive-include` / `recursive-exclude` | given dir + subdirs | add / remove matching files |
| `global-include` / `global-exclude` | entire tree | add / remove matching files |
| `graft` / `prune` | whole directories | add / remove unconditionally |

## Worked Example
The chapter walks through the full distribution pipeline for a hypothetical `MyApp` package:
1. Choose a license (e.g. New BSD for maximal adoption) and place its text in `LICENSE.txt`.
2. Lay out the package directory: `MyApp/{LICENSE.txt, README.txt, MANIFEST.in, setup.py, app_name/, docs/, tests/}`.
3. Write `setup.py` declaring name, version, author, url, and the `packages` list.
4. Write `MANIFEST.in` to bundle documentation files (`include docs/*.txt`) that aren't part of the installable code but should ship with the source distribution.
5. Run `python setup.py sdist` to produce `dist/MyApp-0.1.zip` (or `.tar.gz` depending on platform/explicit `--format`).
6. Register on PyPI (`python setup.py register`) — choose an existing account, create one interactively, or auto-generate credentials from the local OS username.
7. Upload with `python setup.py sdist --format=zip,gztar upload` to publish both archive formats in one step; re-publishing requires a version bump since PyPI rejects duplicate version+format uploads.

## Key Takeaways
1. License choice is a trade-off between protecting end-user freedoms (GPL family) and maximizing downstream adoption freedom (BSD family) — pick based on which matters more for your project's goals.
2. AGPL exists specifically to close the "network service" loophole that lets GPL-licensed server-side code avoid triggering source disclosure.
3. `setup.py`'s `setup()` call is a declarative manifest of package metadata — name, version, url are mandatory; everything else is optional but improves discoverability and usability.
4. `MANIFEST.in` controls what non-code files get bundled into the *distribution archive*; `setup.py`'s `packages`/`package_data` control what gets *installed* — related but separate concerns.
5. `sdist` produces the actual distributable archive; format defaults vary by OS but can be explicitly controlled.
6. PyPI provides standardized discoverability; publishing requires registration and rejects re-uploading an unchanged version number.

## Connects To
- **Ch 8 (Documentation)**: the `docs/` directory in the packaging layout is explicitly tied back to the reStructuredText documentation practices from that chapter.
- **Ch 9 (Testing)**: the `tests/` directory in the packaging layout houses the unit tests discussed there.
- **Ch 11 (Sheets: A CSV Framework)**: this chapter explicitly hands off to the capstone framework-building chapter, noting that framework design (a public API serving other developers) is a distinct design problem from application design.
