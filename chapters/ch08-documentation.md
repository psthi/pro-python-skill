# Chapter 8: Documentation

## Core Idea
Documentation is a distinct skill from writing code, aimed strictly at humans; effective documentation spans a spectrum from the cheapest/most automatic (good naming) through comments and docstrings (embedded, introspectable at runtime) to dedicated external documents (tutorials, references) — and choosing the right combination depends on your application's needs and audience.

## Frameworks Introduced
- **Proper naming as documentation**: classes/variables should be singular nouns (`Book`, `first_name`); functions should be verbs (`find()`, `process_user()`). A well-named function signature (`find_words(text, word)`) documents itself far better than a vague one (`action(var1, var2)`), with zero runtime or maintenance cost.
- **Comments (`#`)**: inline, alongside code, best used to explain *why* code does something (not what — that's what naming/docstrings are for). No multi-line comment syntax in Python — each line needs its own `#`. Not introspectable at runtime (invisible to any tooling once the source isn't being read directly).
- **Docstrings**: a string literal as the first statement in a module/function/class body, automatically stored on the `__doc__` attribute and accessible via introspection at runtime — the key advantage over comments. No enforced format (PEP 257 offers recommendations, not requirements), but the book's four-part checklist: describe what the function does (one sentence, ideally one line), explain the arguments, document the return value's nature (not just its type — what does it *represent*), and document expected/deliberately-raised exceptions.
- **External documentation categories**: installation/configuration guides, tutorials (first-contact, showcases strengths, aimed at conversion), and reference documents (assumes familiarity, supports ongoing lookup) — different audiences at different stages need different documentation types, and very simple applications may not need reference docs at all.
- **reStructuredText (RST/ReST)**: a WYSIWYM (What You See Is What You Mean, as opposed to WYSIWYG) markup language for technical documentation, provided by the third-party `docutils` package — favors plain readability of the *source* text over exact visual control.
- **Sphinx**: builds on reStructuredText to manage documentation as a linked *collection* of documents (rather than one file at a time), generating output like a linked HTML site or a single combined PDF; analogous in spirit to Javadoc/Doxygen but content-first rather than purely code-extraction-first.

## Key Concepts
- **`__doc__`**: the attribute holding a module/function/class's docstring, accessible at runtime — the mechanism that lets automated documentation generators pull human-written text directly from source.
- **PEP 8 Naming Conventions**: referenced as the authoritative style guide for identifier naming (included as an appendix in the book).
- **PEP 257**: the docstring convention guide (also appended) — recommendations, not enforced rules.
- **RST paragraph rule**: contiguous non-blank lines form one paragraph; a blank line separates paragraphs; indentation signals a quoted passage.
- **RST code block**: a paragraph ending in `::` followed by an indented block marks that block as preformatted (not necessarily code — any content that shouldn't be reprocessed by the RST parser).
- **RST emphasis**: single asterisks (`*word*`) = emphasis (typically italics); double asterisks (`**word**`) = strong emphasis (typically bold).
- **RST links**: `` `text`_ `` with a matching `.. _text: URL` target defines a named link; `` `text`__ `` (double underscore) plus a bare `__ URL` target defines an anonymous link (no need to repeat the link text as the target label).
- **RST footnotes**: `[1]_` in text, with `.. [1] citation text` elsewhere in the document — used for bibliographic references or minor clarifying asides.

## Mental Models
- **Documentation is written for strictly-human audiences, and that's a different skill than coding**: the chapter explicitly frames documentation ability as separate from programming ability — some programmers are naturally better at one than the other, and improving at documentation is a deliberate, distinct effort.
- **Write the documentation you'd want to read**: since there's no single right style that suits every reader, the author's own preferences (as long as they're genuinely representative of the target audience) are a reasonable anchor for reference-doc style choices.
- **Docstrings vs. comments — audience-visibility difference, not just location**: comments are for someone reading the raw source; docstrings are for anyone at all, including tools and users who never open a source file, because they're runtime-introspectable via `__doc__`.

