#!/usr/bin/env python3
"""
Object-Oriented Databases - Windows GUI Quiz Simulator
Tkinter-based GUI application for practicing object-oriented database questions.
"""

import json
import random
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

# ─── Constants ───────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.environ.get("QUESTIONS_FILE") or os.path.join(SCRIPT_DIR, "..", "oodb-questions.json")

OPTION_LETTERS = ["a", "b", "c", "d"]

# Color palette
BG_MAIN = "#1a1a2e"
BG_CARD = "#16213e"
BG_HEADER = "#0f3460"
FG_TEXT = "#e0e0e0"
FG_DIM = "#8892b0"
FG_TITLE = "#ffffff"
ACCENT = "#4fc3f7"
GREEN = "#66bb6a"
RED = "#ef5350"
YELLOW = "#ffd54f"
MAGENTA = "#ce93d8"
BTN_BG = "#0f3460"
BTN_HOVER = "#1a5276"
BTN_ACTIVE = "#2980b9"
OPTION_BG = "#1e2a45"
OPTION_SELECTED = "#1a5276"
OPTION_CORRECT = "#1b5e20"
OPTION_WRONG = "#b71c1c"


# ─── Data Loading ────────────────────────────────────────────────────────────
def load_questions():
    if not os.path.exists(JSON_FILE):
        messagebox.showerror("Error", f"No se encontró:\n{JSON_FILE}")
        sys.exit(1)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Normalize array-based options into {a, b, c, d} dicts
    questions = []
    for q in raw:
        opts = {}
        for i, text in enumerate(q.get("options", [])):
            if i < len(OPTION_LETTERS):
                opts[OPTION_LETTERS[i]] = text
        questions.append({
            "id": q["id"],
            "level": q.get("level", "General"),
            "category": q.get("category", "General"),
            "question": q["question"],
            "options": opts,
            "answer": q["answer"],
            "explanation": q.get("explanation", ""),
        })

    # Build metadata dynamically
    levels = sorted(set(q["level"] for q in questions))
    categories = sorted(set(q["category"] for q in questions))
    metadata = {
        "title": "Bases de Datos Orientadas a Objetos",
        "total_questions": len(questions),
        "levels": levels,
        "categories": categories,
    }
    return metadata, questions


