from pydantic import BaseModel


class IDAndConfigMixin(BaseModel):
    id: str


class CreateAtMixin(BaseModel):
    created_at: str


class Status(BaseModel):
    status: str


class ResultBool(BaseModel):
    result: bool


def validate_sorting_value(value):
    if len(value) != 2:
        raise ValueError("Should be a list of two values")

    elif value[1] not in ["asc", "desc"]:
        raise ValueError(
            "Second value for sorting invalid, mast be asc or desc"
        )
    return value
