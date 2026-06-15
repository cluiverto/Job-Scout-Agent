from pydantic import BaseModel


class Skill(BaseModel):
    name: str
    level: int | None = None


class SalaryRange(BaseModel):
    from_: float | None = None
    to: float | None = None
    currency: str = "PLN"


class JobOffer(BaseModel):
    title: str
    company: str | None = None
    city: str | None = None
    salary: SalaryRange | None = None
    experience_level: str | None = None
    required_skills: list[Skill] = []
    nice_to_have_skills: list[Skill] = []
    description: str = ""
    url: str = ""
    source: str = "justjoin.it"
