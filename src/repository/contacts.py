from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact
from src.schemas.contact import ContactUpdateSchema, ContactCreateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contacts = await db.execute(stmt)
    return contacts.scalar_one_or_none()


async def create_contact(body: ContactCreateSchema, db: AsyncSession):
    try:
        contact = Contact(**body.model_dump(exclude_unset=True))
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    except SQLAlchemyError as err:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create contact")


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(first_name: str, last_name: str, email: str, db: AsyncSession):
    query = select(Contact)

    if first_name:
        query = query.filter(Contact.first_name == first_name)
    if last_name:
        query = query.filter(Contact.last_name == last_name)
    if email:
        query = query.filter(Contact.email == email)

    contacts = await db.execute(query)
    return contacts.scalars().all()
