"""Hook de MkDocs: publica junto al sitio los archivos que viven fuera de `book/`
(banco de reactivos y programas de autoevaluación) para que los enlaces de
`autoevaluacion.md` funcionen en el sitio generado."""

from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files

ROOT = Path(__file__).resolve().parent
EXTRA_FILES = [
    "question-bank.json",
    "oodb-questions.json",
    "oodb-questions-en.json",
    "quiz-es.json",
    "quiz-en.json",
    "quiz.py",
    "quiz-win.py",
    "self-test-app/oodb_quiz_console.py",
    "self-test-app/oodb_quiz_gui.py",
    "self-test-app/config.yml",
]


def on_files(files: Files, config: MkDocsConfig) -> Files:
    for uri in EXTRA_FILES:
        if not (ROOT / uri).is_file():
            continue
        existing = files.get_file_from_path(uri)
        if existing is not None:
            files.remove(existing)
        files.append(
            File(
                uri,
                src_dir=str(ROOT),
                dest_dir=config.site_dir,
                use_directory_urls=config.use_directory_urls,
            )
        )
    return files
