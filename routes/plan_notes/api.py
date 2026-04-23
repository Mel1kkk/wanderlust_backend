from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from entities.user.entity import User
from entities.children_group.entity import ChildrenGroup
from entities.plan_notes.entity import PlanNote
from entities.plan_notes.types import PlanNoteCreate, PlanNoteOut

router = APIRouter()


@router.post('', response_model=PlanNoteOut, status_code=status.HTTP_201_CREATED)
async def create_or_update_note(
    data: PlanNoteCreate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can manage plan notes')

    group = await ChildrenGroup.get_by_id(db, data.group_id, user_id=me.id)

    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    note = await PlanNote.upsert(
        db,
        group_id=group.id,
        plan=group.plan,
        teacher_notes=data.teacher_notes
    )

    return {
        'group_id': group.id,
        'title': group.title,
        'plan': note.plan,
        'teacher_notes': note.teacher_notes
    }


@router.get('/{group_id}', response_model=PlanNoteOut)
async def get_note(
    group_id: int,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can view plan notes')

    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)

    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    note = await PlanNote.get_by_group(db, group_id)

    if not note:
        raise HTTPException(status_code=404, detail='Note not found')

    return {
        'group_id': group.id,
        'title': group.title,
        'plan': note.plan,
        'teacher_notes': note.teacher_notes
    }