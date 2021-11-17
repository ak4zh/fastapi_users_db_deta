=====================
FastAPI Users DB Deta
=====================


.. image:: https://img.shields.io/pypi/v/fastapi_users_db_deta.svg
        :target: https://pypi.python.org/pypi/fastapi_users_db_deta

.. image:: https://img.shields.io/travis/ak4zh/fastapi_users_db_deta.svg
        :target: https://travis-ci.com/ak4zh/fastapi_users_db_deta

.. image:: https://readthedocs.org/projects/fastapi-users-db-deta/badge/?version=latest
        :target: https://fastapi-users-db-deta.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Sub-package for Deta Base support in FastAPI Users.


* Free software: MIT license
* Documentation: https://fastapi-users-db-deta.readthedocs.io.


Installation
------------

To install FastAPI Users DB Deta in a project::

    pip install -U fastapi_users_db_deta


Usage
-----

Project structure::

    .
    ├── users
    │   ├── __init__.py
    │   ├── models.py
    │   ├── manager.py
    └── main.py

users/models.py::

    from fastapi_users import models
    from fastapi_users.models import BaseOAuthAccountMixin


    class User(models.BaseUser, BaseOAuthAccountMixin):
        pass


    class UserCreate(models.BaseUserCreate):
        pass


    class UserUpdate(models.BaseUserUpdate):
        pass


    class UserDB(User, models.BaseUserDB):
        pass

users/manager.py::

    from typing import Optional

    import deta
    from fastapi import Depends, Request
    from fastapi_users import BaseUserManager, FastAPIUsers
    from fastapi_users.authentication import JWTAuthentication, CookieAuthentication
    from fastapi_users_db_deta import DetaBaseUserDatabase

    from users.models import UserDB, UserCreate, UserUpdate, User

    SECRET = 'secret'
    DETA_PROJECT_KEY = 'deta_project_key'
    DATABASE = deta.Deta(DETA_PROJECT_KEY)
    UserBase = DATABASE.Base('users')
    OAuthBase = DATABASE.Base('oauth_accounts')


    class UserManager(BaseUserManager[UserCreate, UserDB]):
        user_db_model = UserDB
        reset_password_token_secret = SECRET
        verification_token_secret = SECRET


    async def get_user_db():
        yield DetaBaseUserDatabase(UserDB, UserBase().db, OAuthBase().db)


    async def get_user_manager(user_db=Depends(get_user_db)):
        yield UserManager(user_db)


    jwt_authentication = JWTAuthentication(
        secret=SECRET, lifetime_seconds=5, tokenUrl="auth/jwt/login"
    )
    cookie_authentication = CookieAuthentication(
        secret=SECRET, lifetime_seconds=5, cookie_name='userAuthToken'
    )

    fastapi_users_app = FastAPIUsers(
        get_user_manager,
        [jwt_authentication, cookie_authentication],
        User,
        UserCreate,
        UserUpdate,
        UserDB,
    )

    current_active_user = fastapi_users_app.current_user(active=True)


main.py::

    from fastapi import FastAPI

    from users.manager import cookie_authentication, jwt_authentication, fastapi_users_app

    app = FastAPI()

    # include cookie auth router
    app.include_router(
        fastapi_users_app.get_auth_router(
            cookie_authentication,
        ), prefix="/auth/cookie", tags=["auth"]
    )

    # include jwt auth router
    app.include_router(
        fastapi_users_app.get_auth_router(
            jwt_authentication,
        ), prefix="/auth/jwt", tags=["auth"]
    )

    app.include_router(
        fastapi_users_app.get_register_router(), prefix="/auth", tags=["auth"]
    )

    app.include_router(
        fastapi_users_app.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )

    app.include_router(
        fastapi_users_app.get_verify_router(),
        prefix="/auth",
        tags=["auth"],
    )

    app.include_router(
        fastapi_users_app.get_users_router(), prefix="/users", tags=["users"]
    )

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
