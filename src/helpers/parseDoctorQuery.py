from pathlib import Path

from jinja2 import Template
from openai import OpenAI

from src.models.DoctorSearchQuery import DoctorSearchQuery
from src.models.ParseDoctorQueryArgs import ParseDoctorQueryArgs

SYSTEM_PROMPT_PATH = (
    Path(__file__).resolve().parents[1] / "prompts" / "parseDoctorQuerySystem.j2"
)


def parseDoctorQuery(args: ParseDoctorQueryArgs) -> DoctorSearchQuery:
    systemPrompt = Template(
        SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    ).render()

    client = OpenAI()
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": args.question},
        ],
        text_format=DoctorSearchQuery,
    )

    parsed = response.output_parsed
    if parsed is None:
        raise ValueError("OpenAI returned no parsed output for the query.")
    return parsed
