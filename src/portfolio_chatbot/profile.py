from pydantic import BaseModel, Field


class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    github_url: str | None = None
    live_url: str | None = None


class Experience(BaseModel):
    organization: str | None = None
    location: str | None = None
    role: str | None = None
    period: str | None = None
    duration_years: float | None = None
    details: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    name: str | None = None
    summary: str | None = None
    total_experience_years: float | None = Field(
        default=None,
        description="Overall professional experience, calculated by Python from verified work dates.",
    )
    skills: list[str] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
