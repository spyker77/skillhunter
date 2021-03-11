from django.contrib import admin

from scrapers.models import Job, Search, Skill, Vacancy


class VacancyAdmin(admin.ModelAdmin):
    list_display = (
        "url",
        "title",
        "content",
        "rated_skills",
        "created_date",
    )


class SearchAdmin(admin.ModelAdmin):
    list_display = (
        "query",
        "ip_address",
        "user_agent",
        "created_date",
    )


class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "clean_name",
        "unclean_names",
        "created_date",
    )


admin.site.register(Vacancy, VacancyAdmin)
admin.site.register(Job)
admin.site.register(Search, SearchAdmin)
admin.site.register(Skill, SkillAdmin)
