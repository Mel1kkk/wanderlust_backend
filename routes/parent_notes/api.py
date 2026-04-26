from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from entities.user.entity import User
from entities.children_group.entity import ChildrenGroup
from entities.child.entity import Child
from entities.parent_note.entity import ParentNote
from entities.parent_note.types import ParentNoteCreate, ParentNoteOut, ParentNoteUpdate
from entities.parent_children.entity import ParentChild

router = APIRouter()


async def build_note_out(note: ParentNote, db: AsyncSession) -> ParentNoteOut:
    child = await Child.get_by_id(db, note.child_id)
    about_who = f"{child.first_name} {child.last_name}" if child else "Unknown"
    return ParentNoteOut(
        id=note.id,
        group_id=note.group_id,
        parent_user_id=note.parent_user_id,
        parent_name=note.parent_name,
        child_id=note.child_id,
        about_who=about_who,
        parent_note=note.parent_note
    )


@router.post('', response_model=ParentNoteOut)
async def create_parent_note(
    data: ParentNoteCreate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'parent':
        raise HTTPException(403, 'Only parents can create notes')

    links = await ParentChild.list_by_parent(db, me.id)
    if not links:
        raise HTTPException(404, 'No children assigned to your account')

    child_ids = {l.child_id for l in links}
    if data.child_id not in child_ids:
        raise HTTPException(403, 'This child is not assigned to your account')

    group_id = next(l.group_id for l in links if l.child_id == data.child_id)

    note = await ParentNote.create(
        db,
        group_id=group_id,
        parent_user_id=me.id,
        parent_name=f"{me.firstname} {me.lastname}",
        child_id=data.child_id,
        parent_note=data.parent_note
    )

    return await build_note_out(note, db)


@router.get('/my', response_model=list[ParentNoteOut])
async def get_my_notes(
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'parent':
        raise HTTPException(403, 'Only parents can view their own notes')

    notes = await ParentNote.list_by_parent(db, me.id)
    return [await build_note_out(n, db) for n in notes]


@router.get('/group/{group_id}', response_model=list[ParentNoteOut])
async def get_group_parent_notes(
    group_id: int,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'educator':
        raise HTTPException(403, 'Only educators can view all group notes')

    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(404, 'Group not found')

    notes = await ParentNote.list_by_group(db, group_id)
    return [await build_note_out(n, db) for n in notes]


@router.patch('/{note_id}', response_model=ParentNoteOut)
async def update_parent_note(
    note_id: int,
    data: ParentNoteUpdate,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    if me.role != 'parent':
        raise HTTPException(403, 'Only parents can edit their notes')

    note = await ParentNote.get_by_id(db, note_id)
    if not note:
        raise HTTPException(404, 'Note not found')

    if note.parent_user_id != me.id:
        raise HTTPException(403, 'You can only edit your own notes')

    updated = await ParentNote.update_note_text(db, note_id, data.parent_note)
    return await build_note_out(updated, db)


@router.delete('/{note_id}', status_code=204)
async def delete_parent_note(
    note_id: int,
    db: AsyncSession = Depends(connect_db),
    me: User = Depends(Auth.authenticate_me)
):
    note = await ParentNote.get_by_id(db, note_id)
    if not note:
        raise HTTPException(404, 'Note not found')

    if me.role == 'parent':
        if note.parent_user_id != me.id:
            raise HTTPException(403, 'You can only delete your own notes')
    elif me.role == 'educator':
        group = await ChildrenGroup.get_by_id(db, note.group_id, user_id=me.id)
        if not group:
            raise HTTPException(403, 'Note does not belong to your group')
    else:
        raise HTTPException(403, 'Forbidden')

    await ParentNote.delete_note(db, note_id)
    return