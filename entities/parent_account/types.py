from pydantic import BaseModel, Field


class ParentAccountCreate(BaseModel):
    group_id: int = Field(example=1)
    login: str = Field(min_length=3, max_length=50, example='parent_group_01')


class ParentAccountOut(BaseModel):
    group_id: int
    parent_user_id: int
    login: str
    password: str
    role: str


class ParentPasswordResetIn(BaseModel):
    group_id: int = Field(example=1)


class ParentPasswordResetOut(BaseModel):
    group_id: int
    parent_user_id: int
    login: str
    password: str