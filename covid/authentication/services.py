from werkzeug.security import generate_password_hash, check_password_hash

from covid.adapters import unit_of_work
from covid.domain.model import User


class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


def add_user(username: str, password: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        # Check that the given username is available.
        user = uow.repo.get_user(username)
        if user is not None:
            raise NameNotUniqueException

        # Encrypt password so that the database doesn't store passwords 'in the clear'.
        password_hash = generate_password_hash(password)

        # Create and store the new User, with password encrypted.
        user = User(username, password_hash)
        uow.repo.add_user(user)
        uow.commit()


def get_user(username: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        user = uow.repo.get_user(username)
        if user is None:
            raise UnknownUserException

        return user_to_dict(user)


def authenticate_user(username: str, password: str, uow: unit_of_work.AbstractUnitOfWork):
    authenticated = False

    with uow:
        user = uow.repo.get_user(username)
        if user is not None:
            authenticated = check_password_hash(user.password, password)
        if not authenticated:
            raise AuthenticationException


# ===================================================
# Functions to convert model entities to dictionaries
# ===================================================

def user_to_dict(user: User):
    user_dict = {
        'username': user.username,
        'password': user.password
    }
    return user_dict
