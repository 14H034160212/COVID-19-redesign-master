from datetime import date, datetime

import pytest

from covid.adapters.database_repository import SqlAlchemyRepository
from covid.domain.model import User, Article, Tag, Comment, make_comment
from covid.adapters.repository import RepositoryException


def test_repository_can_add_a_user(session):
    repo = SqlAlchemyRepository(session)

    user = User('Dave', '123456789')
    repo.add_user(user)
    session.commit()

    assert repo.get_user('Dave') is user


def test_repository_can_retrieve_a_user(session):
    repo = SqlAlchemyRepository(session)

    user = repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(session):
    repo = SqlAlchemyRepository(session)

    user = repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_article_count(session):
    repo = SqlAlchemyRepository(session)

    number_of_articles = repo.get_number_of_articles()

    # Check that the query returned 6 Articles.
    assert number_of_articles == 6


def test_repository_can_add_article(session):
    repo = SqlAlchemyRepository(session)

    article = Article(
        date.fromisoformat('2020-03-09'),
        'Second US coronavirus cruise tests negative amid delays and cancellations',
        'It was revealed ...',
        'https://www.nzherald.co.nz/travel/news/article.cfm?c_id=7&objectid=12315024',
        'https://www.nzherald.co.nz/resizer/ix7hy3lzkMWUkD8hE6kdZ-8oaOM=/620x349/smart/filters:quality(70)/arc-anglerfish-syd-prod-nzme.s3.amazonaws.com/public/7VFOBLCBCNDHLICBY3CTPFR2L4.jpg',
        7
    )
    repo.add_article(article)
    session.commit()

    assert repo.get_article(7) is article


def test_repository_can_retrieve_article(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_article(1)

    # Check that the Article has the expected title.
    assert article.title == 'Coronavirus: First case of virus in New Zealand'

    # Check that the Article is commented as expected.
    comment_one = [comment for comment in article.comments if comment.comment == 'Oh no, COVID-19 has hit New Zealand'][
        0]
    comment_two = [comment for comment in article.comments if comment.comment == 'Yeah Freddie, bad news'][0]

    assert comment_one.user.username == 'fmercury'
    assert comment_two.user.username == "thorke"

    # Check that the Article is tagged as expected.
    assert article.is_tagged_by(Tag('Health'))
    assert article.is_tagged_by(Tag('New Zealand'))


def test_repository_does_not_retrieve_a_non_existent_article(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_article(101)
    assert article is None


def test_repository_can_retrieve_articles_by_date(session):
    repo = SqlAlchemyRepository(session)

    articles = repo.get_articles_by_date(date(2020, 3, 1))

    # Check that the query returned 3 Articles.
    assert len(articles) == 3


def test_repository_does_not_retrieve_an_article_when_there_are_no_articles_for_a_given_date(session):
    repo = SqlAlchemyRepository(session)

    articles = repo.get_articles_by_date(date(2020, 3, 8))
    assert len(articles) == 0


def test_repository_can_retrieve_tags(session):
    repo = SqlAlchemyRepository(session)

    tags = repo.get_tags()

    assert len(tags) == 4

    tag_one = [tag for tag in tags if tag.tag_name == 'New Zealand'][0]
    tag_two = [tag for tag in tags if tag.tag_name == 'Health'][0]
    tag_three = [tag for tag in tags if tag.tag_name == 'World'][0]
    tag_four = [tag for tag in tags if tag.tag_name == 'Politics'][0]

    assert len(tag_one.tagged_articles) == 3
    assert len(tag_two.tagged_articles) == 2
    assert len(tag_three.tagged_articles) == 3
    assert len(tag_four.tagged_articles) == 1


def test_repository_can_get_first_article(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_first_article()
    assert article.title == 'Coronavirus: First case of virus in New Zealand'


def test_repository_can_get_last_article(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_last_article()
    assert article.title == 'Coronavirus: Death confirmed as six more test positive in NSW'


def test_repository_can_get_articles_by_ids(session):
    repo = SqlAlchemyRepository(session)

    articles = repo.get_articles_by_id([2, 5, 6])

    assert len(articles) == 3
    assert articles[
               0].title == 'Covid 19 coronavirus: US deaths double in two days, Trump says quarantine not necessary'
    assert articles[1].title == "Australia's first coronavirus fatality as man dies in Perth"
    assert articles[2].title == 'Coronavirus: Death confirmed as six more test positive in NSW'


def test_repository_does_not_retrieve_article_for_non_existent_id(session):
    repo = SqlAlchemyRepository(session)

    articles = repo.get_articles_by_id([2, 9])

    assert len(articles) == 1
    assert articles[
               0].title == 'Covid 19 coronavirus: US deaths double in two days, Trump says quarantine not necessary'


def test_repository_returns_an_empty_list_for_non_existent_ids(session):
    repo = SqlAlchemyRepository(session)

    articles = repo.get_articles_by_id([0, 9])

    assert len(articles) == 0


def test_repository_returns_article_ids_for_existing_tag(session):
    repo = SqlAlchemyRepository(session)

    article_ids = repo.get_article_ids_for_tag('New Zealand')

    assert article_ids == [1, 3, 4]


def test_repository_returns_an_empty_list_for_non_existent_tag(session):
    repo = SqlAlchemyRepository(session)

    article_ids = repo.get_article_ids_for_tag('United States')

    assert len(article_ids) == 0


def test_repository_returns_date_of_previous_article(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_article(6)
    previous_date = repo.get_date_of_previous_article(article)

    assert previous_date.isoformat() == '2020-03-01'


def test_repository_returns_none_when_there_are_no_previous_articles(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_article(1)
    previous_date = repo.get_date_of_previous_article(article)

    assert previous_date is None


def test_repository_returns_date_of_next_article(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_article(3)
    next_date = repo.get_date_of_next_article(article)

    assert next_date.isoformat() == '2020-03-05'


def test_repository_returns_none_when_there_are_no_subsequent_articles(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_article(6)
    next_date = repo.get_date_of_next_article(article)

    assert next_date is None


def test_repository_can_add_a_tag(session):
    repo = SqlAlchemyRepository(session)

    tag = Tag('Motoring')
    repo.add_tag(tag)
    session.commit()

    assert tag in repo.get_tags()


def test_repository_can_add_a_comment(session):
    repo = SqlAlchemyRepository(session)

    user = repo.get_user('thorke')
    article = repo.get_article(2)
    comment = make_comment("Trump's onto it!", user, article)

    repo.add_comment(comment)
    session.commit()

    assert comment in repo.get_comments()


def test_repository_does_not_add_a_comment_without_a_user(session):
    repo = SqlAlchemyRepository(session)

    article = repo.get_article(2)
    comment = Comment(None, article, "Trump's onto it!", datetime.today())

    with pytest.raises(RepositoryException):
        repo.add_comment(comment)


def test_repository_can_retrieve_comments(session):
    repo = SqlAlchemyRepository(session)

    assert len(repo.get_comments()) == 2



