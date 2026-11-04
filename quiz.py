"""
OODB Quiz - Object-Oriented Databases
Supports English and Spanish (Mexican)
"""

import json
import os
import sys
import random
import textwrap
from pathlib import Path

# ──────────────────────────────────────────────
# Attempt to import matplotlib (optional)
# ──────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("TkAgg")          # works on Windows without extra setup
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ──────────────────────────────────────────────
# UI strings
# ──────────────────────────────────────────────
UI = {
    "es": {
        "welcome":        "╔══════════════════════════════════════════════════════════╗\n"
                          "║   CUESTIONARIO: BASES DE DATOS ORIENTADAS A OBJETOS      ║\n"
                          "╚══════════════════════════════════════════════════════════╝",
        "lang_prompt":    "\nSelecciona el idioma / Select language:\n  [1] Español\n  [2] English\n\nOpción: ",
        "start_prompt":   "\n¿Deseas responder todas las preguntas o un número específico?\n"
                          "  [A] Todas ({total})\n  [N] Elegir cantidad\n\nOpción: ",
        "how_many":       "¿Cuántas preguntas? (1-{total}): ",
        "shuffle":        "\n¿Mezclar el orden de las preguntas? [S/N]: ",
        "question_hdr":   "\n─── Pregunta {num}/{total}  ·  Categoría: {cat} ───",
        "options_hint":   "(escribe A, B, C o D y presiona Enter)",
        "answer_prompt":  "Tu respuesta: ",
        "correct":        "✔  ¡Correcto!",
        "wrong":          "✘  Incorrecto. La respuesta correcta es: {letter}) {text}",
        "explanation":    "Explicación:\n{exp}",
        "section_break":  "\n═══  {section}  ═══",
        "results_hdr":    "\n╔══════════════════════════════════════════════════════════╗\n"
                          "║                    RESULTADO FINAL                       ║\n"
                          "╚══════════════════════════════════════════════════════════╝",
        "score_line":     "  Aciertos : {correct} / {total}",
        "pct_line":       "  Porcentaje: {pct:.1f}%",
        "pass_msg":       "  Estado   : ✔  APROBADO  (≥ 80%)",
        "fail_msg":       "  Estado   : ✘  REPROBADO (<  80%)",
        "chart_title":    "Resultado del Cuestionario",
        "chart_correct":  "Correctas",
        "chart_wrong":    "Incorrectas",
        "chart_pass":     "APROBADO ✔",
        "chart_fail":     "REPROBADO ✘",
        "chart_threshold":"Mínimo aprobatorio (80%)",
        "no_chart":       "\n(matplotlib no instalado — no se puede mostrar gráfica)",
        "press_enter":    "\nPresiona Enter para continuar...",
        "invalid":        "  ⚠  Opción inválida, intenta de nuevo.",
        "goodbye":        "\n¡Gracias por participar! Hasta pronto.\n",
    },
    "en": {
        "welcome":        "╔══════════════════════════════════════════════════════════╗\n"
                          "║   QUIZ: OBJECT-ORIENTED DATABASES                        ║\n"
                          "╚══════════════════════════════════════════════════════════╝",
        "lang_prompt":    "\nSelecciona el idioma / Select language:\n  [1] Español\n  [2] English\n\nOption: ",
        "start_prompt":   "\nAnswer all questions or a specific number?\n"
                          "  [A] All ({total})\n  [N] Choose number\n\nOption: ",
        "how_many":       "How many questions? (1-{total}): ",
        "shuffle":        "\nShuffle question order? [Y/N]: ",
        "question_hdr":   "\n─── Question {num}/{total}  ·  Category: {cat} ───",
        "options_hint":   "(type A, B, C or D and press Enter)",
        "answer_prompt":  "Your answer: ",
        "correct":        "✔  Correct!",
        "wrong":          "✘  Wrong. The correct answer was: {letter}) {text}",
        "explanation":    "Explanation:\n{exp}",
        "section_break":  "\n═══  {section}  ═══",
        "results_hdr":    "\n╔══════════════════════════════════════════════════════════╗\n"
                          "║                      FINAL RESULT                        ║\n"
                          "╚══════════════════════════════════════════════════════════╝",
        "score_line":     "  Correct  : {correct} / {total}",
        "pct_line":       "  Score    : {pct:.1f}%",
        "pass_msg":       "  Status   : ✔  PASSED  (≥ 80%)",
        "fail_msg":       "  Status   : ✘  FAILED  (<  80%)",
        "chart_title":    "Quiz Result",
        "chart_correct":  "Correct",
        "chart_wrong":    "Wrong",
        "chart_pass":     "PASSED ✔",
        "chart_fail":     "FAILED ✘",
        "chart_threshold":"Passing threshold (80%)",
        "no_chart":       "\n(matplotlib not installed — cannot display chart)",
        "press_enter":    "\nPress Enter to continue...",
        "invalid":        "  ⚠  Invalid option, please try again.",
        "goodbye":        "\nThank you for playing! See you next time.\n",
    },
}

