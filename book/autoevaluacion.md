# Autoevaluación

El recuerdo activo es el motor de este curso. Aquí tienes el **banco de 60 reactivos** (20 básicos, 20 intermedios y 20 avanzados, en español e inglés) y **cuatro programas** para practicar con él.

## Banco de reactivos

| Archivo | Contenido | Uso |
|---|---|---|
| [`question-bank.json`](question-bank.json) | **Banco maestro bilingüe** (fuente única de verdad) | Edítalo para agregar o corregir reactivos |
| [`oodb-questions.json`](oodb-questions.json) | Derivado en español, con `level` y `category` | `self-test-app/` |
| [`oodb-questions-en.json`](oodb-questions-en.json) | Derivado en inglés, con `level` y `category` | `self-test-app/` |
| [`quiz-es.json`](quiz-es.json) / [`quiz-en.json`](quiz-en.json) | Derivados con `section` y `category` | `quiz.py`, `quiz-win.py` |

Estructura de un reactivo en el banco maestro:

```json
{
  "id": 28, "lesson": "05",
  "level":    {"es": "Intermedio", "en": "Intermediate"},
  "category": {"es": "Persistencia", "en": "Persistence"},
  "question": {"es": "En ZODB, ...", "en": "In ZODB, ..."},
  "options":  {"es": ["...", "...", "...", "..."], "en": ["...", "...", "...", "..."]},
  "answer": "d",
  "explanation": {"es": "...", "en": "..."}
}
```

Después de editar el banco, regenera los derivados (valida, equilibra las respuestas a/b/c/d y escribe los archivos):

```bash
python tools/build_question_bank.py
```

### Distribución

| Nivel | Reactivos | Lecciones que cubre |
|---|---|---|
| 🟢 Básico | 1–20 | 01, 02, 03, 04, 05, 09, 10 |
| 🟡 Intermedio | 21–40 | 02, 03, 04, 05, 06, 07, 09, 10 |
| 🔴 Avanzado | 41–60 | 01, 05, 06, 07, 08, 10, 11, 12, 13 |

Las respuestas correctas están repartidas por igual (15 en cada letra) para que no haya patrones adivinables.

## Programas de autoevaluación

Hay cuatro modelos de programa, cada uno con sus ventajas:

| Programa | Tipo | Idioma | Fortalezas |
|---|---|---|---|
| [`quiz.py`](quiz.py) | Consola | ES / EN (se elige al inicio) | Ligero; eliges la cantidad de preguntas y si se mezclan; gráfica de resultado opcional |
| [`quiz-win.py`](quiz-win.py) | GUI (tkinter) | ES / EN | Interfaz gráfica bilingüe; **mezcla las opciones** de cada pregunta (evita memorizar la letra) |
| [`self-test-app/oodb_quiz_console.py`](self-test-app/oodb_quiz_console.py) | Consola | ES (o EN con variable de entorno) | Subconjunto aleatorio configurable en `config.yml` (`max_questions`, `pass_threshold`): ideal para la práctica diaria de 5 reactivos |
| [`self-test-app/oodb_quiz_gui.py`](self-test-app/oodb_quiz_gui.py) | GUI (tkinter) | ES (o EN con variable de entorno) | Quiz completo, rápido, personalizado, **filtro por nivel y por categoría** y **modo estudio** |

### Cómo ejecutarlos

```bash
pip install -r requirements.txt          # matplotlib y pyyaml (opcionales para gráficas y configuración)

python quiz.py                            # consola bilingüe
python quiz-win.py                        # GUI bilingüe
python self-test-app/oodb_quiz_console.py # consola con config.yml
python self-test-app/oodb_quiz_gui.py     # GUI con filtros y modo estudio
```

Para usar las apps de `self-test-app/` en inglés:

```powershell
# PowerShell
$env:QUESTIONS_FILE_NAME = "../oodb-questions-en.json"; python self-test-app/oodb_quiz_console.py
$env:QUESTIONS_FILE = "oodb-questions-en.json"; python self-test-app/oodb_quiz_gui.py
```

## Protocolo de práctica (vinculado al programa)

| Momento | Herramienta | Configuración | Meta |
|---|---|---|---|
| Diario (10 min) | `oodb_quiz_console.py` | `max_questions: 5` | Activar memoria; anota los fallos como tarjetas |
| Sábado (intercalación) | `oodb_quiz_gui.py` → Quiz rápido | 10–20 aleatorias de todos los niveles vistos | ≥ 80 % |
| Fin de semana 4 | `quiz.py` | Solo nivel básico (1–20) | ≥ 85 % |
| Fin de semana 8 | `quiz-win.py` | 40 preguntas, mezcladas | ≥ 85 % |
| Día 90 | `quiz-win.py` | Las 60, mezcladas, en **inglés** | ≥ 90 % |

!!! tip "Cada error es una tarjeta"
    Cuando falles un reactivo, no basta con leer la explicación: escribe una tarjeta con tus propias palabras (Feynman) y agrégala a la caja 1 de tu sistema Leitner.
