"""Top-level package for FastAPI Users DB Deta."""

__author__ = """Akash Agarwal"""
__email__ = 'agwl.akash@gmail.com'
__version__ = '__version__ = '0.2.1''

from typing import Optional, Type

import deta
from fastapi_users.manager import UserNotExists
from pydantic import UUID4

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import UD


class DetaBaseUserDatabase(BaseUserDatabase[UD]):
    """
    Database adapter for Deta Base.
    :param user_db_model: Pydantic model of a DB representation of a user.
    :param user_base: deta.Deta.AsyncBase() to store user data
    :param oauth_account_base: deta.Deta.AsyncBase() to store oauth accounts with user_id field
    """

    def __init__(
        self, user_db_model: Type[UD], user_base: deta.Deta.AsyncBase, oauth_account_base: deta.Deta.AsyncBase
    ):
        super().__init__(user_db_model)
        self.user_base = user_base
        self.oauth_account_base = oauth_account_base

    async def get(self, id: UUID4) -> Optional[UD]:
        """Get a single user by id."""
        user = await self.user_base.get(key=str(id))
        return self.user_db_model(**user) if user else None

    async def get_by_email(self, email: str) -> Optional[UD]:
        """Get a single user by email."""
        user = await self.user_base.fetch(query=dict(email=email)).items
        return self.user_db_model(**user[0]) if user else None

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UD]:
        """Get a single user by OAuth account id."""
        user = None
        oauth_accounts = await self.oauth_account_base.fetch(query={
                "oauth_name": oauth,
                "account_id": account_id,
            }).items
        if oauth_accounts:
            user = await self.user_base.get(key=oauth_accounts[0]['user_id'])
        if not user:
            raise UserNotExists()
        return self.user_db_model(**user)

    async def update_oauth_accounts(self, user_id: str, oauth_accounts: list):
        if oauth_accounts and self.oauth_account_base:
            for oauth_account in oauth_accounts:
                oauth_account['user_id'] = user_id
                existing = await self.oauth_account_base.fetch(
                    query=dict(oauth_name=oauth_account['oauth_name'], account_id=oauth_account['account_id'])
                ).items
                await self.oauth_account_base.put(
                    oauth_account, key=existing[0]['key'] if existing else str(oauth_account['id'])
                )

    async def create(self, user: UD) -> UD:
        """Create a user."""
        user_id = str(user.id)  # convert UUID4 to str
        user_dict = user.dict()
        oauth_accounts = user_dict.pop("oauth_accounts", None)
        user_dict['id'] = user_id  # replace UUID4 object with str
        user_dict["email"] = user_dict["email"].lower()
        if await self.get_by_email(user_dict["email"]):
            raise ValueError()
        await self.user_base.insert(data=user_dict, key=user_id)
        await self.update_oauth_accounts(user_id, oauth_accounts)
        return user

    async def update(self, user: UD) -> UD:
        """Update a user."""
        key = str(user.id)  # convert UUID4 to str
        user_dict = user.dict()
        user_dict['id'] = key  # replace UUID4 object with str
        oauth_accounts = user_dict.pop("oauth_accounts", None)
        user_dict["email"] = user_dict["email"].lower()
        await self.user_base.put(data=user_dict, key=key)
        await self.update_oauth_accounts(key, oauth_accounts)
        return user

    async def delete(self, user: UD) -> None:
        """Delete a user."""
        key = str(user.id)
        # delete all oauth accounts
        oauth_accounts = await self.oauth_account_base.fetch(query=dict(user_id=key)).items
        for oauth_account in oauth_accounts:
            await self.oauth_account_base.delete(str(oauth_account.id))
        # delete the actual user
        await self.user_base.delete(key=key)
