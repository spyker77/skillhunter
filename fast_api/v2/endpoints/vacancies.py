import pdftotext
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from fast_api.v2.schemas import VacanciesResponseSchema
from resume_analyzer.analyzer import analyze_resume

router = APIRouter()


@router.post(
    "/",
    response_model=VacanciesResponseSchema,
    description="Upload resume in PDF and get tailored vacancies.",
)
def show_tailored_vacancies(resume: UploadFile = File(...)):
    try:
        tailored_vacancies = analyze_resume(resume.file)
    except pdftotext.Error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacancies not found")
    return {"vacancies": tailored_vacancies}
