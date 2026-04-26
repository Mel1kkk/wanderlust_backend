from sqlalchemy import Column, Integer, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.db import BaseEntity


class ParentChild(BaseEntity):
    __tablename__ = 'parent_children'

    id = Column(Integer, primary_key=True, index=True)
    parent_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    child_id = Column(Integer, ForeignKey('children.id', ondelete='CASCADE'), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey('children_groups.id', ondelete='CASCADE'), nullable=False)

    @classmethod
    async def create(cls, db: AsyncSession, parent_user_id: int, child_id: int, group_id: int):
        link = cls(parent_user_id=parent_user_id, child_id=child_id, group_id=group_id)
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link

    @classmethod
    async def get_by_child(cls, db: AsyncSession, child_id: int):
        result = await db.execute(select(cls).where(cls.child_id == child_id))
        return result.scalars().first()

    @classmethod
    async def list_by_parent(cls, db: AsyncSession, parent_user_id: int):
        result = await db.execute(select(cls).where(cls.parent_user_id == parent_user_id))
        return result.scalars().all()

    @classmethod
    async def list_by_group(cls, db: AsyncSession, group_id: int):
        result = await db.execute(select(cls).where(cls.group_id == group_id))
        return result.scalars().all()

    @classmethod
    async def delete_by_child(cls, db: AsyncSession, child_id: int):
        link = await cls.get_by_child(db, child_id)
        if link:
            await db.delete(link)
            await db.commit()

    @classmethod
    async def delete_all_by_parent(cls, db: AsyncSession, parent_user_id: int):
        links = await cls.list_by_parent(db, parent_user_id)
        for link in links:
            await db.delete(link)
        if links:
            await db.commit()