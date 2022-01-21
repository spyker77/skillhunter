import ipaddress

from django.db import models
from pydantic import BaseModel as _BaseModel
from pydantic import HttpUrl, validator


class BaseModel(_BaseModel):
    @classmethod
    def from_orms(cls, instances: list[models.Model]):
        return [cls.from_orm(inst) for inst in instances]


class VacancySchema(BaseModel):
    title: str
    content: str
    rated_skills: str

    class Config:
        orm_mode = True


class VacanciesSchema(BaseModel):
    data: list[VacancySchema]

    @classmethod
    def serialize(cls, instances):
        return cls(data=VacancySchema.from_orms(instances))


class SearchSchema(BaseModel):
    query: str
    ip_address: str
    user_agent: str

    @validator("ip_address", pre=True)
    def set_ip_address(cls, ip_address):
        try:
            # Replicate GenericIPAddressField behavior:
            # https://docs.djangoproject.com/en/4.0/ref/models/fields/#genericipaddressfield
            return str(ipaddress.ip_address(ip_address))
        except ValueError:
            return "1.1.1.1"


class SkillsResponseSchema(BaseModel):
    vacancy_name: str
    number_of_vacancies: int
    rated_skills: list[list[int | str]]


class VacanciesResponseSchema(BaseModel):
    vacancies: list[list[HttpUrl | list[int | str]]]
