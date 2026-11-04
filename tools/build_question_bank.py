"""
Valida el banco maestro bilingüe `question-bank.json`, equilibra la posición de
las respuestas correctas (a/b/c/d) y genera los archivos derivados que usan los
programas de autoevaluación.

    python tools/build_question_bank.py          # valida, equilibra y genera
    python tools/build_question_bank.py --check  # solo valida (falla si hay que regenerar)

Archivos generados (raíz del proyecto):
    oodb-questions.json      Español, con nivel/categoría (self-test-app)
    oodb-questions-en.json   Inglés,  con nivel/categoría (self-test-app)
    quiz-es.json             Español, con sección/categoría (quiz.py, quiz-win.py)
    quiz-en.json             Inglés,  con sección/categoría (quiz.py, quiz-win.py)
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "question-bank.json"
LETTERS = "abcd"
LANGS = ("es", "en")
LEVELS = {"es": ["Básico", "Intermedio", "Avanzado"], "en": ["Basic", "Intermediate", "Advanced"]}
SECTION = {"es": "Nivel {level}", "en": "{level} level"}


def validate(bank: list[dict]) -> list[str]:
    errors = []
    ids = [q["id"] for q in bank]
    if ids != list(range(1, len(bank) + 1)):
        errors.append("Los id deben ser consecutivos desde 1.")
    for q in bank:
        qid = q["id"]
        for field in ("level", "category", "question", "options", "explanation"):
            for lang in LANGS:
                if not q.get(field, {}).get(lang):
                    errors.append(f"#{qid}: falta {field}.{lang}")
        for lang in LANGS:
            opts = q["options"].get(lang, [])
            if len(opts) != 4:
                errors.append(f"#{qid}: options.{lang} debe tener 4 opciones")
            if len(set(opts)) != len(opts):
                errors.append(f"#{qid}: options.{lang} tiene opciones repetidas")
        if q["level"]["es"] not in LEVELS["es"]:
            errors.append(f"#{qid}: nivel desconocido {q['level']['es']!r}")
        if q.get("answer") not in LETTERS:
            errors.append(f"#{qid}: answer debe ser a, b, c o d")
    return errors


def balance(bank: list[dict]) -> bool:
    """Coloca la respuesta correcta del reactivo i en la posición (i-1) % 4."""
    changed = False
    for q in bank:
        current = LETTERS.index(q["answer"])
        target = (q["id"] - 1) % 4
        if current == target:
            continue
        for lang in LANGS:
            opts = q["options"][lang]
            correct = opts.pop(current)
            opts.insert(target, correct)
        q["answer"] = LETTERS[target]
        changed = True
    return changed


def derive(bank: list[dict], lang: str, style: str) -> list[dict]:
    out = []
    for q in bank:
        item = {"id": q["id"]}
        if style == "self-test":
            item["level"] = q["level"][lang]
        else:
            item["section"] = SECTION[lang].format(level=q["level"][lang])
        item.update(
            category=q["category"][lang],
            lesson=q["lesson"],
            question=q["question"][lang],
            options=q["options"][lang],
            answer=q["answer"],
            explanation=q["explanation"][lang],
        )
        out.append(item)
    return out


def dump(path: Path, data) -> str:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return text


def main() -> int:
    check_only = "--check" in sys.argv
    bank = json.loads(MASTER.read_text(encoding="utf-8"))

    errors = validate(bank)
    if errors:
        print("Errores en el banco de reactivos:")
        print("\n".join(f"  - {e}" for e in errors))
        return 1

    changed = balance(bank)
    if check_only and changed:
        print("El banco no está equilibrado: ejecuta python tools/build_question_bank.py")
        return 1
    if changed:
        dump(MASTER, bank)

    if not check_only:
        dump(ROOT / "oodb-questions.json", derive(bank, "es", "self-test"))
        dump(ROOT / "oodb-questions-en.json", derive(bank, "en", "self-test"))
        dump(ROOT / "quiz-es.json", derive(bank, "es", "quiz"))
        dump(ROOT / "quiz-en.json", derive(bank, "en", "quiz"))

    levels = Counter(q["level"]["es"] for q in bank)
    answers = Counter(q["answer"] for q in bank)
    print(f"Reactivos: {len(bank)}  |  Niveles: {dict(levels)}  |  Respuestas: {dict(sorted(answers.items()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
