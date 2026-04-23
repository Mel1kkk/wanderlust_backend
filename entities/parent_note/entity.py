from sqlalchemy import Column, Integer, Text, ForeignKey, String, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from utils.db import BaseEntity

class ParentNote(BaseEntity):
    __tablename__ = 'parent_notes'

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('children_groups.id', ondelete='CASCADE'), nullable=False)
    parent_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_name = Column(String(100), nullable=False)
    parent_note = Column(Text, nullable=False)

    @classmethod
    async def create(cls, db: AsyncSession, group_id: int, parent_user_id: int, parent_name: str, parent_note: str):
        note = cls(group_id=group_id, parent_user_id=parent_user_id, parent_name=parent_name, parent_note=parent_note)
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return note

    @classmethod
    async def list_by_group(cls, db: AsyncSession, group_id: int):
        result = await db.execute(select(cls).where(cls.group_id == group_id).order_by(cls.id.desc()))
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, note_id: int):
        result = await db.execute(select(cls).where(cls.id == note_id))
        return result.scalars().first()

    @classmethod
    async def update_note_text(cls, db: AsyncSession, note_id: int, new_text: str):
        note = await cls.get_by_id(db, note_id)
        if not note:
            return None
        note.parent_note = new_text
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return note

    @classmethod
    async def delete_note(cls, db: AsyncSession, note_id: int):
        note = await cls.get_by_id(db, note_id)
        if not note:
            return None
        await db.delete(note)
        await db.commit()
        return True