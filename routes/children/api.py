from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from entities.user.entity import User
from entities.children_group.entity import ChildrenGroup
from entities.child.entity import Child, GenderEnum
from entities.child.types import ChildCreate, ChildNoteUpdate, ChildOut

router = APIRouter()


@router.post('', response_model=ChildOut)
async def create_child(
    data: ChildCreate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can create children')

    group = await ChildrenGroup.get_by_id(db, data.group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    
    note = data.note_about_child.strip() if data.note_about_child else "No notes about this child"

    child = await Child.create(
        db,
        group_id=data.group_id,
        first_name=data.first_name,
        last_name=data.last_name,
        age=data.age,
        gender=data.gender,
        note_about_child=note
    )

    if not child:
        raise HTTPException(status_code=409, detail='Child already exists in this group')

    group.children_count += 1
    if child.gender == GenderEnum.boy:
        group.boys += 1
    else:
        group.girls += 1

    db.add(group)
    await db.commit()
    await db.refresh(group)

    # return ChildOut.from_orm(child)
    return ChildOut.model_validate(child)
    

@router.patch('/{child_id}/note', response_model=ChildOut)
async def update_child_note(
    child_id: int,
    data: ChildNoteUpdate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can edit child notes')

    child = await Child.get_by_id(db, child_id)
    if not child:
        raise HTTPException(status_code=404, detail='Child not found')

    group = await ChildrenGroup.get_by_id(db, child.group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=403, detail='Child does not belong to your group')

    updated = await Child.update_note(db, child, data.note_about_child)

    # return ChildOut.from_orm(updated)
    return ChildOut.model_validate(updated)


@router.get('/group/{group_id}', response_model=list[ChildOut])
async def get_children(
    group_id: int,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can view children')

    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    children = await Child.list_by_group(db, group_id)

    if not children:
        raise HTTPException(status_code=404, detail='No children in this group')

    # return [ChildOut.from_orm(c) for c in children]
    return [ChildOut.model_validate(c) for c in children]



@router.delete('/{child_id}', status_code=204)
async def delete_child(
    child_id: int,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can delete children')

    child = await Child.get_by_id(db, child_id)
    if not child:
        raise HTTPException(status_code=404, detail='Child not found')

    group = await ChildrenGroup.get_by_id(db, child.group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=403, detail='Child does not belong to your group')

    if child.gender == GenderEnum.boy:
        group.boys -= 1
    else:
        group.girls -= 1

    group.children_count -= 1

    db.add(group)
    await db.commit()

    await Child.delete(db, child)