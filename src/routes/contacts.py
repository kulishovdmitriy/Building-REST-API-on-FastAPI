from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.contact import ContactCreateSchema, ContactResponseSchema, ContactUpdateSchema
from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from datetime import datetime, timedelta
from src.database.models import Contact, User, Role
from sqlalchemy import select, cast, Date
from src.servises.auth import auth_service
from src.servises.role import RoleAccess

router = APIRouter(prefix="/contacts", tags=["contacts"])
access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get('/', response_model=list[ContactResponseSchema])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db, current_user)
    return contacts


@router.get("/all", response_model=list[ContactResponseSchema], dependencies=[Depends(access_to_route_all)])
async def get_all_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    print(contacts)
    return contacts


@router.get('/search', response_model=list[ContactResponseSchema])
async def search_contacts(
        first_name: str = Query(None),
        last_name: str = Query(None),
        email: str = Query(None),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    contacts = await repositories_contacts.search_contacts(first_name, last_name, email, db, current_user)
    return contacts


@router.get('/birthdays', response_model=list[ContactResponseSchema])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    today = datetime.today().date()
    next_week = (datetime.today() + timedelta(days=7)).date()

    query = select(Contact).filter_by(user=current_user).filter(
        cast(Contact.birthday, Date).between(today, next_week)
    )
    contacts = await db.execute(query)
    return contacts.scalars().all()


@router.get('/{contact_id}', response_model=ContactResponseSchema)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contact(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post('/', response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreateSchema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.create_contact(body, db, current_user)
    return contact


@router.put('/{contact_id}', response_model=ContactResponseSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.update_contact(contact_id, body, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    await repositories_contacts.delete_contact(contact_id, db, current_user)
    return None