LETTERS = ["A", "B", "C", "D"]
ANSWER_MAP = {"a": 0, "b": 1, "c": 2, "d": 3}
PASS_THRESHOLD = 80.0

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def wrap(text: str, width: int = 78, indent: str = "  ") -> str:
    """Wrap a long string for the terminal."""
    return textwrap.fill(text, width=width, initial_indent=indent,
                         subsequent_indent=indent)


def ask(prompt: str, valid: list[str]) -> str:
    """Ask until the user gives a valid answer (case-insensitive)."""
    while True:
        ans = input(prompt).strip().upper()
        if ans in [v.upper() for v in valid]:
            return ans
        print("  ⚠  Invalid option.")


def load_questions(lang: str, base_dir: Path) -> list:
    filename = "quiz-es.json" if lang == "es" else "quiz-en.json"
    path = base_dir / filename
    if not path.exists():
        print(f"\n  ERROR: File not found: {path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────
# Chart
# ──────────────────────────────────────────────

def show_chart(correct: int, total: int, lang: str):
    t = UI[lang]
    if not MATPLOTLIB_AVAILABLE:
        print(t["no_chart"])
        return

    wrong = total - correct
    pct = (correct / total) * 100 if total else 0
    passed = pct >= PASS_THRESHOLD

    # ── colour palette ──────────────────────
    c_correct = "#2ecc71"
    c_wrong   = "#e74c3c"
    c_bar_ok  = "#27ae60"
    c_bar_fail= "#c0392b"
    c_thresh  = "#f39c12"
    bg        = "#1e1e2e"
    fg        = "#cdd6f4"

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    fig.patch.set_facecolor(bg)
    status_label = t["chart_pass"] if passed else t["chart_fail"]
    fig.suptitle(f"{t['chart_title']}  —  {status_label}",
                 color=fg, fontsize=15, fontweight="bold", y=1.01)

    # ── LEFT: pie chart ─────────────────────
    ax1 = axes[0]
    ax1.set_facecolor(bg)
    labels  = [t["chart_correct"], t["chart_wrong"]]
    sizes   = [correct, wrong]
    colors  = [c_correct, c_wrong]
    explode = (0.05, 0)

    if wrong == 0:
        sizes   = [correct, 0.001]   # avoid empty-slice matplotlib quirk
        explode = (0.05, 0)

    wedges, texts, autotexts = ax1.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct="%1.1f%%", startangle=90,
        textprops={"color": fg, "fontsize": 11},
    )
    for at in autotexts:
        at.set_color(bg)
        at.set_fontweight("bold")
    ax1.set_title(f"{correct}/{total}", color=fg, fontsize=13, pad=10)

    # ── RIGHT: horizontal bar chart ─────────
    ax2 = axes[1]
    ax2.set_facecolor(bg)
    ax2.tick_params(colors=fg)
    for spine in ax2.spines.values():
        spine.set_edgecolor("#444466")

    bar_color = c_bar_ok if passed else c_bar_fail
    bar = ax2.barh([" "], [pct], color=bar_color, height=0.45,
                   zorder=3, edgecolor="none")
    ax2.barh([" "], [100], color="#2a2a3e", height=0.45, zorder=2)

    # threshold line
    ax2.axvline(PASS_THRESHOLD, color=c_thresh, linewidth=2,
                linestyle="--", zorder=4, label=t["chart_threshold"])

    # percentage label inside/outside bar
    lbl_x = pct - 2 if pct > 10 else pct + 2
    ha    = "right" if pct > 10 else "left"
    ax2.text(lbl_x, 0, f"{pct:.1f}%", va="center", ha=ha,
             color="white", fontsize=14, fontweight="bold", zorder=5)

    ax2.set_xlim(0, 105)
    ax2.set_xlabel("%", color=fg, fontsize=11)
    ax2.set_title(status_label,
                  color=c_bar_ok if passed else c_bar_fail,
                  fontsize=13, fontweight="bold")
    ax2.xaxis.label.set_color(fg)
    ax2.tick_params(axis="x", colors=fg)
    ax2.tick_params(axis="y", colors=fg)
    ax2.legend(facecolor="#2a2a3e", labelcolor=fg, fontsize=9,
               loc="lower right")
    ax2.grid(axis="x", color="#333355", linestyle=":", zorder=1)

    plt.tight_layout()
    plt.show()


