"""Unit tests for the read-only SQL guard (Spatial ETL Pipeline).

The Streamlit SQL Explorer feeds free-form SQL to query_database(); these
tests pin the validation layer that must reject anything mutating.
"""

import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / "2_Programming_Data_Science" / "Spatial Data ETL Pipeline" / "src" / "sql_guard.py"

spec = importlib.util.spec_from_file_location("sql_guard", MODULE_PATH)
sql_guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sql_guard)


def _rejects(q):
    try:
        sql_guard.assert_readonly_query(q)
    except sql_guard.UnsafeSQLError:
        return True
    return False


class TestAllowedQueries:
    def test_select(self):
        assert sql_guard.assert_readonly_query("SELECT * FROM districts") == "SELECT * FROM districts"

    def test_select_lowercase(self):
        assert not _rejects("select name from districts limit 5")

    def test_with_cte(self):
        assert not _rejects("WITH x AS (SELECT 1) SELECT * FROM x")

    def test_explain(self):
        assert not _rejects("EXPLAIN QUERY PLAN SELECT * FROM districts")

    def test_leading_parens(self):
        assert not _rejects("((SELECT 1))")

    def test_trailing_semicolon_ok(self):
        assert not _rejects("SELECT 1;")

    def test_comments_before_select_ok(self):
        assert not _rejects("-- note\nSELECT 1")


class TestRejectedQueries:
    def test_drop_table(self):
        assert _rejects("DROP TABLE districts")

    def test_delete(self):
        assert _rejects("DELETE FROM districts WHERE 1=1")

    def test_update(self):
        assert _rejects("UPDATE districts SET population = 0")

    def test_insert(self):
        assert _rejects("INSERT INTO districts VALUES (1)")

    def test_create(self):
        assert _rejects("CREATE TABLE evil (x TEXT)")

    def test_attach(self):
        assert _rejects("ATTACH DATABASE '/tmp/x.db' AS x")

    def test_multiple_statements(self):
        assert _rejects("SELECT 1; DROP TABLE districts")

    def test_with_delete_compound(self):
        assert _rejects("WITH x AS (SELECT 1) DELETE FROM districts")

    def test_empty(self):
        assert _rejects("")
        assert _rejects("   ")
        assert _rejects(";;;")

    def test_comment_hiding_drop(self):
        assert _rejects("/* harmless */ DROP TABLE districts")

    def test_lowercase_drop_still_rejected(self):
        assert _rejects("drop table districts")
