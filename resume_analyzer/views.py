import pdftotext
from django.shortcuts import render

from .analyzer import analyze_resume
from .forms import UploadResumeForm

LIMIT_OF_VACANCIES = 200


def upload_resume(request):
    upload_resume_form = UploadResumeForm()
    context_for_error = {
        "form": upload_resume_form,
        "error_uploading_resume": "🚨 Please, make sure you've saved the resume in PDF format!",
    }
    if request.method == "POST":
        posted_resume_form = UploadResumeForm(request.POST, request.FILES)
        if posted_resume_form.is_valid():
            resume_in_memory = request.FILES["resume"]
            try:
                tailored_vacancies = analyze_resume(resume_in_memory)
            except pdftotext.Error:
                return render(request, "home.html", context_for_error)
            return render(request, "tailored_vacancies.html", {"vacancies": tailored_vacancies[:LIMIT_OF_VACANCIES]})
