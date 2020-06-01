from django.contrib import admin
from .models import Vacancy, Job, Skill, Stopword


class VacancyAdmin(admin.ModelAdmin):
    list_display = (
        "url",
        "title",
        "content",
        "rated_skills",
        "created_date",
    )


admin.site.register(Vacancy, VacancyAdmin)
admin.site.register(Job)
admin.site.register(Skill)
admin.site.register(Stopword)
