#!/usr/bin/env python3
"""Object-Oriented Databases - Console Quiz Simulator."""

import json
import random
import os
from typing import LiteralString

import matplotlib.pyplot as plt

# Optional: YAML config support
try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except Exception:
    YAML_AVAILABLE = False

BASE_DIR: str | bytes | LiteralString = os.path.dirname(__file__)
QUESTIONS_FILE_NAME = os.environ.get('QUESTIONS_FILE_NAME')
QUESTIONS_FILE = os.path.join(BASE_DIR, QUESTIONS_FILE_NAME) if QUESTIONS_FILE_NAME \
    else os.path.join(BASE_DIR, '..', 'oodb-questions.json')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.yml')
TEST_TITLE = 'Cuestionario de Bases de Datos Orientadas a Objetos (Consola)'

PASS_THRESHOLD = 0.8
MAX_QUESTIONS = 60


def load_config():
    global PASS_THRESHOLD, MAX_QUESTIONS
    if not os.path.exists(CONFIG_FILE):
        return
    try:
        if YAML_AVAILABLE:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or ':' not in line:
                        continue
                    key, val = line.split(':', 1)
                    key = key.strip()
                    val = val.strip().strip('"\'')
                    try:
                        if '.' in val:
                            cast_val = float(val)
                        else:
                            cast_val = int(val)
                        data[key] = cast_val
                    except Exception:
                        data[key] = val
        if isinstance(data, dict):
            if 'pass_threshold' in data and data['pass_threshold'] is not None:
                PASS_THRESHOLD = float(data['pass_threshold'])
            if 'max_questions' in data and data['max_questions'] is not None:
                MAX_QUESTIONS = int(data['max_questions'])
    except Exception:
        pass


def load_questions():
    """Load questions from JSON and return a random subset up to the configured maximum.

    - If the JSON contains more than MAX_QUESTIONS, pick MAX_QUESTIONS unique questions at random.
    - If it contains MAX_QUESTIONS or fewer, return them all.
    """
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    if len(questions) > MAX_QUESTIONS:
        questions = random.sample(questions, k=MAX_QUESTIONS)
    return questions


def ask_question(q):
    level = q.get('level', '')
    category = q.get('category', '')
    print(f"\nPregunta {q['id']} [{level} - {category}]: {q['question']}")
    for idx, opt in enumerate(q['options']):
        print(f"  {chr(97 + idx)}. {opt}")
    user_ans = input("Tu respuesta (a, b, c, d): ").strip().lower()
    correct = user_ans == q['answer']
    if correct:
        print("✅ ¡Correcto!")
    else:
        print(f"❌ Incorrecto. La respuesta correcta era '{q['answer']}'.")
    print(f"Explicación: {q['explanation']}\n")
    return correct


def show_results(correct_count, total):
    incorrect = total - correct_count
    labels = ['Correctas', 'Incorrectas']
    values = [correct_count, incorrect]
    colors = ['#4caf50', '#f44336']
    plt.bar(labels, values, color=colors)
    plt.title('Resultados del Test de Bases de Datos Orientadas a Objetos')
    plt.ylabel('Cantidad de respuestas')
    plt.ylim(0, total)
    plt.text(0, correct_count + 0.1, str(correct_count), ha='center')
    plt.text(1, incorrect + 0.1, str(incorrect), ha='center')
    plt.show()
    porcentaje = correct_count / total
    print(f"\nRespuestas correctas: {correct_count}/{total} ({porcentaje * 100:.1f}%)")
    if porcentaje >= PASS_THRESHOLD:
        print("\n🎉 ¡Aprobaste el test de bases de datos orientadas a objetos!")
    else:
        print("\n❌ No aprobaste. ¡Sigue practicando!")


def main():
    load_config()
    print(f"=== {TEST_TITLE} ===")

    questions = load_questions()
    random.shuffle(questions)
    correct = 0
    for q in questions:
        if ask_question(q):
            correct += 1
    show_results(correct, len(questions))


if __name__ == '__main__':
    main()
