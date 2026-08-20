# Chapter 7: Strings

## Core Idea
Python distinguishes bytes (raw, single-byte-per-character sequences with no linguistic meaning) from text/Unicode strings (multi-byte-capable, meant for human language), and correctly converting between them via an explicit encoding (usually UTF-8) — rather than guessing — is essential to avoid `UnicodeEncodeError`/`UnicodeDecodeError` and silent data corruption.

## Frameworks Introduced
- **Bytes vs. Text distinction**: `bytes` objects (`b'example'` literal) represent raw byte sequences with no inherent character meaning — appropriate for non-textual data (numbers, binary structures, file I/O). Standard `str` is always Unicode in Python 3, representing actual human-language text.
  - When to use bytes: file/network I/O, binary protocols, anything not meant to be *read* as language.
  - When to use str: anything conceptually textual — user-facing content, parsed input, generated output.
- **`ord()`/`chr()`**: convert a single byte/character to/from its integer code point — simple but limited to values 0–255 and don't handle multi-byte structures.
- **The `struct` module** (`struct.pack()`/`struct.unpack()`): a format-string-driven way to convert between Python values and byte sequences, supporting multi-byte integers (`H`/`h` for 2-byte, `I`/`i` for 4-byte, `Q`/`q` for 8-byte; uppercase = unsigned, lowercase = signed), floats (`f`), fixed-width strings (`Ns`), and explicit endianness (`<` little-endian, `>` big-endian prefix).
  - When to use: binary protocol parsing, interoperating with non-Python systems/files with a fixed byte layout.
- **Text encodings** (`str.encode(name)` / `bytes.decode(name)`): convert between Unicode text and a specific byte representation. ASCII covers only 127 characters (English-only, 1 byte/char); UTF-8 is a variable-length Unicode encoding (1–4 bytes/char) that's backward-compatible with ASCII (any ASCII byte sequence is valid UTF-8) and is efficient for mostly-English text while supporting the full Unicode range.
- **String substitution (`%` operator)**: `'template %s' % value` — `%s` calls `str()` on the value, `%r` calls `repr()`. Multiple values are supplied as a tuple; a single tuple value being substituted must itself be wrapped in a 1-tuple to avoid Python misinterpreting it as multiple substitution arguments.

## Key Concepts
- **Byte string literal**: `b'...'` — a `bytes` object in Python 3.0+; in Python 2.6+ syntactically accepted but produces a plain `str`, not a distinct type (a source of cross-version incompatibility the book flags as unresolvable without `2to3`).
- **Unicode code point**: a number representing a character, symbol, or modifier in the Unicode standard (over a million defined); not always a 1:1 mapping to "one visible character" (e.g. combining accent marks).
- **Endianness**: the byte order of a multi-byte value — big-endian stores the most significant byte first, little-endian stores the least significant byte first; must match between producer and consumer or values decode incorrectly.
- **UTF-8's three key properties**: (1) can represent any Unicode code point; (2) more common characters take fewer bytes (ASCII range = 1 byte); (3) fully backward-compatible with ASCII byte-for-byte.
- **`%s` vs `%r` in substitution**: `%s` uses `__str__()` (human-readable); `%r` uses `__repr__()` (unambiguous/debug-oriented) — the book recommends `%r` for logging function arguments since it clearly delimits strings and shows type-distinguishing detail (e.g. quotes around strings).
- **Python 2 vs 3 encode/decode split**: in Python 2, both byte strings and Unicode strings had `encode()`/`decode()` and were often used interchangeably (a frequent source of bugs); Python 3 restricts `encode()` to `str` and `decode()` to `bytes`, making the direction of conversion unambiguous.

## Mental Models
- **Bytes are "meaning-agnostic transport"**: a `bytes` object makes no assumptions about what its contents represent — it's your job to interpret them (as text via decoding, as structured binary via `struct`, or as opaque data passed straight through).
- **An encoding is a lossy-or-lossless *mapping choice*, not a property of the text itself**: the same Unicode string can be validly encoded multiple different ways (UTF-8, UTF-16, etc.); choosing the wrong encoding when *decoding* (assuming ASCII when the source was UTF-8, for instance) doesn't always raise an error — it can produce silently wrong "gibberish" text.
- **Think of `struct` formats as a tiny DSL for describing a byte layout**: each character in the format string both selects a type and consumes the correct positional argument(s) — mismatched counts/order break the roundtrip.

