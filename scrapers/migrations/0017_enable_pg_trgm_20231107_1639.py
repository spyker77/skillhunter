# Generated by Django 4.2.7 on 2023-11-07 16:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("scrapers", "0016_alter_skill_unclean_names_alter_vacancy_rated_skills"),
    ]

    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS pg_trgm;", "DROP EXTENSION IF EXISTS pg_trgm;"),
    ]
