#!/usr/bin/env python3
"""Executable models for atomic ledger/projection and completeness boundaries."""
import sqlite3
import tempfile
from pathlib import Path


def test_ledger_projection_one_transaction():
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "evidence.sqlite"
        con = sqlite3.connect(db)
        con.execute("CREATE TABLE ledger(event_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        con.execute("CREATE TABLE projection(event_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        con.commit()
        con.execute("BEGIN IMMEDIATE")
        con.execute("INSERT INTO ledger VALUES (?, ?)", ("evt-1", "payload"))
        con.execute("INSERT INTO projection VALUES (?, ?)", ("evt-1", "payload"))
        con.commit()
        assert con.execute("SELECT event_id FROM ledger").fetchall() == [("evt-1",)]
        assert con.execute("SELECT event_id FROM projection").fetchall() == [("evt-1",)]
        con.execute("BEGIN IMMEDIATE")
        con.execute("INSERT INTO ledger VALUES (?, ?)", ("evt-2", "payload2"))
        con.execute("INSERT INTO projection VALUES (?, ?)", ("evt-2", "payload2"))
        con.rollback()
        assert con.execute("SELECT event_id FROM ledger ORDER BY event_id").fetchall() == [("evt-1",)]
        assert con.execute("SELECT event_id FROM projection ORDER BY event_id").fetchall() == [("evt-1",)]
        con.close()


def test_stale_json_writer_loses_projection_event():
    ledger = set()
    initial = set()
    writer_a = initial.copy()
    writer_b = initial.copy()
    ledger.add("a")
    writer_a.add("a")
    projection = writer_a.copy()
    ledger.add("b")
    writer_b.add("b")
    projection = writer_b.copy()
    assert ledger == {"a", "b"}
    assert projection == {"b"}
    assert not ledger.issubset(projection)


def test_valid_prefix_needs_external_checkpoint_for_completeness():
    full_chain = ["digest-1", "digest-2", "digest-3"]
    truncated_chain = full_chain[:2]
    assert truncated_chain == ["digest-1", "digest-2"]
    assert len(truncated_chain) < len(full_chain)
    trusted_expected_count = 3
    assert len(truncated_chain) != trusted_expected_count


if __name__ == "__main__":
    test_ledger_projection_one_transaction()
    test_stale_json_writer_loses_projection_event()
    test_valid_prefix_needs_external_checkpoint_for_completeness()
    print("PASS CXLV: atomic ledger/projection commit+rollback; stale-writer loss; external checkpoint requirement (3/3)")
