from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.contact import (
    ContactCreateSchema,
    ContactResponseSchema,
    ContactUpdateSchema,
)
from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from datetime import datetime, timedelta
from src.database.models import Contact, User, Role
from sqlalchemy import select, cast, Date
from src.servises.auth import auth_service
from src.servises.role import RoleAccess

router = APIRouter(prefix="/contacts", tags=["contacts"])
access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get(
    "/",
    response_model=list[ContactResponseSchema],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """

    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of results returned
    :param ge: Specify the minimum value for a parameter
    :param le: Limit the number of contacts returned to 500
    :param offset: int: Skip the first n records
    :param ge: Specify a minimum value, and the le parameter is used to specify a maximum value
    :param db: AsyncSession: Pass the database connection to the function
    :param current_user: User: Get the current user from the database
    :param : Get the contact id
    :return: A list of contacts

    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, current_user)
    return contacts


@router.get(
    "/all",
    response_model=list[ContactResponseSchema],
    dependencies=[Depends(access_to_route_all)],
)
async def get_all_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """

    The get_all_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of contacts returned to 500
    :param offset: int: Specify the offset of the contacts to be returned
    :param ge: Set the minimum value for the limit parameter
    :param db: AsyncSession: Get the database session
    :param user: User: Get the user who sent the request
    :param : Get the contact by id
    :return: A list of contacts

    """
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    print(contacts)
    return contacts


@router.get(
    "/search",
    response_model=list[ContactResponseSchema],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def search_contacts(
    first_name: str = Query(None),
    last_name: str = Query(None),
    email: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """

    The search_contacts function searches for contacts in the database.

    :param first_name: str: Receive the first name of a contact
    :param last_name: str: Filter the contacts by last name
    :param email: str: Search for a contact by email
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :param : Specify the type of data that is expected in the request body
    :return: A list of contacts

    """
    contacts = await repositories_contacts.search_contacts(
        first_name, last_name, email, db, current_user
    )
    return contacts


@router.get(
    "/birthdays",
    response_model=list[ContactResponseSchema],
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """

    The get_upcoming_birthdays function returns a list of contacts whose birthday is within the next week.

    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :param : Get the database session
    :return: A list of contacts with a birthday between today and the next week

    """
    today = datetime.today().date()
    next_week = (datetime.today() + timedelta(days=7)).date()

    query = (
        select(Contact)
        .filter_by(user=current_user)
        .filter(cast(Contact.birthday, Date).between(today, next_week))
    )
    contacts = await db.execute(query)
    return contacts.scalars().all()


@router.get(
    "/{contact_id}",
    response_model=ContactResponseSchema,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """

    The get_contact function is a GET request that returns the contact with the given ID.
    If no such contact exists, it raises an HTTP 404 error.

    :param contact_id: int: Get the contact_id from the url
    :param db: AsyncSession: Get a database connection
    :param current_user: User: Get the current user from the database
    :param : Get the contact id from the url
    :return: A contact object, which is a pydantic model

    """
    contact = await repositories_contacts.get_contact(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post(
    "/",
    response_model=ContactResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def create_contact(
    body: ContactCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """

    The create_contact function creates a new contact in the database.

    :param body: ContactCreateSchema: Validate the request body
    :param db: AsyncSession: Get the database connection
    :param current_user: User: Get the user who is currently logged in
    :param : Get the contact id from the url
    :return: A contact object

    """
    contact = await repositories_contacts.create_contact(body, db, current_user)
    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_contact(
    contact_id: int,
    body: ContactUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """

    The update_contact function updates a contact in the database.

    :param contact_id: int: Get the contact id from the url
    :param body: ContactUpdateSchema: Get the data from the request body
    :param db: AsyncSession: Pass the database session to the repository
    :param current_user: User: Get the user who is currently logged in
    :param : Get the contact id
    :return: A contact object

    """
    contact = await repositories_contacts.update_contact(
        contact_id, body, db, current_user
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """

    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact to be deleted
    :param db: AsyncSession: Pass the database session to the repository
    :param current_user: User: Get the user id from the current_user object
    :param : Specify the contact id of the contact to be deleted
    :return: None, which means that the api endpoint will return an empty response

    """
    await repositories_contacts.delete_contact(contact_id, db, current_user)
    return None