# ─── App ─────────────────────────────────────────────────────────────────────
class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.metadata, self.all_questions = load_questions()

        self.title("🗄️ OODB Quiz Simulator")
        self.configure(bg=BG_MAIN)
        self.minsize(900, 680)
        self.geometry("960x720")

        # Try to center
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 960) // 2
        y = (self.winfo_screenheight() - 720) // 2
        self.geometry(f"+{x}+{y}")

        # Fonts
        self.font_title = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.font_subtitle = tkfont.Font(family="Segoe UI", size=11)
        self.font_question = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.font_option = tkfont.Font(family="Segoe UI", size=11)
        self.font_btn = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.font_small = tkfont.Font(family="Segoe UI", size=10)
        self.font_explanation = tkfont.Font(family="Segoe UI", size=14)

        # Quiz state
        self.quiz_questions = []
        self.current_index = 0
        self.score = 0
        self.answered = False
        self.selected_option = tk.StringVar(value="")
        self.results = []  # (q_id, user_ans, correct_ans, is_correct)

        # Configure ttk style
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

        # Container
        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(fill="both", expand=True)

        self.show_home()

    def _configure_styles(self):
        s = self.style
        s.configure("TFrame", background=BG_MAIN)
        s.configure("Card.TFrame", background=BG_CARD)
        s.configure("Header.TFrame", background=BG_HEADER)
        s.configure("TLabel", background=BG_MAIN, foreground=FG_TEXT, font=self.font_small)
        s.configure("Title.TLabel", background=BG_HEADER, foreground=FG_TITLE, font=self.font_title)
        s.configure("Subtitle.TLabel", background=BG_HEADER, foreground=FG_DIM, font=self.font_subtitle)
        s.configure("Question.TLabel", background=BG_CARD, foreground=FG_TITLE, font=self.font_question)
        s.configure("Meta.TLabel", background=BG_CARD, foreground=MAGENTA, font=self.font_small)
        s.configure("Score.TLabel", background=BG_CARD, foreground=ACCENT, font=self.font_subtitle)
        s.configure("Correct.TLabel", background=BG_CARD, foreground=GREEN, font=self.font_option)
        s.configure("Wrong.TLabel", background=BG_CARD, foreground=RED, font=self.font_option)

        s.configure("Accent.TButton", background=ACCENT, foreground="#000", font=self.font_btn,
                     padding=(20, 10))
        s.map("Accent.TButton",
              background=[("active", BTN_ACTIVE), ("disabled", "#555")])

        s.configure("Menu.TButton", background=BTN_BG, foreground=FG_TEXT, font=self.font_btn,
                     padding=(20, 12), borderwidth=0)
        s.map("Menu.TButton",
              background=[("active", BTN_HOVER)])

        s.configure("Nav.TButton", background=BTN_BG, foreground=FG_TEXT, font=self.font_small,
                     padding=(14, 8))
        s.map("Nav.TButton", background=[("active", BTN_HOVER)])

    # ─── Page Management ─────────────────────────────────────────────────
    def clear_container(self):
        # Unbind any global mousewheel handler before destroying widgets
        self.unbind_all("<MouseWheel>")
        for w in self.container.winfo_children():
            w.destroy()

    # ─── HOME SCREEN ─────────────────────────────────────────────────────
    def show_home(self):
        self.clear_container()

        # Header
        header = ttk.Frame(self.container, style="Header.TFrame")
        header.pack(fill="x", padx=0, pady=0)
        header_inner = ttk.Frame(header, style="Header.TFrame")
        header_inner.pack(padx=30, pady=20)

        ttk.Label(header_inner, text="🗄️  Object-Oriented Databases Quiz", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header_inner, text="Bases de Datos Orientadas a Objetos — Simulador de Examen",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

        # Stats
        stats_frame = ttk.Frame(self.container, style="Card.TFrame")
        stats_frame.pack(fill="x", padx=30, pady=(20, 10))
        stats_inner = ttk.Frame(stats_frame, style="Card.TFrame")
        stats_inner.pack(padx=20, pady=15)

        meta = self.metadata
        for text in [
            f"📋  {meta['total_questions']} preguntas disponibles",
            f"🪜  {len(meta['levels'])} niveles de dificultad",
            f"🏷️  {len(meta['categories'])} categorías cubiertas",
        ]:
            ttk.Label(stats_inner, text=text, style="TLabel",
                      background=BG_CARD).pack(anchor="w", pady=2)

        # Menu buttons
        total = meta["total_questions"]
        menu_frame = ttk.Frame(self.container)
        menu_frame.pack(fill="x", padx=30, pady=10)

        buttons = [
            (f"▶  Quiz Completo ({total} preguntas)", lambda: self.start_quiz(self.all_questions)),
            ("⚡  Quiz Rápido (10 aleatorias)", lambda: self.start_quiz(
                random.sample(self.all_questions, min(10, total)))),
            ("🎯  Quiz Personalizado...", self.show_custom_dialog),
            ("🪜  Filtrar por Nivel...", self.show_level_picker),
            ("🏷️  Filtrar por Categoría...", self.show_category_picker),
            ("📖  Modo Estudio", lambda: self.start_study(self.all_questions)),
        ]

        for text, cmd in buttons:
            btn = ttk.Button(menu_frame, text=text, command=cmd, style="Menu.TButton")
            btn.pack(fill="x", pady=3)

        # Footer
        ttk.Label(self.container, text="Curso neuro-optimizado de BDOO en 90 días",
                  foreground=FG_DIM).pack(side="bottom", pady=10)

    # ─── Dialogs ─────────────────────────────────────────────────────────
    def show_custom_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Quiz Personalizado")
        dialog.configure(bg=BG_CARD)
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 180) // 2
        dialog.geometry(f"+{x}+{y}")

        ttk.Label(dialog, text="¿Cuántas preguntas?", background=BG_CARD,
                  foreground=FG_TITLE, font=self.font_question).pack(pady=(20, 10))

        var = tk.StringVar(value="15")
        spin = tk.Spinbox(dialog, from_=1, to=len(self.all_questions), textvariable=var,
                          width=8, font=self.font_option, justify="center",
                          bg=OPTION_BG, fg=FG_TEXT, insertbackground=FG_TEXT)
        spin.pack(pady=5)

        def start():
            try:
                n = int(var.get())
                n = max(1, min(n, len(self.all_questions)))
            except ValueError:
                n = 10
            dialog.destroy()
            self.start_quiz(random.sample(self.all_questions, n))

        ttk.Button(dialog, text="Iniciar", command=start, style="Accent.TButton").pack(pady=15)

    def show_level_picker(self):
        levels = sorted(set(q["level"] for q in self.all_questions))
        self._show_picker("Selecciona un Nivel", levels,
                          lambda lvl: self.start_quiz(
                              [q for q in self.all_questions if q["level"] == lvl]),
                          count_fn=lambda item: sum(1 for q in self.all_questions if q.get("level") == item))

    def show_category_picker(self):
        categories = sorted(set(q["category"] for q in self.all_questions))
        self._show_picker("Selecciona una Categoría", categories,
                          lambda cat: self.start_quiz(
                              [q for q in self.all_questions if q["category"] == cat]),
                          count_fn=lambda item: sum(1 for q in self.all_questions if q.get("category") == item))

    def _show_picker(self, title, items, callback, count_fn):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=BG_CARD)
        dialog.geometry("420x500")
        dialog.resizable(False, True)
        dialog.transient(self)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 500) // 2
        dialog.geometry(f"+{x}+{y}")

        ttk.Label(dialog, text=title, background=BG_CARD,
                  foreground=FG_TITLE, font=self.font_question).pack(pady=(15, 10))

        # Scrollable list
        canvas = tk.Canvas(dialog, bg=BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Card.TFrame")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=5)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

        for item in items:
            count = count_fn(item)
            btn_text = f"{item}  ({count} preguntas)"

            def make_cb(i=item):
                def cb():
                    dialog.destroy()
                    callback(i)
                return cb

            btn = ttk.Button(scroll_frame, text=btn_text, command=make_cb(), style="Menu.TButton")
            btn.pack(fill="x", padx=5, pady=2)

    # ─── QUIZ SCREEN ─────────────────────────────────────────────────────
    def start_quiz(self, questions):
        self.quiz_questions = list(questions)
        random.shuffle(self.quiz_questions)
        self.current_index = 0
        self.score = 0
        self.answered = False
        self.results = []
        self.selected_option.set("")
        self.show_question()

    def show_question(self):
        self.clear_container()
        self.answered = False
        self.selected_option.set("")

        q = self.quiz_questions[self.current_index]
        total = len(self.quiz_questions)
        idx = self.current_index + 1

        # ── Top bar ──
        top = ttk.Frame(self.container, style="Header.TFrame")
        top.pack(fill="x")
        top_inner = ttk.Frame(top, style="Header.TFrame")
        top_inner.pack(fill="x", padx=20, pady=10)

        ttk.Label(top_inner, text=f"Pregunta {idx} de {total}",
                  background=BG_HEADER, foreground=FG_TITLE,
                  font=self.font_subtitle).pack(side="left")

        pct = (self.score / max(idx - 1, 1)) * 100 if idx > 1 else 0
        score_color = GREEN if pct >= 70 else YELLOW if pct >= 50 else RED
        score_text = f"✅ {self.score}/{idx - 1}" if idx > 1 else "✅ 0/0"
        ttk.Label(top_inner, text=score_text, background=BG_HEADER,
                  foreground=score_color, font=self.font_subtitle).pack(side="right")

        # ── Progress bar ──
        progress_bg = tk.Frame(self.container, bg="#333", height=4)
        progress_bg.pack(fill="x")
        progress_fill = tk.Frame(progress_bg, bg=ACCENT, height=4)
        progress_fill.place(relx=0, rely=0, relwidth=idx / total, relheight=1)

        # ── Card ──
        card = ttk.Frame(self.container, style="Card.TFrame")
        card.pack(fill="both", expand=True, padx=25, pady=15)
        card_inner = ttk.Frame(card, style="Card.TFrame")
        card_inner.pack(fill="both", expand=True, padx=20, pady=15)

        # Meta
        meta_text = f"🪜 {q['level']}   🏷️  {q['category']}"
        ttk.Label(card_inner, text=meta_text, style="Meta.TLabel").pack(anchor="w")

        # Question
        q_label = ttk.Label(card_inner, text=q["question"], style="Question.TLabel",
                            wraplength=780)
        q_label.pack(anchor="w", pady=(10, 15))

        # Options
        self.option_frames = {}
        option_keys = sorted(q["options"].keys())
        for key in option_keys:
            opt_frame = tk.Frame(card_inner, bg=OPTION_BG, cursor="hand2",
                                 bd=0, highlightthickness=2, highlightbackground=BG_CARD)
            opt_frame.pack(fill="x", pady=3)

            opt_label = tk.Label(opt_frame, text=f"  {key})  {q['options'][key]}",
                                 bg=OPTION_BG, fg=FG_TEXT, font=self.font_option,
                                 anchor="w", padx=15, pady=10, cursor="hand2",
                                 wraplength=720, justify="left")
            opt_label.pack(fill="x")

            self.option_frames[key] = (opt_frame, opt_label)

            def make_click(k=key):
                def handler(event=None):
                    if not self.answered:
                        self.select_option(k)
                return handler

            opt_frame.bind("<Button-1>", make_click())
            opt_label.bind("<Button-1>", make_click())

        # Explanation area (hidden until answered)
        self.explanation_frame = ttk.Frame(card_inner, style="Card.TFrame")
        self.explanation_label = tk.Label(self.explanation_frame, text="",
                                          bg=BG_CARD, fg=FG_DIM,
                                          font=self.font_explanation,
                                          wraplength=750, justify="left",
                                          anchor="nw")
        self.explanation_label.pack(fill="x", pady=(5, 0))

        # ── Bottom buttons ──
        btn_bar = ttk.Frame(self.container)
        btn_bar.pack(fill="x", padx=25, pady=(0, 15))

        ttk.Button(btn_bar, text="🏠 Menú", command=self.confirm_quit_quiz,
                   style="Nav.TButton").pack(side="left")

        self.btn_confirm = ttk.Button(btn_bar, text="✔ Confirmar",
                                       command=self.confirm_answer,
                                       style="Accent.TButton", state="disabled")
        self.btn_confirm.pack(side="right")

        self.btn_next = ttk.Button(btn_bar, text="Siguiente ▶",
                                    command=self.next_question,
                                    style="Accent.TButton")
        # btn_next is packed after confirming

    def select_option(self, key):
        if self.answered:
            return
        self.selected_option.set(key)

        # Highlight selected, reset others
        for k, (frame, label) in self.option_frames.items():
            if k == key:
                frame.configure(bg=OPTION_SELECTED, highlightbackground=ACCENT)
                label.configure(bg=OPTION_SELECTED)
            else:
                frame.configure(bg=OPTION_BG, highlightbackground=BG_CARD)
                label.configure(bg=OPTION_BG)

        self.btn_confirm.configure(state="normal")

    def confirm_answer(self):
        if self.answered:
            return
        self.answered = True
        self.btn_confirm.pack_forget()

        q = self.quiz_questions[self.current_index]
        user_ans = self.selected_option.get()
        correct_ans = q["answer"]
        is_correct = user_ans == correct_ans

        if is_correct:
            self.score += 1

        self.results.append((q["id"], user_ans, correct_ans, is_correct))

        # Color the options
        for k, (frame, label) in self.option_frames.items():
            if k == correct_ans:
                frame.configure(bg=OPTION_CORRECT, highlightbackground=GREEN)
                label.configure(bg=OPTION_CORRECT, fg="#fff")
            elif k == user_ans and not is_correct:
                frame.configure(bg=OPTION_WRONG, highlightbackground=RED)
                label.configure(bg=OPTION_WRONG, fg="#fff")
            else:
                frame.configure(highlightbackground=BG_CARD)

        # Show result text
        result_text = "✅ ¡Correcto!" if is_correct else f"❌ Incorrecto — respuesta: {correct_ans})"
        result_color = GREEN if is_correct else RED
        ttk.Label(self.explanation_frame, text=result_text, background=BG_CARD,
                  foreground=result_color, font=self.font_option).pack(anchor="w")

        # Show explanation
        self.explanation_label.configure(text=f"💡 {q['explanation']}")
        self.explanation_frame.pack(fill="x", pady=(10, 0))

        # Show next/finish button
        is_last = self.current_index >= len(self.quiz_questions) - 1
        btn_text = "📊 Ver Resultados" if is_last else "Siguiente ▶"
        cmd = self.show_results if is_last else self.next_question
        self.btn_next.configure(text=btn_text, command=cmd)
        self.btn_next.pack(side="right")

    def next_question(self):
        self.current_index += 1
        self.show_question()

    def confirm_quit_quiz(self):
        if messagebox.askyesno("Salir del Quiz", "¿Seguro que quieres volver al menú?\nSe perderá tu progreso."):
            self.show_home()

    # ─── RESULTS SCREEN ──────────────────────────────────────────────────
    def show_results(self):
        self.clear_container()
        total = len(self.quiz_questions)
        pct = (self.score / total * 100) if total > 0 else 0

        # Header
        header = ttk.Frame(self.container, style="Header.TFrame")
        header.pack(fill="x")
        h_inner = ttk.Frame(header, style="Header.TFrame")
        h_inner.pack(padx=30, pady=20)

        ttk.Label(h_inner, text="📊  Resultados Finales", style="Title.TLabel").pack(anchor="w")

        # Score card
        card = ttk.Frame(self.container, style="Card.TFrame")
        card.pack(fill="x", padx=30, pady=15)
        c_inner = ttk.Frame(card, style="Card.TFrame")
        c_inner.pack(padx=25, pady=20)

        score_color = GREEN if pct >= 70 else YELLOW if pct >= 50 else RED

        tk.Label(c_inner, text=f"{self.score} / {total}", bg=BG_CARD,
                 fg=score_color, font=tkfont.Font(family="Segoe UI", size=42, weight="bold")
                 ).pack()
        tk.Label(c_inner, text=f"{pct:.0f}%", bg=BG_CARD, fg=score_color,
                 font=self.font_title).pack()

        # Progress bar
        bar_bg = tk.Frame(c_inner, bg="#333", height=12)
        bar_bg.pack(fill="x", pady=10)
        bar_fill = tk.Frame(bar_bg, bg=score_color, height=12)
        bar_fill.place(relx=0, rely=0, relwidth=pct / 100, relheight=1)

        # Message
        if pct >= 90:
            msg = "🏆 ¡EXCELENTE! Dominas las bases de datos orientadas a objetos como un experto."
        elif pct >= 70:
            msg = "👍 ¡MUY BIEN! Buen conocimiento de bases de datos orientadas a objetos."
        elif pct >= 50:
            msg = "📘 Aprobado, pero hay áreas por mejorar."
        else:
            msg = "📚 Necesitas estudiar más. ¡No te rindas!"

        tk.Label(c_inner, text=msg, bg=BG_CARD, fg=FG_TEXT,
                 font=self.font_question).pack(pady=(10, 0))

        # Incorrect questions
        incorrect = [(qid, ua, ca) for qid, ua, ca, ok in self.results if not ok]
        if incorrect:
            err_frame = ttk.Frame(self.container, style="Card.TFrame")
            err_frame.pack(fill="both", expand=True, padx=30, pady=(0, 15))
            err_inner = ttk.Frame(err_frame, style="Card.TFrame")
            err_inner.pack(fill="both", expand=True, padx=15, pady=10)

            tk.Label(err_inner, text=f"❌ Preguntas incorrectas ({len(incorrect)})",
                     bg=BG_CARD, fg=RED, font=self.font_subtitle, anchor="w"
                     ).pack(fill="x", pady=(0, 5))

            # Scrollable list
            canvas = tk.Canvas(err_inner, bg=BG_CARD, highlightthickness=0)
            sb = ttk.Scrollbar(err_inner, orient="vertical", command=canvas.yview)
            scroll_f = ttk.Frame(canvas, style="Card.TFrame")
            scroll_f.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scroll_f, anchor="nw")
            canvas.configure(yscrollcommand=sb.set)
            canvas.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")

            for qid, user_ans, correct_ans in incorrect:
                q_obj = next((q for q in self.all_questions if q["id"] == qid), None)
                if q_obj:
                    row = tk.Frame(scroll_f, bg=BG_CARD)
                    row.pack(fill="x", pady=2)
                    tk.Label(row, text=f"  #{qid}: {q_obj['question'][:80]}...",
                             bg=BG_CARD, fg=FG_DIM, font=self.font_small,
                             anchor="w").pack(side="left", fill="x", expand=True)
                    tk.Label(row, text=f"Tu: {user_ans}",
                             bg=BG_CARD, fg=RED, font=self.font_small).pack(side="left", padx=5)
                    tk.Label(row, text=f"✓: {correct_ans}",
                             bg=BG_CARD, fg=GREEN, font=self.font_small).pack(side="left", padx=5)

        # Buttons
        btn_bar = ttk.Frame(self.container)
        btn_bar.pack(fill="x", padx=30, pady=(0, 15))

        ttk.Button(btn_bar, text="🏠  Volver al Menú", command=self.show_home,
                   style="Accent.TButton").pack(side="left")

        ttk.Button(btn_bar, text="🔄  Reintentar", style="Nav.TButton",
                   command=lambda: self.start_quiz(self.quiz_questions)).pack(side="right")

    # ─── STUDY MODE ──────────────────────────────────────────────────────
    def start_study(self, questions):
        self.quiz_questions = list(questions)
        self.current_index = 0
        self.show_study_card()

    def show_study_card(self):
        self.clear_container()
        q = self.quiz_questions[self.current_index]
        total = len(self.quiz_questions)
        idx = self.current_index + 1

        # Top bar
        top = ttk.Frame(self.container, style="Header.TFrame")
        top.pack(fill="x")
        top_inner = ttk.Frame(top, style="Header.TFrame")
        top_inner.pack(fill="x", padx=20, pady=10)

        ttk.Label(top_inner, text=f"📖  Modo Estudio — {idx} de {total}",
                  background=BG_HEADER, foreground=FG_TITLE,
                  font=self.font_subtitle).pack(side="left")
        ttk.Label(top_inner, text=f"🪜 {q['level']}   🏷️  {q['category']}",
                  background=BG_HEADER, foreground=MAGENTA,
                  font=self.font_small).pack(side="right")

        # Card
        card = ttk.Frame(self.container, style="Card.TFrame")
        card.pack(fill="both", expand=True, padx=25, pady=15)

        # Scrollable content
        canvas = tk.Canvas(card, bg=BG_CARD, highlightthickness=0)
        sb = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, style="Card.TFrame")
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw", tags="content_window")

        def on_canvas_resize(event):
            canvas.itemconfig("content_window", width=event.width)
        canvas.bind("<Configure>", on_canvas_resize)

        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        sb.pack(side="right", fill="y", padx=(0, 5), pady=15)

        # Mousewheel
        def on_mousewheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Question
        tk.Label(content, text=q["question"], bg=BG_CARD, fg=FG_TITLE,
                 font=self.font_question, wraplength=750, justify="left",
                 anchor="w").pack(fill="x", padx=10, pady=(5, 15))

        # Options with answer highlighted
        for key in sorted(q["options"].keys()):
            is_correct = key == q["answer"]
            bg = OPTION_CORRECT if is_correct else OPTION_BG
            fg_color = "#fff" if is_correct else FG_TEXT
            marker = "  ✅" if is_correct else ""

            opt_frame = tk.Frame(content, bg=bg, bd=0,
                                 highlightthickness=2,
                                 highlightbackground=GREEN if is_correct else BG_CARD)
            opt_frame.pack(fill="x", padx=10, pady=2)
            tk.Label(opt_frame, text=f"  {key})  {q['options'][key]}{marker}",
                     bg=bg, fg=fg_color, font=self.font_option,
                     anchor="w", padx=15, pady=8, wraplength=700,
                     justify="left").pack(fill="x")

        # Explanation
        tk.Label(content, text="💡 Explicación:", bg=BG_CARD, fg=ACCENT,
                 font=self.font_subtitle, anchor="w").pack(fill="x", padx=10, pady=(15, 5))

        tk.Label(content, text=q["explanation"], bg=BG_CARD, fg=FG_DIM,
                 font=self.font_explanation, wraplength=750, justify="left",
                 anchor="nw").pack(fill="x", padx=10, pady=(0, 10))

        # Navigation
        btn_bar = ttk.Frame(self.container)
        btn_bar.pack(fill="x", padx=25, pady=(0, 15))

        ttk.Button(btn_bar, text="🏠 Menú", command=self.show_home,
                   style="Nav.TButton").pack(side="left")

        if idx < total:
            ttk.Button(btn_bar, text="Siguiente ▶",
                       command=self._study_next, style="Accent.TButton").pack(side="right")

        if idx > 1:
            ttk.Button(btn_bar, text="◀ Anterior",
                       command=self._study_prev, style="Nav.TButton").pack(side="right", padx=(0, 5))

    def _study_next(self):
        if self.current_index < len(self.quiz_questions) - 1:
            self.current_index += 1
            self.show_study_card()

    def _study_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_study_card()


# ─── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
