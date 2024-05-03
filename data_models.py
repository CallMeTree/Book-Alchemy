from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, WriteOnlyMapped


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Author(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    birth_date: Mapped[str] = mapped_column(String(10), index=True)
    date_of_death: Mapped[str] = mapped_column(String(10), index=True)
    books: WriteOnlyMapped["Book"] = relationship(back_populates="author")

    def __repr__(self):
        return '<Author {}>'.format(self.name)


class Book(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(17), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    publication_year: Mapped[str] = mapped_column(String(10), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey(Author.id), index=True)
    author: Mapped["Author"] = relationship(back_populates="books")

    def __repr__(self):
        return '<Book {}>'.format(self.title)
