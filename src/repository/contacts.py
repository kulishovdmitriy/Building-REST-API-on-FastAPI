from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact
from src.schemas.contact import ContactUpdateSchema, ContactCreateSchema
from src.database.models import User


async def get_contacts(limit: int, offset: int, db: AsyncSession, current_user: User):
    """
    The get_contacts function returns a list of contacts for the current user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=current_user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_all_contacts function returns a list of all contacts in the database.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify how many rows to skip
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Specify the id of the contact we want to get
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Ensure that the user is only able to access their own contacts
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=current_user)
    contacts = await db.execute(stmt)
    return contacts.scalar_one_or_none()


async def create_contact(
    body: ContactCreateSchema, db: AsyncSession, current_user: User
):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactCreateSchema: Validate the body of the request
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the user that is currently logged in
    :return: A contact object, so the response schema is contactschema
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=current_user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession, current_user: User
):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Specify the contact to update
    :param body: ContactUpdateSchema: Pass in the json body of the request
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Make sure that the user is only able to delete
    :return: The updated contact
    :doc-author: Trelent
    """
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
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Identify the contact to delete
    :param db: AsyncSession: Pass in the database session
    :param current_user: User: Ensure that the user is only able to delete contacts that they own
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The search_contacts function searches for contacts in the database.

    :param first_name: str: Filter the query by first name
    :param last_name: str: Filter the contacts by last name
    :param email: str: Filter the query by email
    :param db: AsyncSession: Pass the database connection to the function
    :param current_user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    query = select(Contact).filter_by(user=current_user)

    if first_name:
        query = query.filter(Contact.first_name == first_name)
    if last_name:
        query = query.filter(Contact.last_name == last_name)
    if email:
        query = query.filter(Contact.email == email)

    contacts = await db.execute(query)
    return contacts.scalars().all()
