# Self-Test App

Herramientas en Python para practicar con el banco de reactivos del curso de
**Bases de Datos Orientadas a Objetos**, a partir de
[`../oodb-questions.json`](../oodb-questions.json) (generado desde `../question-bank.json`).

## Requisitos

```bash
pip install pyyaml matplotlib
```

> `tkinter` es necesario para la GUI y viene incluido en la mayoría de las distribuciones de Python.

## Programas

| Programa | Descripción |
|---|---|
| `oodb_quiz_console.py` | Cuestionario interactivo en terminal; muestra una gráfica de resultados al final |
| `oodb_quiz_gui.py` | Cuestionario gráfico (tkinter): quiz completo, rápido, personalizado, filtro por nivel o categoría y modo estudio |

## Uso

Se pueden ejecutar desde **cualquier** directorio; resuelven las rutas a partir de su propia ubicación.

```bash
python self-test-app/oodb_quiz_console.py
python self-test-app/oodb_quiz_gui.py
```

En inglés:

```powershell
$env:QUESTIONS_FILE_NAME = "../oodb-questions-en.json"; python self-test-app/oodb_quiz_console.py
$env:QUESTIONS_FILE = "oodb-questions-en.json"; python self-test-app/oodb_quiz_gui.py   # ruta relativa al directorio actual
```

## Configuración

Edita `config.yml` para ajustar el umbral de aprobación y el número máximo de preguntas por sesión del cuestionario de consola. Para la práctica diaria del programa de estudio usa `max_questions: 5`.
