from pydantic import BaseModel, Field


class DoctorSearchQuery(BaseModel):
    """Structured representation of a natural-language doctor search question.

    Populated by an LLM via OpenAI's structured-output `parse` endpoint so we
    can feed the fields directly into the ranker without manual parsing.
    """

    limit: int = Field(
        default=5,
        ge=1,
        description="How many doctors the user asked for. Default to 5 if unspecified.",
    )
    name: str | None = Field(
        default=None,
        description="Full or partial doctor name if mentioned.",
    )
    speciality: str | None = Field(
        default=None,
        description="Medical speciality (e.g. 'Cardiology', 'Psychiatry').",
    )
    location: str | None = Field(
        default=None,
        description="City or town if mentioned.",
    )
    county: str | None = Field(
        default=None,
        description="County / region if mentioned.",
    )
    clinic_name: str | None = Field(
        default=None,
        description="Clinic name if mentioned.",
    )
    address: str | None = Field(
        default=None,
        description="Street address if mentioned.",
    )
    education: str | None = Field(
        default=None,
        description="University / school if mentioned.",
    )
