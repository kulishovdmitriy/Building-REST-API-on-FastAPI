import datetime
import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact, User
from src.schemas.contact import ContactCreateSchema, ContactUpdateSchema
from src.repository.contacts import (
    get_contact,
    get_contacts,
    get_all_contacts,
    create_contact,
    delete_contact,
    update_contact,
)


class TestAsyncTodo(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username="test_user", password="qwerty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contact(self):

        mock_contact = Contact(
            id=1,
            first_name="test_title",
            last_name="test_description",
            email="test@com.ua",
            user=self.user,
        )

        self.session.execute.return_value.scalar_one_or_none.return_value = mock_contact
        result = await get_contact(1, self.session, self.user)
        self.assertEqual(await result, mock_contact)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                first_name="test_title_1",
                last_name="test_description_1",
                email="test@com.ua",
                user=self.user,
            ),
            Contact(
                id=2,
                first_name="test_title_2",
                last_name="test_description_2",
                email="test2@com.ua",
                user=self.user,
            ),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit, offset, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                first_name="test_title_1",
                last_name="test_description_1",
                email="test@com.ua",
                user=self.user,
            ),
            Contact(
                id=2,
                first_name="test_title_2",
                last_name="test_description_2",
                email="test2@com.ua",
                user=self.user,
            ),
        ]
        mocked_contacts = Mock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_create_contacts(self):
        birthday = datetime.datetime.strptime("12.05.1996", "%d.%m.%Y")
        body = ContactCreateSchema(
            first_name="test_title",
            last_name="test_description",
            email="test2@com.ua",
            phone_number="0661122333",
            birthday=birthday,
        )
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)

    async def test_update_contacts(self):
        birthday = datetime.datetime.strptime("12.05.1996", "%d.%m.%Y")
        body = ContactUpdateSchema(
            first_name="test_title",
            last_name="test_description",
            email="test2@com.ua",
            phone_number="0661122333",
            birthday=birthday,
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            first_name="test_title",
            last_name="test_description",
            email="test2@com.ua",
            phone_number="0661122333",
            birthday=birthday,
            user=self.user,
        )
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.birthday, body.birthday)

    async def test_delete_contacts(self):
        birthday = datetime.datetime.strptime("12.05.1996", "%d.%m.%Y")
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            first_name="test_title",
            last_name="test_description",
            email="test2@com.ua",
            phone_number="0661122333",
            birthday=birthday,
            user=self.user,
        )
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)
