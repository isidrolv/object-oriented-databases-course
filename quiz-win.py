"""
OODB Quiz - Object-Oriented Databases  (Windows GUI)
Supports English and Spanish (Mexican)
"""

import json
import sys
import random
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# ── Windows DPI awareness ──────────────────────────────────────────────────────
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ── matplotlib (optional, for results chart) ──────────────────────────────────
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
# UI strings  (mirrors quiz.py)
# ══════════════════════════════════════════════════════════════════════════════
UI = {
    "es": {
        "title":           "Cuestionario de BDOO",
        "welcome_title":   "CUESTIONARIO DE BASES DE DATOS ORIENTADAS A OBJETOS",
        "lang_prompt":     "Selecciona el idioma:",
        "start_title":     "Configuración del Cuestionario",
        "all_questions":   "Todas las preguntas ({total})",
        "choose_number":   "Elegir cantidad:",
        "shuffle_lbl":     "¿Mezclar el orden de las preguntas?",
        "start_btn":       "Comenzar",
        "confirm_btn":     "Confirmar",
        "question_hdr":    "Pregunta {num} de {total}",
        "category_lbl":    "Categoría: {cat}",
        "section_lbl":     "Sección: {section}",
        "next_btn":        "Siguiente →",
        "correct":         "✔  ¡Correcto!",
        "wrong":           "✘  Incorrecto. La respuesta correcta es: {letter}) {text}",
        "explanation_lbl": "Explicación:",
        "results_title":   "RESULTADO FINAL",
        "score_line":      "Aciertos: {correct} / {total}",
        "pct_line":        "Porcentaje: {pct:.1f}%",
        "pass_msg":        "✔  APROBADO  (≥ 80%)",
        "fail_msg":        "✘  REPROBADO (<  80%)",
        "chart_title":     "Resultado del Cuestionario",
        "chart_correct":   "Correctas",
        "chart_wrong":     "Incorrectas",
        "chart_pass":      "APROBADO ✔",
        "chart_fail":      "REPROBADO ✘",
        "chart_threshold": "Mínimo aprobatorio (80%)",
        "play_again":      "Jugar de nuevo",
        "exit_btn":        "Salir",
        "invalid":         "⚠  Por favor selecciona una opción (A, B, C o D).",
        "no_chart":        "(matplotlib no instalado — no se puede mostrar gráfica)",
    },
    "en": {
        "title":           "OODB Quiz",
        "welcome_title":   "OBJECT-ORIENTED DATABASES QUIZ",
        "lang_prompt":     "Select language:",
        "start_title":     "Quiz Setup",
        "all_questions":   "All questions ({total})",
        "choose_number":   "Choose number:",
        "shuffle_lbl":     "Shuffle question order?",
        "start_btn":       "Start",
        "confirm_btn":     "Confirm",
        "question_hdr":    "Question {num} of {total}",
        "category_lbl":    "Category: {cat}",
        "section_lbl":     "Section: {section}",
        "next_btn":        "Next →",
        "correct":         "✔  Correct!",
        "wrong":           "✘  Wrong. The correct answer was: {letter}) {text}",
        "explanation_lbl": "Explanation:",
        "results_title":   "FINAL RESULT",
        "score_line":      "Correct: {correct} / {total}",
        "pct_line":        "Score: {pct:.1f}%",
        "pass_msg":        "✔  PASSED  (≥ 80%)",
        "fail_msg":        "✘  FAILED  (<  80%)",
        "chart_title":     "Quiz Result",
        "chart_correct":   "Correct",
        "chart_wrong":     "Wrong",
        "chart_pass":      "PASSED ✔",
        "chart_fail":      "FAILED ✘",
        "chart_threshold": "Passing threshold (80%)",
        "play_again":      "Play again",
        "exit_btn":        "Exit",
        "invalid":         "⚠  Please select an option (A, B, C or D).",
        "no_chart":        "(matplotlib not installed — cannot display chart)",
    },
}

LETTERS        = ["A", "B", "C", "D"]
ANSWER_MAP     = {"a": 0, "b": 1, "c": 2, "d": 3}
PASS_THRESHOLD = 80.0

