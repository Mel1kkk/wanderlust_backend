from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db import connect_db
from utils.facades.Auth import Auth
from entities.user.entity import User
from entities.children_group.entity import ChildrenGroup
from entities.parent_note.entity import ParentNote
from entities.parent_note.types import ParentNoteCreate, ParentNoteOut, ParentNoteUpdate

router = APIRouter()

@router.post('', response_model=ParentNoteOut)
async def create_parent_note(data: ParentNoteCreate, db: AsyncSession = Depends(connect_db), me: User = Depends(Auth.authenticate_me)):
    if me.role != 'parent':
        raise HTTPException(status_code=403, detail='Only parents can create notes')
    group = await ChildrenGroup.get_by_parent_user_id(db, me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found for this parent')
    note = await ParentNote.create(db, group.id, me.id, data.parent_name, data.parent_note)
    return ParentNoteOut.from_orm(note)

@router.get('/group/{group_id}', response_model=list[ParentNoteOut])
async def get_group_parent_notes(group_id: int, db: AsyncSession = Depends(connect_db), me: User = Depends(Auth.authenticate_me)):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can view parent notes')
    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    notes = await ParentNote.list_by_group(db, group_id)
    return [ParentNoteOut.from_orm(note) for note in notes]

@router.patch('/{note_id}', response_model=ParentNoteOut)
async def update_parent_note(note_id: int, data: ParentNoteUpdate, db: AsyncSession = Depends(connect_db), me: User = Depends(Auth.authenticate_me)):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can edit notes')
    note = await ParentNote.get_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail='Note not found')
    group = await ChildrenGroup.get_by_id(db, note.group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=403, detail='Note does not belong to your group')
    updated_note = await ParentNote.update_note_text(db, note_id, data.parent_note)
    return ParentNoteOut.from_orm(updated_note)

@router.delete('/{note_id}', status_code=204)
async def delete_parent_note(note_id: int, db: AsyncSession = Depends(connect_db), me: User = Depends(Auth.authenticate_me)):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can delete notes')
    note = await ParentNote.get_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail='Note not found')
    group = await ChildrenGroup.get_by_id(db, note.group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=403, detail='Note does not belong to your group')
    await ParentNote.delete_note(db, note_id)
    return

@router.delete('/group/{group_id}', status_code=204)
async def delete_all_parent_notes(group_id: int, db: AsyncSession = Depends(connect_db), me: User = Depends(Auth.authenticate_me)):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can delete notes')
    group = await ChildrenGroup.get_by_id(db, group_id, user_id=me.id)
    if not group:
        raise HTTPException(status_code=404, detail='Group not found')
    notes = await ParentNote.list_by_group(db, group_id)
    for note in notes:
        await ParentNote.delete_note(db, note.id)
    return

@router.delete('/parents/{parent_user_id}', status_code=204)
async def delete_parent_account(parent_user_id: int, db: AsyncSession = Depends(connect_db), me: User = Depends(Auth.authenticate_me)):
    if me.role != 'educator':
        raise HTTPException(status_code=403, detail='Only educators can delete parents')
    parent = await User.get_by_id(db, parent_user_id)
    if not parent or parent.role != 'parent':
        raise HTTPException(status_code=404, detail='Parent not found')
    group = await ChildrenGroup.get_by_parent_user_id(db, parent.id)
    if not group or group.user_id != me.id:
        raise HTTPException(status_code=403, detail='Parent does not belong to your group')
    await db.delete(parent)
    await db.commit()
    return