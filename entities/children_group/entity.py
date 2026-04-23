from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import Boolean

from utils.db import BaseEntity


class ChildrenGroup(BaseEntity):
    __tablename__ = 'children_groups'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), unique=True, nullable=True)
    title = Column(String(128), nullable=False)
    age_group = Column(String(32), nullable=False)
    children_count = Column(Integer, default=0)
    general_notes = Column(Text, default='')
    plan = Column(Text, default='No Plan')
    is_completed = Column(Boolean, default=False, nullable=False)

    user = relationship('User', foreign_keys=[user_id], backref='children_groups')
    parent_user = relationship('User', foreign_keys=[parent_user_id])

    has_special_needs = Column(Boolean, default=False, nullable=False)
    special_notes = Column(Text, default='')

    @classmethod
    async def new(
        cls,
        db: AsyncSession,
        user_id: int,
        title: str,
        age_group: str,
        children_count: int = 0,
        general_notes: str = '',
        has_special_needs: bool = False,
        special_notes: str = ''
    ):
        inst = cls(
            user_id=user_id,
            title=title,
            age_group=age_group,
            children_count=children_count,
            general_notes=general_notes,
            has_special_needs=has_special_needs,
            special_notes=special_notes
        )
        db.add(inst)
        await db.flush()
        await db.commit()
        await db.refresh(inst)
        return inst

    # @classmethod
    # async def list_by_user(cls, db: AsyncSession, user_id: int):
    #     result = await db.execute(
    #         select(cls).where(cls.user_id == user_id).order_by(cls.id.desc())
    #     )
    #     return result.scalars().all()

    @classmethod
    async def list_by_user(cls, db: AsyncSession, user_id: int):
        result = await db.execute(
            select(cls)
            .where(cls.user_id == user_id)
            .order_by(cls.has_special_needs.desc(), cls.id.desc())
        )
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: int, user_id: int = None):
        stmt = select(cls).where(cls.id == id)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_by_parent_user_id(cls, db: AsyncSession, parent_user_id: int):
        result = await db.execute(
            select(cls).where(cls.parent_user_id == parent_user_id)
        )
        return result.scalars().first()

    @classmethod
    async def attach_parent(cls, db: AsyncSession, group: 'ChildrenGroup', parent_user_id: int):
        group.parent_user_id = parent_user_id
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group

    @classmethod
    async def update_completed(
        cls,
        db: AsyncSession,
        group: 'ChildrenGroup',
        is_completed: bool
    ):
        group.is_completed = is_completed
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group

    @classmethod
    async def update_plan(
        cls,
        db: AsyncSession,
        group: 'ChildrenGroup',
        new_plan: str
    ):
        group.plan = new_plan
        group.is_completed = False
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group  

 