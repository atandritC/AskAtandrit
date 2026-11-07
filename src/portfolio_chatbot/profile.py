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
    duration_months: int | None = Field(
        default=None,
        description="Role duration in whole calendar months, calculated by Python.",
    )
    duration_display: str | None = Field(
        default=None,
        description="Human-readable role duration, such as '1 year 9 months'.",
    )
    details: list[str] = Field(default_factory=list)
    start_year: int | None = None
    start_month: int | None = Field(default=None, ge=1, le=12)
    end_year: int | None = None
    end_month: int | None = Field(default=None, ge=1, le=12)
    is_current: bool | None = None


class CandidateProfile(BaseModel):
    name: str | None = None
    summary: str | None = None
    total_experience_months: int | None = Field(
        default=None,
        description="Overall professional experience in whole calendar months, calculated by Python from verified work dates.",
    )
    total_experience_display: str | None = Field(
        default=None,
        description="Human-readable overall experience, such as '1 year 9 months'.",
    )
    skills: list[str] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
