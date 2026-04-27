from pydantic import BaseModel, Field
from typing import List
from pydantic import BaseModel, Field, field_validator

class ParentAccountCreate(BaseModel):
    group_id: int = Field(example=1)
    child_ids: List[int] = Field(example=[1, 2])
    login: str = Field(min_length=3, max_length=50, example='parent_group_01')


class ParentAccountOut(BaseModel):
    parent_user_id: int
    login: str
    password: str
    role: str
    child_ids: List[int]


class ParentChildrenUpdate(BaseModel):
    child_ids: List[int] = Field(example=[3, 4])


class ParentChildrenOut(BaseModel):
    parent_user_id: int
    login: str
    child_ids: List[int]


class ParentPasswordResetIn(BaseModel):
    parent_user_id: int = Field(example=5)


class ParentPasswordResetOut(BaseModel):
    parent_user_id: int
    login: str
    password: str


# class ParentProfileUpdate(BaseModel):
#     firstname: str = Field(min_length=1, max_length=25, example='Aruzhan')
#     lastname: str = Field(min_length=1, max_length=25, example='Bekova')

class ParentProfileUpdate(BaseModel):
    firstname: str = Field(min_length=3, max_length=23, example='Aruzhan')
    lastname: str = Field(min_length=3, max_length=23, example='Bekova')

    @field_validator('firstname', 'lastname')
    @classmethod
    def normalize_names(cls, v: str):
        v = v.strip()

        if len(v) < 3:
            raise ValueError("Name must be at least 3 characters")

        return v.capitalize()

class ParentProfileOut(BaseModel):
    id: int
    firstname: str
    lastname: str
    login: str