# ── Colour palette ─────────────────────────────────────────────────────────────
BG      = "#1e1e2e"
FG      = "#cdd6f4"
ACCENT  = "#89b4fa"
CORRECT = "#2ecc71"
WRONG   = "#e74c3c"
PANEL   = "#181825"
BTN_BG  = "#313244"
BTN_FG  = "#cdd6f4"


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_questions(lang: str, base_dir: Path) -> list:
    filename = "quiz-es.json" if lang == "es" else "quiz-en.json"
    path = base_dir / filename
    if not path.exists():
        messagebox.showerror("Error", f"File not found:\n{path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════════
# Application root
# ══════════════════════════════════════════════════════════════════════════════

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OODB Quiz")
        self.configure(bg=BG)
        self.geometry("960x700")
        self.minsize(720, 520)
        self._center()

        self.base_dir  = Path(__file__).parent
        self.lang      = "es"
        self.questions = []
        self.current_q = 0
        self.correct   = 0

        self._frame = None
        self.show_lang_screen()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w,  h  = self.winfo_width(),       self.winfo_height()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── screen navigation ─────────────────────────────────────────────────────

    def _switch(self, frame_cls, *args, **kwargs):
        if self._frame:
            self._frame.destroy()
        self._frame = frame_cls(self, *args, **kwargs)
        self._frame.pack(fill="both", expand=True)

    def show_lang_screen(self):
        self._switch(LangScreen)

    def show_setup_screen(self):
        self._switch(SetupScreen)

    def show_quiz_screen(self):
        self.current_q = 0
        self.correct   = 0
        self._switch(QuizScreen)

    def show_results_screen(self):
        self._switch(ResultsScreen)


# ══════════════════════════════════════════════════════════════════════════════
# Base frame helpers
# ══════════════════════════════════════════════════════════════════════════════

class BaseFrame(tk.Frame):
    def __init__(self, master: QuizApp):
        super().__init__(master, bg=BG)

    def add_header(self, text: str, size: int = 15, color: str = ACCENT) -> tk.Label:
        lbl = tk.Label(self, text=text, bg=BG, fg=color,
                       font=("Segoe UI", size, "bold"), wraplength=880,
                       justify="center")
        lbl.pack(pady=(24, 6))
        return lbl

    def add_separator(self):
        tk.Frame(self, height=1, bg="#444466").pack(fill="x", padx=28, pady=6)

    @staticmethod
    def make_button(parent, text: str, command, width: int = 18,
                    bg: str = BTN_BG, fg: str = BTN_FG) -> tk.Button:
        return tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=ACCENT, activeforeground=BG,
            font=("Segoe UI", 11), relief="flat",
            padx=14, pady=7, width=width, cursor="hand2",
        )


# ══════════════════════════════════════════════════════════════════════════════
# Screen 1 — Language selection
# ══════════════════════════════════════════════════════════════════════════════

class LangScreen(BaseFrame):
    def __init__(self, master: QuizApp):
        super().__init__(master)
        self.app = master

        self.add_header(
            "OBJECT-ORIENTED DATABASES QUIZ\nCUESTIONARIO DE BASES DE DATOS ORIENTADAS A OBJETOS",
            size=17,
        )
        self.add_separator()

        tk.Label(self, text="Selecciona el idioma / Select language:",
                 bg=BG, fg=FG, font=("Segoe UI", 13)).pack(pady=(20, 14))

        row = tk.Frame(self, bg=BG)
        row.pack()
        self.make_button(row, "🇲🇽  Español", lambda: self._pick("es"),
                         width=22).pack(side="left", padx=14)
        self.make_button(row, "🇺🇸  English", lambda: self._pick("en"),
                         width=22).pack(side="left", padx=14)

    def _pick(self, lang: str):
        self.app.lang = lang
        self.app.title(UI[lang]["title"])
        self.app.show_setup_screen()


# ══════════════════════════════════════════════════════════════════════════════
# Screen 2 — Quiz setup
# ══════════════════════════════════════════════════════════════════════════════

