from pydantic import BaseModel, Field


class ParentNoteCreate(BaseModel):
    child_id: int = Field(example=1)
    parent_note: str = Field(min_length=1, example='My child will be absent tomorrow')


class ParentNoteOut(BaseModel):
    id: int
    group_id: int
    parent_user_id: int
    parent_name: str
    child_id: int
    about_who: str
    parent_note: str

    model_config = {'from_attributes': True}


class ParentNoteUpdate(BaseModel):
    parent_note: str = Field(min_length=1, example='Updated note')