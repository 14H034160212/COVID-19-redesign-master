from datetime import date, datetime


class User:
    def __init__(
            self, username: str, password: str
    ):
        self._username = username
        self._password = password
        self._comments = list()

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def comments(self) -> list:
        return self._comments

    def add_comment(self, comment: 'Comment'):
        self._comments.append(comment)

    def __repr__(self):
        return f'<User {self._username} {self._password}>'

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other._username == self._username

    def __hash__(self):
        return hash(self._username)


class Comment:
    def __init__(
            self, user: User, article: 'Article', comment: str, timestamp: datetime
    ):
        self._user = user
        self._article = article
        self._comment = comment
        self._timestamp = timestamp

    @property
    def user(self) -> User:
        return self._user

    @property
    def article(self) -> 'Article':
        return self._article

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    def __eq__(self, other):
        if not isinstance(other, Comment):
            return False
        return other._user == self._user and other._article == self._article and other._comment == self._comment and other._timestamp == self._timestamp

    def __hash__(self):
        return hash(self._username)


class Article:
    def __init__(
            self, date: date, title: str, first_para: str, hyperlink: str, image_hyperlink: str, id:int = None
    ):
        self._id = id
        self._date = date
        self._title = title
        self._first_para = first_para
        self._hyperlink = hyperlink
        self._image_hyperlink = image_hyperlink
        self._comments = list()
        self._tags = list()

    @property
    def id(self):
        return self._id

    @property
    def date(self) -> date:
        return self._date

    @property
    def title(self) -> str:
        return self._title

    @property
    def first_para(self) -> str:
        return self._first_para

    @property
    def hyperlink(self) -> str:
        return self._hyperlink

    @property
    def image_hyperlink(self) -> str:
        return self._image_hyperlink

    @property
    def comments(self) -> list:
        return self._comments

    @property
    def tags(self) -> list:
        return self._tags

    def is_tagged_by(self, tag: 'Tag'):
        return tag in self._tags

    def is_tagged(self) -> bool:
        return len(self._tags) > 0

    def add_comment(self, comment: Comment):
        self._comments.append(comment)

    def add_tag(self, tag: 'Tag'):
        self._tags.append(tag)

    def __repr__(self):
        return f'<Article {self._date.isoformat()} {self._title}>'

    def __eq__(self, other):
        if not isinstance(other, Article):
            return False
        return (
                other._date == self._date and
                other._title == self._title and
                other._first_para == self._first_para and
                other._hyperlink == self._hyperlink and
                other._image_hyperlink == self._image_hyperlink
        )

    def __hash__(self):
        return hash((self._date, self._title, self._first_para, self._hyperlink, self._image_hyperlink))

    def __lt__(self, other):
        return self._date < other._date


class Tag:
    def __init__(
            self, tag_name: str
    ):
        self._tag_name = tag_name
        self._tagged_articles = list()

    @property
    def tag_name(self) -> str:
        return self._tag_name

    @property
    def tagged_articles(self):
        return self._tagged_articles

    def is_applied_to(self, article: Article):
        return article in self._tagged_articles

    def add_article(self, article: Article):
        self._tagged_articles.append(article)

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return False
        return other._tag_name == self._tag_name

    def __hash__(self):
        return hash(self._tag_name)


def make_comment(comment_text: str, user: User, article: Article, timestamp: datetime = datetime.today()):
    comment = Comment(user, article, comment_text, timestamp)
    user.add_comment(comment)
    article.add_comment(comment)

    return comment


def make_tag_association(article: Article, tag: Tag):
    article.add_tag(tag)
    tag.add_article(article)


def contains(list, item):
    # Note: the 'in' operator when applied to a list performs a value equality
    # check rather than an identity check. This functions tests for membership
    # of item within a list by identity.
    index = 0
    found = False
    while index < len(list) and not found:
        if list[index] is item:
            found = True
        else:
            index = index + 1
    return found
