from typing import List

from covid.adapters import unit_of_work
from covid.domain.model import make_comment, Article, Comment, Tag


class NonExistentArticleException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_comment(article_id: int, comment_text: str, username: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        # Check that the article exists.
        article = uow.repo.get_article(article_id)
        if article is None:
            raise NonExistentArticleException

        user = uow.repo.get_user(username)
        if user is None:
            raise UnknownUserException

        # Create comment.
        comment = make_comment(comment_text, user, article)

        # Update the repository.
        uow.repo.add_comment(comment)
        uow.commit()


def get_article(article_id: int, uow: unit_of_work.AbstractUnitOfWork):
    article = None
    with uow:
        article = uow.repo.get_article(article_id)

        if article is None:
            raise NonExistentArticleException

    return article_to_dict(article)


def get_first_article(uow: unit_of_work.AbstractUnitOfWork):
    article = None
    with uow:
        article = uow.repo.get_first_article()

    return article_to_dict(article)


def get_last_article(uow: unit_of_work.AbstractUnitOfWork):
    article = None
    with uow:
        article = uow.repo.get_last_article()
    return article_to_dict(article)


def get_articles_by_date(date, uow: unit_of_work.AbstractUnitOfWork):
    # Returns articles for the target date (empty if no matches), the date of the previous article (might be null), the date of the next article (might be null)
    with uow:
        articles = uow.repo.get_articles_by_date(target_date=date)

        articles_dto = list()
        prev_date = next_date = None

        if len(articles) > 0:
            prev_date = uow.repo.get_date_of_previous_article(articles[0])
            next_date = uow.repo.get_date_of_next_article(articles[0])

            # Convert Articles to dictionary form.
            articles_dto = articles_to_dict(articles)

        return articles_dto, prev_date, next_date


def get_article_ids_for_tag(tag_name, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        article_ids = uow.repo.get_article_ids_for_tag(tag_name)

        return article_ids


def get_articles_by_id(id_list, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        articles = uow.repo.get_articles_by_id(id_list)

        # Convert Articles to dictionary form.
        articles_as_dict = articles_to_dict(articles)

        return articles_as_dict


def get_comments_for_article(article_id, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        article = uow.repo.get_article(article_id)

        if article is None:
            raise NonExistentArticleException

        return comments_to_dict(article.comments)


# ============================================
# Functions to convert model entities to dicts
# ============================================

def article_to_dict(article: Article):
    article_dict = {
        'id': article.id,
        'date': article.date,
        'title': article.title,
        'first_para': article.first_para,
        'hyperlink': article.hyperlink,
        'image_hyperlink': article.image_hyperlink,
        'comments': comments_to_dict(article.comments),
        'tags': tags_to_dict(article.tags)
    }
    return article_dict


def articles_to_dict(articles: List[Article]):
    return [article_to_dict(article) for article in articles]


def comment_to_dict(comment: Comment):
    comment_dict = {
        'username': comment.user.username,
        'article_id': comment.article.id,
        'comment_text': comment.comment,
        'timestamp': comment.timestamp
    }
    return comment_dict


def comments_to_dict(comments: List[Comment]):
    return [comment_to_dict(comment) for comment in comments]


def tag_to_dict(tag: Tag):
    tag_dict = {
        'name': tag.tag_name,
        'tagged_articles': [article.id for article in tag.tagged_articles]
    }
    return tag_dict


def tags_to_dict(tags: List[Tag]):
    return [tag_to_dict(tag) for tag in tags]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_article(dict):
    article = Article(dict.id, dict.date, dict.title, dict.first_para, dict.hyperlink)
    # Note there's no comments or tags.
    return article
