"""Initialize Flask app."""

from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.pool import NullPool, StaticPool

from covid.adapters import memory_repository, database_repository
from covid.adapters.orm import metadata, map_model_to_tables
from covid.adapters.unit_of_work import SqlAlchemyUnitOfWork, InMemoryUnitOfWork

import covid.adapters.unit_of_work as uow

	
def create_app(test_config=None):
    """Construct the core application."""

    # Create the Flask app object.
    app = Flask(__name__)

    # Configure the app from configuration-file settings.
    app.config.from_object('config.Config')
    data_path = 'covid\\adapters\\data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings.
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']

    if app.config['REPOSITORY'] == 'memory':
        # Create the InMemoryUnitOfWork and MemoryRepository implementations for a memory-based repository.
        repo = memory_repository.MemoryRepository()
        uow.uow_instance = InMemoryUnitOfWork(repo)
        memory_repository.populate(data_path, repo)

    elif app.config['REPOSITORY'] == 'database':
        # Configure database.
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']

        if database_uri == 'sqlite://':
            # In-memory database.
            pool = StaticPool
        else:
            # File-based database.
            pool = NullPool

        engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=pool)

        if app.config['TESTING'] or len(engine.table_names()) == 0:
            # For testing, or first-time use of the web application, reinitialise the database.
            clear_mappers()
            metadata.create_all(engine)                        # Conditionally create database tables.
            for table in reversed(metadata.sorted_tables):     # Remove any data from the tables.
                engine.execute(table.delete())
            database_repository.populate(engine, data_path)    # Populate the database with fresh data.

        # Create the database session factory and unit of work objects.
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        uow.uow_instance = SqlAlchemyUnitOfWork(session_factory)

        # Generate mappings that map domain model classes to the database tables.
        map_model_to_tables()

    # Build the application - these steps require an application context.
    with app.app_context():
        # Register blueprints.
        from .home import home
        app.register_blueprint(home.home_blueprint)

        from .news import news
        app.register_blueprint(news.news_blueprint)

        from .authentication import authentication
        app.register_blueprint(authentication.authentication_blueprint)

        from .utilities import utilities
        app.register_blueprint(utilities.utilities_blueprint)

        # Register a tear-down method that will be called after each request has been processed.
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            if isinstance(uow.uow_instance, SqlAlchemyUnitOfWork):
                uow.uow_instance.close_current_session()

    return app
