from pydantic import BaseModel, ValidationError
from rich import print
from typing import Union


class StringModel(BaseModel):
    first_string: str
    second_string: str


class FloatModel(BaseModel):
    first_float: float
    second_float: float


Model = Union[StringModel, FloatModel]


def validate_model(data: str) -> Model:
    try:
        return StringModel.model_validate_json(data)
    except Exception:
        pass

    try:
        return FloatModel.model_validate_json(data)
    except Exception:
        raise ValidationError("Failed to validate data")


test_data = """{
  "first_float": 1.0,
  "second_float": 2.0
}"""


out = validate_model(test_data)
print(out)
print(type(out))
if isinstance(out, StringModel):
    print("[bold red]It's a string model!")
elif isinstance(out, FloatModel):
    print("[bold green]It's a float model!")