# ──────────────────────────────────────────────
# Quiz logic
# ──────────────────────────────────────────────

def run_quiz(questions: list, lang: str):
    t   = UI[lang]
    yes = "S" if lang == "es" else "Y"

    total   = len(questions)
    correct = 0
    wrong_q = []                   # accumulate for optional review
    last_section = None

    for idx, q in enumerate(questions, start=1):
        # ── section banner ───────────────────
        section = q.get("section", "")
        if section != last_section:
            print(t["section_break"].format(section=section))
            last_section = section

        # ── question header ──────────────────
        print(t["question_hdr"].format(num=idx, total=total,
                                       cat=q.get("category", "")))
        print()
        print(wrap(q["question"], indent="  "))
        print()

        # ── options ──────────────────────────
        for i, opt in enumerate(q["options"]):
            print(f"  {LETTERS[i]}) {opt}")
        print()
        print(f"  {t['options_hint']}")

        # ── get answer ───────────────────────
        raw = input(f"  {t['answer_prompt']}").strip().upper()
        while raw not in LETTERS:
            print(t["invalid"])
            raw = input(f"  {t['answer_prompt']}").strip().upper()

        user_idx    = LETTERS.index(raw)
        correct_idx = ANSWER_MAP.get(q["answer"].lower(), 0)

        if user_idx == correct_idx:
            correct += 1
            print(f"\n  {t['correct']}")
        else:
            correct_letter = LETTERS[correct_idx]
            correct_text   = q["options"][correct_idx]
            print(f"\n  {t['wrong'].format(letter=correct_letter, text=correct_text)}")
            print()
            exp_wrapped = textwrap.fill(
                q.get("explanation", ""),
                width=76,
                initial_indent="  ",
                subsequent_indent="  ",
            )
            print(f"  {t['explanation'].split(chr(10))[0]}")
            print(exp_wrapped)
            wrong_q.append(q)

        input(t["press_enter"])
        clear()

    return correct, wrong_q


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def main():
    base_dir = Path(__file__).parent

    clear()
    # language selection (shown before we know the lang)
    print(UI["es"]["welcome"])
    choice = ask(UI["es"]["lang_prompt"], ["1", "2"])
    lang   = "es" if choice == "1" else "en"
    t      = UI[lang]

    clear()
    print(t["welcome"])

    # load questions
    questions = load_questions(lang, base_dir)
    total_available = len(questions)

    # how many questions
    yes_key = "S" if lang == "es" else "Y"
    mode    = ask(t["start_prompt"].format(total=total_available), ["A", "N"])
    if mode == "N":
        while True:
            try:
                n = int(input(t["how_many"].format(total=total_available)))
                if 1 <= n <= total_available:
                    questions = questions[:n]
                    break
                print(t["invalid"])
            except ValueError:
                print(t["invalid"])

    # shuffle
    shuf = ask(t["shuffle"], [yes_key, "N"])
    if shuf == yes_key:
        random.shuffle(questions)

    clear()
    print(t["welcome"])

    # ── run ──────────────────────────────────
    correct, _ = run_quiz(questions, lang)
    total       = len(questions)
    pct         = (correct / total * 100) if total else 0
    passed      = pct >= PASS_THRESHOLD

    # ── results ──────────────────────────────
    clear()
    print(t["results_hdr"])
    print()
    print(t["score_line"].format(correct=correct, total=total))
    print(t["pct_line"].format(pct=pct))
    print()
    print(t["pass_msg"] if passed else t["fail_msg"])
    print()

    # ── chart ────────────────────────────────
    show_chart(correct, total, lang)

    print(t["goodbye"])


if __name__ == "__main__":
    main()