class SetupScreen(BaseFrame):
    def __init__(self, master: QuizApp):
        super().__init__(master)
        self.app = master
        t    = UI[master.lang]

        self._all_q = load_questions(master.lang, master.base_dir)
        total       = len(self._all_q)

        self.add_header(t["welcome_title"])
        self.add_separator()

        tk.Label(self, text=t["start_title"],
                 bg=BG, fg=FG, font=("Segoe UI", 12, "bold")).pack(pady=(10, 8))

        # ── question count ────────────────────────────────────────────────────
        self._mode = tk.StringVar(value="A")

        outer = tk.Frame(self, bg=BG)
        outer.pack(pady=4)

        tk.Radiobutton(
            outer, text=t["all_questions"].format(total=total),
            variable=self._mode, value="A",
            bg=BG, fg=FG, selectcolor=PANEL,
            activebackground=BG, activeforeground=ACCENT,
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=3)

        row_n = tk.Frame(outer, bg=BG)
        row_n.pack(anchor="w", pady=3)
        tk.Radiobutton(
            row_n, text=t["choose_number"],
            variable=self._mode, value="N",
            bg=BG, fg=FG, selectcolor=PANEL,
            activebackground=BG, activeforeground=ACCENT,
            font=("Segoe UI", 11),
        ).pack(side="left")
        self._n_var = tk.StringVar(value=str(min(10, total)))
        tk.Spinbox(
            row_n, from_=1, to=total, textvariable=self._n_var,
            width=6, bg=PANEL, fg=FG, buttonbackground=BTN_BG,
            insertbackground=FG, font=("Segoe UI", 11), relief="flat",
        ).pack(side="left", padx=10)

        # ── shuffle ───────────────────────────────────────────────────────────
        self._shuffle = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self, text=t["shuffle_lbl"],
            variable=self._shuffle,
            bg=BG, fg=FG, selectcolor=PANEL,
            activebackground=BG, activeforeground=ACCENT,
            font=("Segoe UI", 11),
        ).pack(pady=(14, 6))

        self.add_separator()

        self.make_button(self, t["start_btn"], self._start,
                         width=16, bg=ACCENT, fg=BG).pack(pady=18)

    def _start(self):
        questions = list(self._all_q)
        if self._mode.get() == "N":
            try:
                n = max(1, min(int(self._n_var.get()), len(questions)))
            except ValueError:
                n = 10
            questions = questions[:n]
        if self._shuffle.get():
            random.shuffle(questions)
        self.app.questions = questions
        self.app.show_quiz_screen()


# ══════════════════════════════════════════════════════════════════════════════
# Screen 3 — Individual question
# ══════════════════════════════════════════════════════════════════════════════

