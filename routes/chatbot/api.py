from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from entities.children_group.entity import ChildrenGroup
from entities.user.entity import User
from chatbot.generator import generate_text

router = APIRouter()


class GenerateRequest(BaseModel):
    group_id: int
    theme: str = 'summer'
    output_type: str
    teacher_notes: str = 'make a creative plan'
    max_tokens: int = 600


class GenerateResponse(BaseModel):
    text: str


@router.post('/generate', response_model=GenerateResponse)
async def generate(
    req: GenerateRequest,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can generate plans')

    group = await ChildrenGroup.get_by_id(db, req.group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    input_data = {
        'age_group': group.age_group,
        'theme': req.theme,
        'output_type': req.output_type,
        'teacher_notes': req.teacher_notes,
        'max_tokens': req.max_tokens,
        'has_special_needs': group.has_special_needs,
        'special_notes': group.special_notes        
    }

    result = generate_text(input_data)

    group.plan = result
    group.is_completed = False
    db.add(group)
    await db.commit()
    await db.refresh(group)

    return {'text': result}