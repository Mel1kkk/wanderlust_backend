from pydantic import BaseModel, Field


class ChildrenGroupCreate(BaseModel):
    title: str = '03-N'
    age_group: str = '4-5'
    children_count: int = 20
    general_notes: str = 'A few childs with syndromes'

    has_special_needs: bool = False
    special_notes: str = ''

class ChildrenGroupOut(BaseModel):
    id: int
    title: str
    age_group: str
    children_count: int
    general_notes: str

    has_special_needs: bool
    special_notes: str

    plan: str = ''
    parent_user_id: int | None = None
    is_completed: bool

    model_config = {
        'from_attributes': True
    }

class PlanUpdate(BaseModel):
    plan: str = Field(min_length=1, example="Updated lesson plan...")    

class CompleteUpdate(BaseModel):
    is_completed: bool    