from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from entities.children_group.entity import ChildrenGroup
from entities.children_group.types import ChildrenGroupCreate, ChildrenGroupOut, PlanUpdate, CompleteUpdate
from entities.user.entity import User
from entities.plan_notes.entity import PlanNote
from entities.parent_children.entity import ParentChild

router = APIRouter()


@router.post('', response_model=ChildrenGroupOut, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: ChildrenGroupCreate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can create groups')

    title_raw = data.title.strip()
    if not title_raw:
        raise HTTPException(status_code=400, detail='Group title cannot be empty')

    title_normalized = title_raw.lower()
    existing_groups = await ChildrenGroup.list_by_user(db, me.id)
    for g in existing_groups:
        if g.title.lower() == title_normalized:
            raise HTTPException(status_code=409, detail='Group with this title already exists')

    group = await ChildrenGroup.new(
        db,
        user_id=me.id,
        title=data.title,
        age_group=data.age_group,
        general_notes=data.general_notes,
        has_special_needs=data.has_special_needs,
        special_notes=data.special_notes
    )

    return ChildrenGroupOut(
        id=group.id,
        title=group.title,
        age_group=group.age_group,
        children_count=group.children_count,
        boys_count=group.boys,
        girls_count=group.girls,
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
    if me.role == 'educator':
        groups = await ChildrenGroup.list_by_user(db, me.id)

    elif me.role == 'parent':
        links = await ParentChild.list_by_parent(db, me.id)
        if links:
            group = await ChildrenGroup.get_by_id(db, links[0].group_id)
            groups = [group] if group else []
        else:
            groups = []

    else:
        raise HTTPException(status_code=403, detail='Unknown role')

    # return [
    #     ChildrenGroupOut(
    #         id=g.id,
    #         title=g.title,
    #         age_group=g.age_group,
    #         children_count=g.children_count,
    #         boys_count=g.boys,
    #         girls_count=g.girls,
    #         general_notes=g.general_notes,
    #         has_special_needs=g.has_special_needs,
    #         special_notes=g.special_notes,
    #         plan=g.plan,
    #         parent_user_id=g.parent_user_id,
    #         is_completed=g.is_completed
    #     )
    #     for g in groups
    # ]

    groups_with_parents = []

    for g in groups:
        parents = []

        links = await ParentChild.list_by_group(db, g.id)
        parent_ids = set(l.parent_user_id for l in links)

        for pid in parent_ids:
            parent = await User.get_by_id(db, pid)
            if parent:
                parents.append({
                    "parent_id": parent.id,
                    "full_name": f"{parent.firstname} {parent.lastname}"
                })

        groups_with_parents.append(
            ChildrenGroupOut(
                id=g.id,
                title=g.title,
                age_group=g.age_group,
                children_count=g.children_count,
                boys_count=g.boys,
                girls_count=g.girls,
                general_notes=g.general_notes,
                has_special_needs=g.has_special_needs,
                special_notes=g.special_notes,
                plan=g.plan,
                parent_user_id=g.parent_user_id,
                is_completed=g.is_completed,
                parents=parents
            )
        )

    return groups_with_parents

@router.delete('/{group_id}', status_code=204)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can delete groups')

    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    group.parent_user_id = None
    db.add(group)

    await db.delete(group)
    await db.commit()
    return


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
        boys_count=group.boys,
        girls_count=group.girls,
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
        boys_count=group.boys,
        girls_count=group.girls,
        general_notes=group.general_notes,
        has_special_needs=group.has_special_needs,
        special_notes=group.special_notes,
        plan=group.plan,
        parent_user_id=group.parent_user_id,
        is_completed=group.is_completed
    )