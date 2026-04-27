from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from utils.db import BaseEntity
import enum


class GenderEnum(str, enum.Enum):
    boy = 'boy'
    girl = 'girl'


class Child(BaseEntity):
    __tablename__ = 'children'

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey('children_groups.id', ondelete='CASCADE'), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)

    note_about_child = Column(Text, nullable=False, default="No notes about this child")

    @classmethod
    async def create(cls, db: AsyncSession, group_id: int, first_name: str, last_name: str, age: int, gender: GenderEnum, note_about_child: str):
        existing = await db.execute(
            select(cls).where(
                and_(
                    cls.group_id == group_id,
                    cls.first_name == first_name,
                    cls.last_name == last_name
                )
            )
        )
        if existing.scalars().first():
            return None

        child = cls(
            group_id=group_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            note_about_child=note_about_child
        )
        db.add(child)
        await db.commit()
        await db.refresh(child)
        return child

    @classmethod
    async def update_note(cls, db: AsyncSession, child: 'Child', new_note: str):  # // NEW METHOD
        child.note_about_child = new_note
        db.add(child)
        await db.commit()
        await db.refresh(child)
        return child

    @classmethod
    async def list_by_group(cls, db: AsyncSession, group_id: int):
        result = await db.execute(
            select(cls).where(cls.group_id == group_id).order_by(cls.id.desc())
        )
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, child_id: int):
        result = await db.execute(select(cls).where(cls.id == child_id))
        return result.scalars().first()

    @classmethod
    async def delete(cls, db: AsyncSession, child: 'Child'):
        await db.delete(child)
        await db.commit()