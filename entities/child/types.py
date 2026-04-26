# from pydantic import BaseModel, Field
# from enum import Enum


# class GenderEnum(str, Enum):
#     boy = 'boy'
#     girl = 'girl'


# class ChildCreate(BaseModel):
#     group_id: int
#     first_name: str = Field(min_length=1, max_length=50)
#     last_name: str = Field(min_length=1, max_length=50)
#     age: int = Field(ge=1, le=7)
#     gender: GenderEnum


# class ChildOut(BaseModel):
#     id: int
#     group_id: int
#     first_name: str
#     last_name: str
#     age: int
#     gender: GenderEnum

#     model_config = {
#         'from_attributes': True
#     }


from pydantic import BaseModel, Field, field_validator
from enum import Enum


class GenderEnum(str, Enum):
    boy = 'boy'
    girl = 'girl'


def normalize_name(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("Field cannot be empty")

    if any(char.isdigit() for char in value):
        raise ValueError("Name cannot contain numbers")

    return value.lower().capitalize()


class ChildCreate(BaseModel):
    group_id: int
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=1, le=7)
    gender: GenderEnum

    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v):
        return normalize_name(v)

    # 🆕 CLEAN LAST NAME
    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v):
        return normalize_name(v)


class ChildOut(BaseModel):
    id: int
    group_id: int
    first_name: str
    last_name: str
    age: int
    gender: GenderEnum

    model_config = {
        'from_attributes': True
    }

    # 🆕 normalize on output too (extra safety)
    @field_validator('first_name', 'last_name', mode='before')
    @classmethod
    def format_names(cls, v):
        if not v:
            return v
        return v.strip().lower().capitalize()