from django.views.generic import TemplateView

from resume_analyzer.forms import UploadResumeForm
from scrapers.forms import SearchForm


class BaseFormWithContextView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["upload_resume_form"] = UploadResumeForm()
        context["search_form"] = SearchForm()
        return context


class HomePageView(BaseFormWithContextView):
    template_name = "home.html"


class AboutPageView(TemplateView):
    template_name = "about.html"
