from typing import List, Tuple

from django.db import models
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    @classmethod
    def from_orms(cls, instances: List[models.Model]):
        return [cls.from_orm(inst) for inst in instances]


class VacancySchema(BaseModel):
    title: str
    content: str
    rated_skills: str

    class Config:
        orm_mode = True


class VacanciesSchema(BaseModel):
    data: List[VacancySchema]

    @classmethod
    def serialize(cls, instances):
        return cls(data=VacancySchema.from_orms(instances))


class SkillsResponseSchema(BaseModel):
    vacancy_name: str
    number_of_vacancies: int
    rated_skills: List[Tuple[str, int]]
