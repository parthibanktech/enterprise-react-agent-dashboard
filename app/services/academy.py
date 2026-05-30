import os
import re
import ast
import sys
import subprocess
from app.core.config import BASE_DIR

def get_lessons_metadata() -> list:
    """Scan the lessons/ folder and dynamically parse course files using AST to extract metadata."""
    lessons_dir = os.path.join(BASE_DIR, "lessons")
    lessons = []
    if not os.path.exists(lessons_dir):
        return lessons
        
    for filename in sorted(os.listdir(lessons_dir)):
        if filename.endswith(".py") and re.match(r"^\d{2}_", filename):
            filepath = os.path.join(lessons_dir, filename)
            lesson_id = filename[:2]
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    node = ast.parse(f.read())
                docstring = ast.get_docstring(node) or ""
            except Exception:
                docstring = ""
                
            concept = ""
            description = ""
            title = filename.replace("_", " ").replace(".py", "").title()
            title = re.sub(r"^(\d{2})\s+", r"\1: ", title)
            title = (
                title.replace("Llms", "LLMs")
                .replace("Llm", "LLM")
                .replace("React", "ReAct")
                .replace("Ui", "UI")
                .replace("Sql", "SQL")
                .replace("Api", "API")
            )
            
            if docstring:
                lines = docstring.strip().split("\n")
                concept_line = [l for l in lines if l.strip().lower().startswith("concept:")]
                if concept_line:
                    concept = concept_line[0].split(":", 1)[1].strip()
                
                desc_lines = []
                capture = False
                for line in lines:
                    if "concept:" in line.lower():
                        capture = True
                        continue
                    if capture:
                        desc_lines.append(line)
                description = "\n".join(desc_lines).strip()
            
            lessons.append({
                "id": lesson_id,
                "filename": filename,
                "title": title,
                "concept": concept or "General Agent Concept",
                "description": description or "Learn about building resilient AI agents with LangChain.",
            })
    return lessons

def get_lesson_code(lesson_id: str) -> dict:
    """Retrieve raw python code for the selected lesson script."""
    lessons_dir = os.path.join(BASE_DIR, "lessons")
    if not os.path.exists(lessons_dir):
        raise FileNotFoundError("Lessons directory not found")
        
    filename = None
    for f in os.listdir(lessons_dir):
        if f.startswith(lesson_id) and f.endswith(".py") and re.match(r"^\d{2}_", f):
            filename = f
            break
            
    if not filename:
        raise ValueError(f"Lesson '{lesson_id}' not found")
        
    filepath = os.path.join(lessons_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    return {"filename": filename, "code": code}

def run_lesson(lesson_id: str) -> dict:
    """Execute a lesson script inside the current active python environment and return stdout/stderr."""
    lessons_dir = os.path.join(BASE_DIR, "lessons")
    if not os.path.exists(lessons_dir):
        raise FileNotFoundError("Lessons directory not found")
        
    filename = None
    for f in os.listdir(lessons_dir):
        if f.startswith(lesson_id) and f.endswith(".py") and re.match(r"^\d{2}_", f):
            filename = f
            break
            
    if not filename:
        raise ValueError(f"Lesson '{lesson_id}' not found")
        
    filepath = os.path.join(lessons_dir, filename)
    
    run_env = os.environ.copy()
    run_env["NON_INTERACTIVE"] = "true"

    result = subprocess.run(
        [sys.executable, filepath],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=BASE_DIR,
        env=run_env
    )
    return {
        "filename": filename,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }
