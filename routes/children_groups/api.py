from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from entities.children_group.entity import ChildrenGroup
from entities.children_group.types import ChildrenGroupCreate, ChildrenGroupOut
from entities.user.entity import User
from entities.children_group.types import PlanUpdate
from entities.plan_notes.entity import PlanNote
from entities.children_group.types import CompleteUpdate

router = APIRouter()


@router.post('', response_model=ChildrenGroupOut, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: ChildrenGroupCreate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can create groups')

    group = await ChildrenGroup.new(
        db,
        user_id=me.id,
        title=data.title,
        age_group=data.age_group,
        children_count=data.children_count,
        general_notes=data.general_notes,
        has_special_needs=data.has_special_needs,
        special_notes=data.special_notes
    )

    return ChildrenGroupOut(
        id=group.id,
        title=group.title,
        age_group=group.age_group,
        children_count=group.children_count,
        general_notes=group.general_notes,
        
        has_special_needs=group.has_special_needs,
        special_notes=group.special_notes,
        
        plan=group.plan,
        parent_user_id=group.parent_user_id,
        is_completed=group.is_completed
    )


@router.get('', response_model=list[ChildrenGroupOut])
async def list_groups(
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    # if me.role != 'educator':
    #     raise HTTPException(status_code=403, detail='Only educators can view groups list')

    # groups = await ChildrenGroup.list_by_user(db, me.id)

    if me.role == 'educator':
        groups = await ChildrenGroup.list_by_user(db, me.id)
    
    elif me.role == 'parent':
        group = await ChildrenGroup.get_by_parent_user_id(db, me.id)
        groups = [group] if group else []
    
    else:
        raise HTTPException(status_code=403, detail="Unknown role")

    result = []
    for g in groups:
        result.append(ChildrenGroupOut(
            id=g.id,
            title=g.title,
            age_group=g.age_group,
            children_count=g.children_count,
            general_notes=g.general_notes,

            has_special_needs=g.has_special_needs,
            special_notes=g.special_notes,

            plan=g.plan,
            parent_user_id=g.parent_user_id,
            is_completed=g.is_completed
        ))

    return result

@router.patch('/{group_id}/plan', response_model=ChildrenGroupOut)
async def update_group_plan(
    group_id: int,
    data: PlanUpdate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can edit plans')

    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    group = await ChildrenGroup.update_plan(db, group, data.plan)

    note = await PlanNote.get_by_group(db, group_id)
    if note:
        note.plan = data.plan
        db.add(note)
        await db.commit()
        await db.refresh(note)

    return ChildrenGroupOut(
        id=group.id,
        title=group.title,
        age_group=group.age_group,
        children_count=group.children_count,
        general_notes=group.general_notes,

        has_special_needs=group.has_special_needs,
        special_notes=group.special_notes,
        
        plan=group.plan,
        parent_user_id=group.parent_user_id,
        is_completed=group.is_completed
    )

@router.patch('/{group_id}/complete', response_model=ChildrenGroupOut)
async def update_completed_status(
    group_id: int,
    data: CompleteUpdate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can change completion status')

    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    if group.plan == 'No Plan':
        raise HTTPException(status_code=400, detail='Cannot complete empty plan')

    group = await ChildrenGroup.update_completed(db, group, data.is_completed)

    return ChildrenGroupOut(
        id=group.id,
        title=group.title,
        age_group=group.age_group,
        children_count=group.children_count,
        general_notes=group.general_notes,
        plan=group.plan,
        parent_user_id=group.parent_user_id,
        is_completed=group.is_completed
    )
