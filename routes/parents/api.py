from fastapi import APIRouter, Depends, HTTPException, status
from secrets import choice
from string import ascii_letters, digits
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from utils.facades.Hasher import Hasher
from entities.user.entity import User
from entities.children_group.entity import ChildrenGroup
from entities.child.entity import Child
from entities.parent_children.entity import ParentChild
from entities.parent_account.types import (
    ParentAccountCreate, ParentAccountOut,
    ParentChildrenUpdate, ParentChildrenOut,
    ParentPasswordResetIn, ParentPasswordResetOut,
    ParentProfileUpdate, ParentProfileOut
)
from entities.parent_children.entity import ParentChild
from entities.child.entity import Child

router = APIRouter()


def generate_password(length: int = 16) -> str:
    chars = ascii_letters + digits + '@$!%*?&'
    return ''.join(choice(chars) for _ in range(length))


@router.post('/create', response_model=ParentAccountOut, status_code=status.HTTP_201_CREATED)
async def create_parent_account(
    data: ParentAccountCreate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(403, 'Only educators can create parent accounts')

    group = await ChildrenGroup.get_by_id(db, data.group_id, user_id=me.id)
    if not group:
        raise HTTPException(404, 'Group not found')

    if not data.child_ids:
        raise HTTPException(400, 'At least one child must be provided')

    for child_id in data.child_ids:
        child = await Child.get_by_id(db, child_id)
        if not child or child.group_id != data.group_id:
            raise HTTPException(404, f'Child {child_id} not found in this group')
        existing = await ParentChild.get_by_child(db, child_id)
        if existing:
            raise HTTPException(409, f'Child {child_id} already has a parent assigned')

    existing_user = await User.get_by_login(db, data.login)
    if existing_user:
        raise HTTPException(409, 'This login is already taken')

    plain_password = generate_password()
    parent_user = await User.new_parent(db, login=data.login, password_hash=Hasher.hash_it(plain_password))

    for child_id in data.child_ids:
        await ParentChild.create(db, parent_user_id=parent_user.id, child_id=child_id, group_id=data.group_id)

    return ParentAccountOut(
        parent_user_id=parent_user.id,
        login=parent_user.login,
        password=plain_password,
        role=parent_user.role,
        child_ids=data.child_ids
    )


@router.post('/reset-password', response_model=ParentPasswordResetOut)
async def reset_parent_password(
    data: ParentPasswordResetIn,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(403, 'Only educators can reset parent passwords')

    parent = await User.get_by_id(db, data.parent_user_id)
    if not parent or parent.role != 'parent':
        raise HTTPException(404, 'Parent not found')

    links = await ParentChild.list_by_parent(db, parent.id)
    if not links:
        raise HTTPException(404, 'Parent has no assigned group')

    group = await ChildrenGroup.get_by_id(db, links[0].group_id, user_id=me.id)
    if not group:
        raise HTTPException(403, 'This parent does not belong to your group')

    plain_password = generate_password()
    await User.update_password(db, parent, Hasher.hash_it(plain_password), must_change_password=True)

    return ParentPasswordResetOut(
        parent_user_id=parent.id,
        login=parent.login,
        password=plain_password
    )


@router.patch('/me', response_model=ParentProfileOut)
async def update_my_profile(
    data: ParentProfileUpdate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'parent':
        raise HTTPException(403, 'Only parents can update their own profile')

    updated = await User.update_profile(db, me, data.firstname, data.lastname)

    return ParentProfileOut(
        id=updated.id,
        firstname=updated.firstname,
        lastname=updated.lastname,
        login=updated.login
    )


@router.post('/{parent_user_id}/add-children', response_model=ParentChildrenOut)
async def add_children_to_parent(
    parent_user_id: int,
    data: ParentChildrenUpdate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(403, 'Only educators can manage parent accounts')

    parent = await User.get_by_id(db, parent_user_id)
    if not parent or parent.role != 'parent':
        raise HTTPException(404, 'Parent not found')

    existing_links = await ParentChild.list_by_parent(db, parent_user_id)
    if not existing_links:
        raise HTTPException(400, 'Parent has no group assigned yet')

    group_id = existing_links[0].group_id
    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(403, 'This parent does not belong to your group')

    existing_child_ids = {l.child_id for l in existing_links}

    for child_id in data.child_ids:
        child = await Child.get_by_id(db, child_id)
        if not child or child.group_id != group_id:
            raise HTTPException(404, f'Child {child_id} not found in this group')
        if child_id in existing_child_ids:
            raise HTTPException(409, f'Child {child_id} is already assigned to this parent')
        taken = await ParentChild.get_by_child(db, child_id)
        if taken:
            raise HTTPException(409, f'Child {child_id} already has a parent assigned')
        await ParentChild.create(db, parent_user_id=parent_user_id, child_id=child_id, group_id=group_id)

    all_links = await ParentChild.list_by_parent(db, parent_user_id)

    return ParentChildrenOut(
        parent_user_id=parent.id,
        login=parent.login,
        child_ids=[l.child_id for l in all_links]
    )


@router.delete('/{parent_user_id}/remove-children', status_code=204)
async def remove_children_from_parent(
    parent_user_id: int,
    data: ParentChildrenUpdate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(403, 'Only educators can manage parent accounts')

    parent = await User.get_by_id(db, parent_user_id)
    if not parent or parent.role != 'parent':
        raise HTTPException(404, 'Parent not found')

    existing_links = await ParentChild.list_by_parent(db, parent_user_id)
    if not existing_links:
        raise HTTPException(404, 'Parent has no assigned children')

    group_id = existing_links[0].group_id
    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(403, 'This parent does not belong to your group')

    existing_child_ids = {l.child_id for l in existing_links}

    for child_id in data.child_ids:
        if child_id not in existing_child_ids:
            raise HTTPException(404, f'Child {child_id} is not assigned to this parent')
        await ParentChild.delete_by_child(db, child_id)

    return


@router.delete('/{parent_user_id}', status_code=204)
async def delete_parent_account(
    parent_user_id: int,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(403, 'Only educators can delete parent accounts')

    parent = await User.get_by_id(db, parent_user_id)
    if not parent or parent.role != 'parent':
        raise HTTPException(404, 'Parent not found')

    links = await ParentChild.list_by_parent(db, parent_user_id)
    if links:
        group = await ChildrenGroup.get_by_id(db, links[0].group_id, user_id=me.id)
        if not group:
            raise HTTPException(403, 'This parent does not belong to your group')

    # CASCADE on users.id → deletes parent_children + parent_notes automatically
    await db.delete(parent)
    await db.commit()
    return

@router.get('/me/details')
async def get_my_details(
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'parent':
        raise HTTPException(403, 'Only parents can access this endpoint')

    links = await ParentChild.list_by_parent(db, me.id)

    children = []
    for link in links:
        child = await Child.get_by_id(db, link.child_id)
        if child:
            children.append({
                "child_id": child.id,
                "first_name": child.first_name,
                "last_name": child.last_name,
                "full_name": f"{child.first_name} {child.last_name}"  # // NEW
            })

    return {
        "parent_id": me.id,
        "firstname": me.firstname,
        "lastname": me.lastname,
        "full_name": f"{me.firstname} {me.lastname}",  # // NEW
        "children": children
    }