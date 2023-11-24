from django.shortcuts import render
from django.views.generic import FormView
from pypdf.errors import PdfStreamError

from pages.views import BaseFormWithContextView

from .analyzer import analyze_resume
from .forms import UploadResumeForm

LIMIT_OF_VACANCIES = 200


class UploadResumeView(BaseFormWithContextView, FormView):
    template_name = "tailored_vacancies.html"
    form_class = UploadResumeForm

    def form_valid(self, form):
        resume_in_memory = self.request.FILES["file"]
        try:
            tailored_vacancies = analyze_resume(resume_in_memory)
            return render(self.request, self.template_name, {"vacancies": tailored_vacancies[:LIMIT_OF_VACANCIES]})
        except PdfStreamError:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context["error_uploading_resume"] = "🚨 Please, make sure you've saved the resume in PDF format!"
        return render(self.request, "home.html", context)
