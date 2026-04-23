from pydantic import BaseModel, Field

class ParentNoteCreate(BaseModel):
    parent_name: str = Field(min_length=1, max_length=100, example='Aruzhan')
    parent_note: str = Field(min_length=1, example='My child will be absent tomorrow')

class ParentNoteOut(BaseModel):
    id: int
    group_id: int
    parent_user_id: int
    parent_name: str
    parent_note: str

    model_config = {'from_attributes': True}

class ParentNoteUpdate(BaseModel):
    parent_note: str = Field(min_length=1, example='Updated note by educator')