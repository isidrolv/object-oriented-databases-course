# Bases de Datos Orientadas a Objetos: curso neuro-optimizado de 90 días

Programa de estudio para llegar al **1 % superior** en Bases de Datos Orientadas a Objetos (BDOO) en 13 semanas, basado en **recuerdo activo**, **repetición espaciada**, **intercalación** y la **técnica Feynman**.

## Contenido

| Ruta | Qué contiene |
|---|---|
| `book/programa-de-estudio.md` | Plan semanal de 13 semanas, ciclo diario, calendario de repasos, plantilla Feynman e intercalación |
| `book/lecciones/` | 14 lecciones (00–13): fundamentos, modelo de objetos, ODMG/ODL, OQL, persistencia, almacenamiento e índices, transacciones, evolución de esquema, objeto-relacional, ORM, optimización, sistemas reales y diseño avanzado |
| `book/ejemplos/` | 7 ejercicios (2 básicos, 3 intermedios, 2 avanzados) con problema, escenario, entradas/salidas, solución incompleta y respuesta esperada |
| `book/autoevaluacion.md`, `book/glosario.md` | Guía de autoevaluación y glosario |
| `question-bank.json` | **Banco maestro de 60 reactivos** bilingüe (ES/EN): 20 básicos, 20 intermedios y 20 avanzados |
| `oodb-questions*.json`, `quiz-*.json` | Derivados generados por `tools/build_question_bank.py` |
| `quiz.py`, `quiz-win.py` | Cuestionarios bilingües (consola y GUI) |
| `self-test-app/` | Cuestionarios de consola (con `config.yml`) y GUI (filtros y modo estudio) |
| `tests/` | Pruebas de integridad del banco de reactivos |
| `mkdocs.yml`, `mkdocs_hooks.py` | Sitio de documentación con MkDocs Material |

## Inicio rápido

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (source .venv/bin/activate en Linux/macOS)
pip install -r requirements.txt

mkdocs serve                      # http://127.0.0.1:8000
mkdocs build                      # genera site/

python quiz.py                    # practicar con el banco
python tools/build_question_bank.py   # regenerar derivados tras editar question-bank.json
pytest -q                         # validar el banco
```

> **Nota:** ZODB todavía no publica *wheels* para versiones muy recientes de Python. Si `pip install ZODB` falla al compilar, usa Python 3.12/3.13 o instala en modo Python puro: `PURE_PYTHON=1 pip install ZODB` (en PowerShell: `$env:PURE_PYTHON=1`).

Los programas de cuestionario se adaptaron de los del proyecto `ArchitecturalInterviewQuestionsAndAswers`.
