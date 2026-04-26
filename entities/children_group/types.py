from pydantic import BaseModel, Field, field_validator


class ChildrenGroupCreate(BaseModel):
    title: str = '03-N'
    age_group: str = '4-5'
    general_notes: str = 'A few childs with syndromes'

    has_special_needs: bool = False
    special_notes: str = ''

    @field_validator('age_group')
    @classmethod
    def validate_age_group(cls, v: str):

        v = v.strip()

        if '-' not in v:
            raise ValueError("Age group must be in format X-Y")

        parts = v.split('-')

        if len(parts) != 2:
            raise ValueError("Age group must be in format X-Y")

        try:
            start = int(parts[0])
            end = int(parts[1])
        except ValueError:
            raise ValueError("Age group must contain numbers only")

        if start < 1 or end > 7:
            raise ValueError("Age range must be between 1 and 7")

        if start >= end:
            raise ValueError("Start age must be less than end age")

        return f"{start}-{end}"


class ChildrenGroupOut(BaseModel):
    id: int
    title: str
    age_group: str
    children_count: int
    boys_count: int
    girls_count: int
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