from fastapi import APIRouter, HTTPException
from app.services import academy as academy_service

router = APIRouter(prefix="/api/lessons", tags=["Syllabus Reference"])

@router.get("")
def list_lessons():
    """Retrieve list of all 11 lesson modules with metadata parsed from docstrings."""
    try:
        return academy_service.get_lessons_metadata()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load course list: {e}")

@router.get("/{lesson_id}/code")
def get_lesson_code(lesson_id: str):
    """Retrieve raw python script contents for a specific lesson."""
    try:
        return academy_service.get_lesson_code(lesson_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lesson script: {e}")

@router.post("/{lesson_id}/run")
def run_lesson(lesson_id: str):
    """Execute a lesson script inside the active virtual environment and capture execution console trace."""
    try:
        return academy_service.run_lesson(lesson_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subprocess run failure: {e}")
