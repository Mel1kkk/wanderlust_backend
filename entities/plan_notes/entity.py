from sqlalchemy import Column, Integer, Text, ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.db import BaseEntity


class PlanNote(BaseEntity):
    __tablename__ = "plan_notes"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("children_groups.id", ondelete="CASCADE"), unique=True, nullable=False)

    plan = Column(Text, nullable=False)
    teacher_notes = Column(Text, nullable=False)

    @classmethod
    async def upsert(cls, db: AsyncSession, group_id: int, plan: str, teacher_notes: str):

        result = await db.execute(
            select(cls).where(cls.group_id == group_id)
        )
        note = result.scalars().first()

        if note:
            note.plan = plan
            note.teacher_notes = teacher_notes
        else:
            note = cls(
                group_id=group_id,
                plan=plan,
                teacher_notes=teacher_notes
            )
            db.add(note)

        await db.commit()
        await db.refresh(note)

        return note

    @classmethod
    async def get_by_group(cls, db: AsyncSession, group_id: int):
        result = await db.execute(
            select(cls).where(cls.group_id == group_id)
        )
        return result.scalars().first()