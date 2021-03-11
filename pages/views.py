from django.views.generic import TemplateView

from resume_analyzer.forms import UploadResumeForm


class HomePageView(TemplateView):
    template_name = "home.html"
    upload_resume_form = UploadResumeForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.upload_resume_form
        return context


class AboutPageView(TemplateView):
    template_name = "about.html"
