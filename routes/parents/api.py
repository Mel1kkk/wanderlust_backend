from fastapi import APIRouter, Depends, HTTPException, status
from secrets import choice
from string import ascii_letters, digits
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from utils.facades.Hasher import Hasher
from entities.user.entity import User
from entities.children_group.entity import ChildrenGroup
from entities.parent_account.types import (
    ParentAccountCreate,
    ParentAccountOut,
    ParentPasswordResetIn,
    ParentPasswordResetOut
)

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
        raise HTTPException(status_code=403, detail='Only educators can create parent accounts')

    group = await ChildrenGroup.get_by_id(db, data.group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    if group.parent_user_id is not None:
        raise HTTPException(status_code=409, detail='Parent account already exists for this group')

    existing_user = await User.get_by_login(db, data.login)
    if existing_user:
        raise HTTPException(status_code=409, detail='This login already taken')

    plain_password = generate_password()
    parent_user = await User.new_parent(
        db=db,
        login=data.login,
        password_hash=Hasher.hash_it(plain_password)
    )

    group = await ChildrenGroup.attach_parent(db, group, parent_user.id)

    return ParentAccountOut(
        group_id=group.id,
        parent_user_id=parent_user.id,
        login=parent_user.login,
        password=plain_password,
        role=parent_user.role
    )


@router.post('/reset-password', response_model=ParentPasswordResetOut)
async def reset_parent_password(
    data: ParentPasswordResetIn,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can reset parent password')

    group = await ChildrenGroup.get_by_id(db, data.group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')

    if group.parent_user_id is None:
        raise HTTPException(status_code=404, detail='Parent account not found')

    parent_user = await User.get_by_id(db, group.parent_user_id)

    if parent_user.role != 'parent':
        raise HTTPException(status_code=400, detail='Linked user is not parent')

    plain_password = generate_password()
    await User.update_password(
        db=db,
        user=parent_user,
        password_hash=Hasher.hash_it(plain_password),
        must_change_password=True
    )

    return ParentPasswordResetOut(
        group_id=group.id,
        parent_user_id=parent_user.id,
        login=parent_user.login,
        password=plain_password
    )