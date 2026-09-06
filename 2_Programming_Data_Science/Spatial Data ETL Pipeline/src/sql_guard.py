"""sql_guard.py — Defensive validation for user-supplied SQL (read-only path).

Used by the Streamlit "SQL Explorer" tab and the CLI ``query`` command so a
free-form text box can never mutate (or exfiltrate) the database.

Defense in depth — three independent layers:

1. **Token allow-list**: the first keyword must be SELECT / WITH / EXPLAIN.
2. **Single statement only**: any ';' beyond an optional trailing one rejects.
3. **Connection hardening** (in ``loader.query_database``): the database is
   opened ``mode=ro`` (SQLite read-only URI) *and* ``PRAGMA query_only=ON``
   is set, so even a syntactically valid write (e.g. a ``WITH ... DELETE``)
   fails at the engine level.

Pure standard-library module — unit-testable without pandas installed.
"""

from __future__ import annotations

_ALLOWED_FIRST_TOKENS = {"SELECT", "WITH", "EXPLAIN"}


class UnsafeSQLError(ValueError):
    """Raised when a SQL string is not a read-only, single statement."""


# Write keywords that must never appear as a bare token in an accepted
# statement (string literals, quoted identifiers and comments are skipped
# by the tokenizer, so e.g. WHERE note = 'DROP' stays legal).
_WRITE_KEYWORDS = frozenset({
    "INSERT", "UPDATE", "DELETE", "REPLACE", "DROP", "CREATE", "ALTER",
    "ATTACH", "DETACH", "PRAGMA", "VACUUM", "REINDEX", "ANALYZE",
})


def _scan_write_keywords(sql: str) -> str | None:
    """Return the first bare write keyword found, or None.

    SQLite allows compound statements like `WITH x AS (…) DELETE …`, so a
    first-token allow-list alone is not sufficient. This lightweight scan
    skips 'strings', "quoted identifiers", [bracket identifiers], -- line
    and /* block */ comments before matching whole words.
    """
    i, n = 0, len(sql)
    while i < n:
        ch = sql[i]

        if ch.isspace():
            i += 1
            continue

        if sql.startswith("--", i):                      # line comment
            nl = sql.find("\n", i)
            i = n if nl == -1 else nl + 1
            continue

        if sql.startswith("/*", i):                      # block comment
            end = sql.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue

        if ch == "'":                                     # string literal
            i += 1
            while i < n:
                if sql[i] == "'":
                    if i + 1 < n and sql[i + 1] == "'":  # escaped ''
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue

        if ch in ('"', "`"):                              # quoted identifier
            quote = ch
            i += 1
            while i < n:
                if sql[i] == quote:
                    if i + 1 < n and sql[i + 1] == quote:
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue

        if ch == "[":                                     # [identifier]
            end = sql.find("]", i + 1)
            i = n if end == -1 else end + 1
            continue

        if ch.isalpha() or ch == "_":                     # bare word
            j = i
            while j < n and (sql[j].isalnum() or sql[j] == "_"):
                j += 1
            word = sql[i:j].upper()
            if word in _WRITE_KEYWORDS:
                return word
            i = j
            continue

        i += 1
    return None


def _first_token(sql: str) -> str:
    s = sql.strip()
    # strip leading parens/whitespace: "((SELECT 1))"
    while s.startswith("("):
        s = s[1:].lstrip()
    # strip SQL comments that could hide the real first keyword
    while s.startswith("--"):
        s = s.split("\n", 1)[1] if "\n" in s else ""
        s = s.lstrip()
    while s.startswith("/*"):
        end = s.find("*/")
        if end == -1:
            return ""
        s = s[end + 2:].lstrip()
    return s.split(None, 1)[0].upper() if s else ""


def assert_readonly_query(sql: str) -> str:
    """Validate that ``sql`` is a single read-only statement; return it.

    Raises ``UnsafeSQLError`` with a user-friendly message otherwise.
    """
    if not sql or not sql.strip():
        raise UnsafeSQLError("Query is empty.")

    body = sql.strip()
    while body.endswith(";"):
        body = body[:-1].rstrip()

    if not body:
        raise UnsafeSQLError("Query is empty.")

    if ";" in body:
        raise UnsafeSQLError(
            "Only a single statement is allowed (no ';' separators)."
        )

    token = _first_token(sql)
    if token not in _ALLOWED_FIRST_TOKENS:
        raise UnsafeSQLError(
            "Only read-only queries are allowed "
            f"(SELECT / WITH / EXPLAIN) — statement starts with '{token or '?'}'."
        )

    # Catch compound statements like `WITH x AS (…) DELETE …` where the first
    # token is legal but the statement is still a write.
    write_word = _scan_write_keywords(body)
    if write_word:
        raise UnsafeSQLError(
            f"Read-only policy: '{write_word}' is not allowed inside a query."
        )

    return sql
