from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact
from src.schemas.contact import ContactUpdateSchema, ContactCreateSchema
from src.database.models import User


async def get_contacts(limit: int, offset: int, db: AsyncSession, current_user: User):
    """ """
    stmt = select(Contact).filter_by(user=current_user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, current_user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    contacts = await db.execute(stmt)
    return contacts.scalar_one_or_none()


async def create_contact(
    body: ContactCreateSchema, db: AsyncSession, current_user: User
):
    contact = Contact(**body.model_dump(exclude_unset=True), user=current_user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession, current_user: User
):
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
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


async def delete_contact(contact_id: int, db: AsyncSession, current_user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(
    first_name: str, last_name: str, email: str, db: AsyncSession, current_user: User
):
    query = select(Contact).filter_by(user=current_user)

    if first_name:
        query = query.filter(Contact.first_name == first_name)
    if last_name:
        query = query.filter(Contact.last_name == last_name)
    if email:
        query = query.filter(Contact.email == email)

    contacts = await db.execute(query)
    return contacts.scalars().all()
