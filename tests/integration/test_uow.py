import pytest

from datetime import date

from covid.domain.model import Article
from covid.adapters import unit_of_work
from covid.domain import model


def make_article(new_article_date):
    article = Article(
        new_article_date,
        'Coronavirus travel restrictions: Self-isolation deadline pushed back to give airlines breathing room',
        'The self-isolation deadline has been pushed back',
        'https://www.nzherald.co.nz/business/news/article.cfm?c_id=3&objectid=12316800',
        'https://th.bing.com/th/id/OIP.0lCxLKfDnOyswQCF9rcv7AHaCz?w=344&h=132&c=7&o=5&pid=1.7'
    )
    return article


def test_uow_can_retrieve_an_article_and_add_a_comment_to_it(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        # Fetch Article and User.
        article = uow.repo.get_article(5)
        author = uow.repo.get_user('thorke')

        # Create a new Comment, connecting it to the Article and User.
        comment = model.make_comment('First death in Australia', author, article)

        # Commit the changes.
        uow.commit()

    # Check that a Comment has been added that links to the Article and User.
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        # Fetch Article and User.
        article = uow.repo.get_article(5)
        author = uow.repo.get_user('thorke')

        assert comment in article.comments
        assert comment in author.comments


def test_uow_rolls_back_uncommited_work_by_default(session_factory):
    new_article_date = date.fromisoformat('2020-03-15')

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        article = make_article(new_article_date)

        # Add the article but don't commit it.
        uow.repo.add_article(article)

    # Using a new unit of work, check that the new Article wasn't added to the repository.
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        articles = uow.repo.get_articles_by_date(new_article_date)

        assert len(articles) == 0


def test_uow_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    new_article_date = date.fromisoformat('2020-03-15')

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            article = make_article(new_article_date)
            uow.repo.add_article(article)
            raise MyException()

    # Using a new unit of work, check that the above exception caused the Article not to be added to the repository.
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        articles = uow.repo.get_articles_by_date(new_article_date)

        assert len(articles) == 0





