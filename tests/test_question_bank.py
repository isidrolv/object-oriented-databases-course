"""Pruebas de integridad del banco de reactivos.

    pytest -q
"""

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_question_bank as builder  # noqa: E402


@pytest.fixture(scope="module")
def bank():
    return json.loads((ROOT / "question-bank.json").read_text(encoding="utf-8"))


def test_has_60_questions_20_per_level(bank):
    assert len(bank) == 60
    assert Counter(q["level"]["es"] for q in bank) == {"Básico": 20, "Intermedio": 20, "Avanzado": 20}


def test_master_is_valid(bank):
    assert builder.validate(bank) == []


def test_answers_are_balanced(bank):
    assert Counter(q["answer"] for q in bank) == {"a": 15, "b": 15, "c": 15, "d": 15}


def test_balance_is_idempotent(bank):
    import copy
    assert builder.balance(copy.deepcopy(bank)) is False


def test_languages_are_aligned(bank):
    for q in bank:
        assert len(q["options"]["es"]) == len(q["options"]["en"]) == 4


def test_lessons_exist(bank):
    lessons = {p.name[:2] for p in (ROOT / "book" / "lecciones").glob("*.md")}
    for q in bank:
        assert q["lesson"] in lessons, f"#{q['id']} apunta a una lección inexistente"


@pytest.mark.parametrize("name,lang", [
    ("oodb-questions.json", "es"), ("oodb-questions-en.json", "en"),
    ("quiz-es.json", "es"), ("quiz-en.json", "en"),
])
def test_derived_files_match_master(bank, name, lang):
    derived = json.loads((ROOT / name).read_text(encoding="utf-8"))
    assert len(derived) == len(bank)
    for d, q in zip(derived, bank):
        assert d["id"] == q["id"]
        assert d["question"] == q["question"][lang]
        assert d["options"] == q["options"][lang]
        assert d["answer"] == q["answer"]