class QuizScreen(BaseFrame):
    def __init__(self, master: QuizApp):
        super().__init__(master)
        self.app = master
        self._build_widgets()
        self._load_question()

    def _build_widgets(self):
        t = UI[self.app.lang]

        # ── top bar ───────────────────────────────────────────────────────────
        top = tk.Frame(self, bg=PANEL, pady=8)
        top.pack(fill="x")

        self._prog_lbl = tk.Label(top, text="", bg=PANEL, fg=ACCENT,
                                  font=("Segoe UI", 12, "bold"))
        self._prog_lbl.pack(side="left", padx=20)

        self._sec_lbl = tk.Label(top, text="", bg=PANEL, fg=FG,
                                 font=("Segoe UI", 10))
        self._sec_lbl.pack(side="right", padx=20)

        self._cat_lbl = tk.Label(top, text="", bg=PANEL, fg=FG,
                                 font=("Segoe UI", 10, "italic"))
        self._cat_lbl.pack(side="right", padx=10)

        # ── progress bar ──────────────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Q.Horizontal.TProgressbar",
                        background=ACCENT, troughcolor=PANEL,
                        bordercolor=PANEL, lightcolor=ACCENT, darkcolor=ACCENT)
        self._pbar = tk.DoubleVar(value=0)
        ttk.Progressbar(self, variable=self._pbar, maximum=100,
                        style="Q.Horizontal.TProgressbar").pack(fill="x")

        # ── question text ─────────────────────────────────────────────────────
        q_wrap = tk.Frame(self, bg=BG, pady=12)
        q_wrap.pack(fill="x", padx=30)
        self._q_lbl = tk.Label(q_wrap, text="", bg=BG, fg=FG,
                               font=("Segoe UI", 12), wraplength=860,
                               justify="left", anchor="w")
        self._q_lbl.pack(fill="x")

        # ── answer options ────────────────────────────────────────────────────
        self._ans_var   = tk.StringVar(value="")
        self._radio_btns = []
        opt_wrap = tk.Frame(self, bg=BG)
        opt_wrap.pack(fill="x", padx=44, pady=4)
        for letter in LETTERS:
            rb = tk.Radiobutton(
                opt_wrap, text="",
                variable=self._ans_var, value=letter,
                bg=BG, fg=FG, selectcolor=PANEL,
                activebackground=BG, activeforeground=ACCENT,
                font=("Segoe UI", 11),
                anchor="w", justify="left", wraplength=800, cursor="hand2",
            )
            rb.pack(fill="x", pady=3, anchor="w")
            self._radio_btns.append(rb)

        # ── feedback ──────────────────────────────────────────────────────────
        self._fb_lbl = tk.Label(self, text="", bg=BG,
                                font=("Segoe UI", 11, "bold"),
                                wraplength=860, justify="left")
        self._fb_lbl.pack(fill="x", padx=44, pady=(8, 0))

        self._exp_lbl = tk.Label(self, text="", bg=BG, fg=FG,
                                 font=("Segoe UI", 10), wraplength=860,
                                 justify="left", anchor="w")
        self._exp_lbl.pack(fill="x", padx=44, pady=(4, 0))

        # ── bottom buttons ────────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(side="bottom", pady=16)

        self._next_btn = self.make_button(
            btn_row, t["next_btn"], self._next, width=14, bg=ACCENT, fg=BG)
        self._submit_btn = self.make_button(
            btn_row, t["confirm_btn"], self._submit, width=18)

        self._submit_btn.pack(side="right", padx=10)
        # next_btn only shown after answer

    def _load_question(self):
        idx   = self.app.current_q
        q     = self.app.questions[idx]
        t     = UI[self.app.lang]
        total = len(self.app.questions)

        self._pbar.set(idx / total * 100)
        self._prog_lbl.config(text=t["question_hdr"].format(num=idx + 1, total=total))
        self._cat_lbl.config(text=t["category_lbl"].format(cat=q.get("category", "")))
        self._sec_lbl.config(text=t["section_lbl"].format(section=q.get("section", "")))

        self._q_lbl.config(text=q["question"])
        self._ans_var.set("")

        # Shuffle option order; store permutation so _submit can resolve the correct answer
        perm = list(range(len(q["options"])))
        random.shuffle(perm)
        self._perm = perm

        for i, rb in enumerate(self._radio_btns):
            rb.config(text=f"{LETTERS[i]})  {q['options'][perm[i]]}",
                      state="normal", fg=FG, selectcolor=PANEL)

        self._fb_lbl.config(text="")
        self._exp_lbl.config(text="")
        self._submit_btn.pack(side="right", padx=10)
        self._next_btn.pack_forget()

    def _submit(self):
        t   = UI[self.app.lang]
        raw = self._ans_var.get()
        if not raw:
            self._fb_lbl.config(text=t["invalid"], fg=WRONG)
            return

        q                    = self.app.questions[self.app.current_q]
        user_idx             = LETTERS.index(raw)
        correct_original_idx = ANSWER_MAP.get(q["answer"].lower(), 0)
        # Find where the correct option ended up after shuffling
        correct_display_idx  = self._perm.index(correct_original_idx)

        for rb in self._radio_btns:
            rb.config(state="disabled")

        if user_idx == correct_display_idx:
            self.app.correct += 1
            self._fb_lbl.config(text=t["correct"], fg=CORRECT)
            self._exp_lbl.config(text="")
        else:
            c_letter = LETTERS[correct_display_idx]
            c_text   = q["options"][correct_original_idx]
            self._fb_lbl.config(
                text=t["wrong"].format(letter=c_letter, text=c_text), fg=WRONG)
            exp = q.get("explanation", "")
            self._exp_lbl.config(text=f"{t['explanation_lbl']} {exp}")

        self._submit_btn.pack_forget()
        self._next_btn.pack(side="right", padx=10)

    def _next(self):
        self.app.current_q += 1
        if self.app.current_q >= len(self.app.questions):
            self.app.show_results_screen()
        else:
            self._load_question()


# ══════════════════════════════════════════════════════════════════════════════
# Screen 4 — Results
# ══════════════════════════════════════════════════════════════════════════════

