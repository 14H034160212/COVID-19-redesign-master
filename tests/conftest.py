import os
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from covid import create_app
from covid.adapters import memory_repository, database_repository
from covid.adapters.orm import metadata, map_model_to_tables
from covid.adapters.memory_repository import MemoryRepository
from covid.adapters.unit_of_work import InMemoryUnitOfWork


TEST_DATABASE_URI = 'sqlite://'
TEST_DATA_PATH = 'C:\\Users\\ianwo\\OneDrive\\Documents\\PythonDev\\repo 02.07.2020\\COVID-19\\tests\\data'


@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository()
    memory_repository.populate(TEST_DATA_PATH, repo)
    return repo


@pytest.fixture
def in_memory_uow():
    repo = MemoryRepository()
    memory_repository.populate(TEST_DATA_PATH, repo)
    return InMemoryUnitOfWork(repo)


@pytest.fixture
def empty_session():
    engine = create_engine(TEST_DATABASE_URI)
    metadata.create_all(engine)
    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    yield session_factory()
    metadata.drop_all(engine)
    clear_mappers()


@pytest.fixture
def session():
    clear_mappers()
    engine = create_engine(TEST_DATABASE_URI)
    metadata.create_all(engine)
    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    database_repository.populate(engine, TEST_DATA_PATH)
    yield session_factory()
    metadata.drop_all(engine)
    clear_mappers()


@pytest.fixture
def session_factory():
    clear_mappers()
    engine = create_engine(TEST_DATABASE_URI)
    metadata.create_all(engine)
    database_repository.populate(engine, TEST_DATA_PATH)
    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    yield session_factory
    metadata.drop_all(engine)
    clear_mappers()


@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,                                # Set to True during testing.
        'REPOSITORY': 'database',                       # Set to 'memory' or 'database' depending on desired repository.
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI,   # Use an in-memory SQLite database for testing 'database' repo.
        'TEST_DATA_PATH': TEST_DATA_PATH,               # Path for loading test data into the repository.
        'WTF_CSRF_ENABLED': False                       # test_client will not send a CSRF token, so disable validation.
    })

    return my_app.test_client()


class AuthenticationManager:
    def __init__(self, client):
        self._client = client

    def login(self, username='thorke', password='cLQ^C#oFXloS'):
        return self._client.post(
            'authentication/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthenticationManager(client)
