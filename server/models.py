import re

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

# Words/phrases a post title must contain at least one of (case-sensitive,
# exactly as written in the assignment).
CLICKBAIT_PHRASES = ("Won't Believe", "Secret", "Top", "Guess")

# The only categories a post may have.
VALID_CATEGORIES = ("Fiction", "Non-Fiction")


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('name')
    def validate_name(self, key, value):
        """Name is required and must not already belong to another author."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Author must have a name.')

        # Look for another author with the same name. no_autoflush stops the
        # query from flushing half-built objects. If this author already has
        # an id, exclude it so re-saving the same name is not a "duplicate".
        with db.session.no_autoflush:
            query = Author.query.filter(Author.name == value)
            if self.id is not None:
                query = query.filter(Author.id != self.id)
            if query.first() is not None:
                raise ValueError('Author name must be unique.')

        return value

    @validates('phone_number')
    def validate_phone_number(self, key, value):
        """Phone number (when given) must be exactly ten digits, 0-9 only."""
        if value is None:
            return value
        if not isinstance(value, str) or not re.fullmatch(r'[0-9]{10}', value):
            raise ValueError('Phone number must be exactly ten digits.')
        return value

    def __repr__(self):
        return f'Author(id={self.id}, name={self.name})'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    category = db.Column(db.String)
    summary = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('title')
    def validate_title(self, key, value):
        """Title is required and must contain a clickbait phrase."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Post must have a title.')
        if not any(phrase in value for phrase in CLICKBAIT_PHRASES):
            raise ValueError(
                'Title must contain one of: '
                + ', '.join(f'"{p}"' for p in CLICKBAIT_PHRASES) + '.'
            )
        return value

    @validates('content')
    def validate_content(self, key, value):
        """Content must be at least 250 characters long."""
        if not isinstance(value, str) or len(value) < 250:
            raise ValueError('Content must be at least 250 characters long.')
        return value

    @validates('summary')
    def validate_summary(self, key, value):
        """Summary is optional but may be at most 250 characters."""
        if value is not None and len(value) > 250:
            raise ValueError('Summary must be at most 250 characters long.')
        return value

    @validates('category')
    def validate_category(self, key, value):
        """Category must be exactly 'Fiction' or 'Non-Fiction'."""
        if value not in VALID_CATEGORIES:
            raise ValueError('Category must be "Fiction" or "Non-Fiction".')
        return value

    def __repr__(self):
        return f'Post(id={self.id}, title={self.title} content={self.content}, summary={self.summary})'