## Anti-patterns
- **Assuming byte-string literals (`b'...'`) behave identically across Python 2 and 3**: pre-3.0, `b'...'` just produces a regular `str`; there is no way to write source that is simultaneously correct and idiomatic on both sides of the 2/3 divide — the book recommends writing Python 2 syntax and using `2to3` to convert, rather than trying to hand-write dual-compatible code.
- **Guessing an encoding instead of tracking it explicitly** (echoing Ch. 1's "refuse the temptation to guess"): decoding with the wrong assumed encoding can silently produce corrupted (but not necessarily error-raising) text.
- **Substituting a bare tuple into a `%`-style format string**: Python can't distinguish "a tuple that is itself the single value to inject" from "multiple positional values to inject" — passing a 2-item tuple where only one `%s` placeholder exists raises `TypeError: not all arguments converted during string formatting`; the fix is to wrap the intended single tuple value in another 1-tuple, e.g. `'%r' % (args,)`.
- **Using `ord()`/`chr()` for anything beyond single-byte, English-range conversions**: doesn't scale to multi-byte structures or values outside 0–255 — use `struct` instead.
- **Relying on implicit string coercion for concatenation**: Python does not auto-convert non-string types for `+` concatenation — must explicitly call `str()` first, or use `%`/`.format()` substitution instead.

## Code Examples
```python
>>> struct.pack(b'10s10sB', last_name, first_name, age)
b'Alchin\x00\x00\x00\x00Marty\x00\x00\x00\x00\x00\x1c'
```
- **What it demonstrates**: packing multiple heterogeneous values (two fixed-width strings padded with null bytes, plus an unsigned byte) into a single binary structure in one call — the inverse `struct.unpack()` with the same format string recovers all three values.

```python
>>> unicode = 'This is a test: \u20ac'  # Euro symbol
>>> unicode.encode('utf-8')
b'This is a test: \xe2\x82\xac'
>>> unicode.encode('ascii')
Traceback (most recent call last):
  ...
UnicodeEncodeError: 'ascii' codec can't encode character '\u20ac' in position 16: ordinal not in range(128)
```
- **What it demonstrates**: UTF-8 can represent any Unicode code point (including €, outside ASCII's range); ASCII cannot, and raises rather than silently corrupting the value — the safer failure mode compared to a "gibberish" mis-decode.

```python
>>> def log(*args):
...     print('Logging arguments: %r' % args)
...
>>> log('test', 'ing')
Traceback (most recent call last):
  ...
TypeError: not all arguments converted during string formatting
```
- **What it demonstrates**: the classic tuple-substitution trap — `args` is itself a tuple (from `*args`), and `%` substitution can't tell "this tuple IS the one value" from "these are N values to fill N placeholders."

## Reference Tables
| `struct` format code | Meaning | Bytes | Signed? |
|---|---|---|---|
| `B` / `b` | byte | 1 | unsigned / signed |
| `H` / `h` | short | 2 | unsigned / signed |
| `I` / `i` | int | 4 | unsigned / signed |
| `Q` / `q` | long long | 8 | unsigned / signed |
| `f` | float | 4 | n/a |
| `Ns` | fixed-width string | N | n/a |
| `<` prefix | little-endian | — | — |
| `>` prefix | big-endian | — | — |

| Substitution placeholder | Calls |
|---|---|
| `%s` | `str(value)` |
| `%r` | `repr(value)` |

## Worked Example
The book walks through the motivation for the `struct` module by starting from `ord()`/`chr()`'s limitations:
1. `ord(b'A')` → `65`; `chr(65)` → `'A'` — fine for single bytes, but `chr()` returns a standard `str`, not a `bytes` object, and neither handles values above 255 or multi-byte layouts.
2. Introduce `struct.pack(b'B', 65)` as the more robust single-byte equivalent, then extend to multi-byte integers (`H`/`h`), demonstrating that byte order (endianness) affects the packed value's meaning — `struct.unpack(b'H', b'*\x00')` gives `42`, while the same bytes reversed give `10752`.
3. Show explicit endianness control via `<`/`>` prefixes so packed data reliably round-trips with external systems that have a fixed byte-order expectation.
4. Extend to packing multiple heterogeneous values (fixed-width strings + an integer) in one call — a realistic binary-record use case (packing a person's `last_name`, `first_name`, and `age` into one byte string).

## Key Takeaways
1. Treat `bytes` and `str` as fundamentally different — `bytes` is raw, meaning-agnostic data; `str` is Unicode text meant to be read as language.
2. Use `struct.pack()`/`struct.unpack()` (not `ord()`/`chr()`) for multi-byte or mixed-type binary structures, and always specify endianness explicitly when interoperating with external systems.
3. UTF-8 is the practical default text encoding: full Unicode coverage, ASCII-backward-compatible, and space-efficient for mostly-ASCII content.
4. Never guess an unknown encoding — an incorrect guess can silently corrupt text rather than raising a clear error.
5. Prefer `%r` over `%s` for debugging/logging output, since `repr()` disambiguates types (e.g. shows quotes around strings) that `str()` would not.
6. When substituting a tuple as a single value into a `%`-format string, wrap it in an extra 1-tuple (`'%r' % (value,)`) to avoid Python misinterpreting its elements as separate substitution arguments.
7. Python 3 cleanly separates `encode()` (str → bytes) from `decode()` (bytes → str) — no more ambiguous interchangeable use as existed in Python 2.

## Connects To
- **Ch 1 (Principles and Philosophy)**: "in the face of ambiguity, refuse the temptation to guess" is directly embodied in this chapter's encoding-must-be-explicit guidance.
- **Ch 2 (Advanced Basics)**: `UnicodeDecodeError` handling (referenced there as a file-reading exception type) is explained fully here.
- **Ch 5 (Common Protocols)**: string substitution's `%` operator is backed by `__mod__()`, the same operator-overloading protocol covered there.
