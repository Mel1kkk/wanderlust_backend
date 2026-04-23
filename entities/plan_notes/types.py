from pydantic import BaseModel, Field


class PlanNoteCreate(BaseModel):
    group_id: int = Field(example=1)
    teacher_notes: str = Field(
        example="Add more outdoor games and a short music activity at the end of the lesson"
    )


class PlanNoteOut(BaseModel):
    group_id: int
    title: str
    plan: str
    teacher_notes: str

    model_config = {
        "from_attributes": True
    }