class ResultsScreen(BaseFrame):
    def __init__(self, master: QuizApp):
        super().__init__(master)
        self.app = master
        t       = UI[master.lang]
        total   = len(master.questions)
        correct = master.correct
        pct     = (correct / total * 100) if total else 0
        passed  = pct >= PASS_THRESHOLD

        self.add_header(t["results_title"])
        self.add_separator()

        # ── score info ────────────────────────────────────────────────────────
        info = tk.Frame(self, bg=BG)
        info.pack(pady=8)
        tk.Label(info, text=t["score_line"].format(correct=correct, total=total),
                 bg=BG, fg=FG, font=("Segoe UI", 14)).pack()
        tk.Label(info, text=t["pct_line"].format(pct=pct),
                 bg=BG, fg=FG, font=("Segoe UI", 14)).pack()

        status_color = CORRECT if passed else WRONG
        status_text  = t["pass_msg"] if passed else t["fail_msg"]
        tk.Label(info, text=status_text, bg=BG, fg=status_color,
                 font=("Segoe UI", 16, "bold")).pack(pady=8)

        self.add_separator()

        # ── chart ─────────────────────────────────────────────────────────────
        if MATPLOTLIB_AVAILABLE:
            self._embed_chart(correct, total, passed, t)
        else:
            tk.Label(self, text=t["no_chart"], bg=BG, fg=FG,
                     font=("Segoe UI", 10, "italic")).pack(pady=10)

        self.add_separator()

        # ── buttons ───────────────────────────────────────────────────────────
        row = tk.Frame(self, bg=BG)
        row.pack(pady=14)
        self.make_button(row, t["play_again"],
                         master.show_lang_screen, width=18,
                         bg=ACCENT, fg=BG).pack(side="left", padx=14)
        self.make_button(row, t["exit_btn"],
                         master.destroy, width=12).pack(side="left", padx=14)

    def _embed_chart(self, correct: int, total: int, passed: bool, t: dict):
        wrong = total - correct
        pct   = (correct / total * 100) if total else 0

        C_OK    = "#2ecc71"
        C_FAIL  = "#e74c3c"
        C_BAR_OK  = "#27ae60"
        C_BAR_FAIL= "#c0392b"
        C_THRESH  = "#f39c12"
        BG_C    = "#1e1e2e"
        FG_C    = "#cdd6f4"

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.0))
        fig.patch.set_facecolor(BG_C)

        # ── Pie ───────────────────────────────────────────────────────────────
        ax1.set_facecolor(BG_C)
        sizes   = [correct, wrong if wrong > 0 else 0.001]
        labels  = [t["chart_correct"], t["chart_wrong"]]
        colors  = [C_OK, C_FAIL]
        _, texts, autotexts = ax1.pie(
            sizes, labels=labels, colors=colors, explode=(0.05, 0),
            autopct="%1.1f%%", startangle=90,
            textprops={"color": FG_C, "fontsize": 9},
        )
        for at in autotexts:
            at.set_color(BG_C)
            at.set_fontweight("bold")
        ax1.set_title(f"{correct}/{total}", color=FG_C, fontsize=11, pad=8)

        # ── Bar ───────────────────────────────────────────────────────────────
        ax2.set_facecolor(BG_C)
        for spine in ax2.spines.values():
            spine.set_edgecolor("#444466")
        ax2.tick_params(colors=FG_C)

        bar_color = C_BAR_OK if passed else C_BAR_FAIL
        ax2.barh([" "], [100],    color="#2a2a3e",  height=0.45, zorder=2)
        ax2.barh([" "], [pct],    color=bar_color,  height=0.45, zorder=3, edgecolor="none")
        ax2.axvline(PASS_THRESHOLD, color=C_THRESH, linewidth=2,
                    linestyle="--", zorder=4, label=t["chart_threshold"])

        lbl_x = pct - 2 if pct > 10 else pct + 2
        ax2.text(lbl_x, 0, f"{pct:.1f}%", va="center",
                 ha="right" if pct > 10 else "left",
                 color="white", fontsize=12, fontweight="bold", zorder=5)

        ax2.set_xlim(0, 105)
        ax2.set_xlabel("%", color=FG_C, fontsize=10)
        status_label = t["chart_pass"] if passed else t["chart_fail"]
        ax2.set_title(status_label,
                      color=C_BAR_OK if passed else C_BAR_FAIL,
                      fontsize=11, fontweight="bold")
        ax2.tick_params(axis="x", colors=FG_C)
        ax2.tick_params(axis="y", colors=FG_C)
        ax2.legend(facecolor="#2a2a3e", labelcolor=FG_C, fontsize=8, loc="lower right")
        ax2.grid(axis="x", color="#333355", linestyle=":", zorder=1)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=20, pady=4)
        plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