## Anti-patterns
- **Vague, generic argument/function names** (`def action(var1, var2)`): forces every reader to infer meaning from the function body alone — the cheapest documentation win (accurate naming) is being skipped.
- **Explaining *what* code does in a comment when the *why* is what's actually missing**: comments are most valuable for intent/rationale that isn't obvious from the code itself; restating the obvious in a comment doesn't add value.
- **Docstrings that document only the return value's type, not its meaning**: e.g. saying a function "returns a list" without specifying that the list contains *indexes of matches* rather than the matches themselves — the type alone doesn't tell the caller enough to use the return value correctly.
- **Skipping documentation of exceptions a function deliberately raises as part of its contract**: callers who need to catch specific exceptions can't do so reliably if the docstring doesn't say which ones are expected and under what conditions.
- **Distracting inline URLs in RST source** (embedding the target directly inside backticks/angle-brackets rather than as a named reference at the end of the document): saves a line but makes the source harder to read, especially with multiple links.

## Code Examples
```python
def find_words(text, word):
    """
    Locate all instances of a word in a given piece of text.
    Return a list of indexes where the words were found.
    If no instances of the word were found, return an empty list.

    text -- a block of text to search
    word -- an individual word to search for
    """
```
- **What it demonstrates**: a docstring following the book's four-part checklist — what the function does, what each argument means, and precisely what the return value represents (index positions, not the matched words themselves, and the empty-list case is explicit).

```rst
This paragraph shows the basics of how a link is formed in reStructuredText.
You can find additional information in the `official documentation`_.

.. _official documentation: http://docutils.sf.net/docs/
```
- **What it demonstrates**: a named RST link — multi-word link text enclosed in backticks with a trailing underscore, resolved against a target definition elsewhere in the document (commonly placed at the end so it doesn't interrupt the narrative flow).

```rst
The reStructuredText format isn't part of Python itself, but it's popular enough
that even published books [1]_ reference it as an integral part of the Python
development process.

.. [1] Alchin, Marty. *Pro Python*. Apress, 2010.
```
- **What it demonstrates**: an RST footnote reference and its corresponding citation definition — useful for bibliographic references without breaking the reading flow of the main text.

## Reference Tables
| Documentation type | Audience stage | Introspectable at runtime? |
|---|---|---|
| Naming | Anyone reading a signature | No, but free |
| Comments | Someone reading raw source | No |
| Docstrings | Anyone/anything via `__doc__` | Yes |
| Installation/config docs | First contact | No |
| Tutorials | New users, conversion | No |
| Reference docs | Experienced users | No (usually generated from docstrings + prose) |

| RST syntax | Effect |
|---|---|
| blank line | paragraph separator |
| `::` + indent | preformatted/code block |
| `*text*` | emphasis (italics) |
| `**text**` | strong emphasis (bold) |
| `` `text`_ `` + `.. _text: URL` | named link |
| `` `text`__ `` + `__ URL` | anonymous link |
| `[1]_` + `.. [1] ...` | footnote |

## Key Takeaways
1. Good naming is the cheapest, always-available form of documentation — invest in it before reaching for comments or docstrings.
2. Comments explain *why*; docstrings explain *what* (and are runtime-introspectable via `__doc__`, comments are not).
3. A complete docstring covers: one-sentence purpose, argument meanings, the *meaning* (not just type) of the return value, and any exceptions the function deliberately raises as part of its contract.
4. Different documentation types serve different audience stages: installation/config (before use), tutorials (first contact, conversion), reference (ongoing use by experienced users) — not every application needs all three.
5. reStructuredText favors readable plain-text source (WYSIWYM) over precise visual control (WYSIWYG); Sphinx extends it to manage a whole linked document collection rather than one file at a time.
6. There's no single correct documentation style — write the kind of documentation you personally find useful to read, since your target audience likely shares your sensibilities if they're drawn to your software.

## Connects To
- **Ch 1 (Principles and Philosophy)**: "Readability Counts" is invoked directly regarding reStructuredText's plain-text-first design philosophy.
- **Ch 3 (Functions)**: docstring access via `__doc__`/`inspect.getdoc()` (introduced there for function introspection) underlies this chapter's emphasis on docstrings being runtime-accessible.
- **Ch 4 (Classes)**: docstring conventions extend the same introspection points (module/function/class `__doc__`) discussed there.
- **Ch 9 (Testing)**: the chapter explicitly hands off to testing as "the next chapter," framing tests as verifying that documentation stays accurate — i.e. documentation and tests both describe intended behavior, from different angles.
- **Ch 10 (Distribution)**: installation/configuration documentation is flagged here as depending on the distribution approach covered in that chapter.
