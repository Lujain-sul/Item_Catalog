#!/usr/bin/env python3
# Development guide from udacity classroom:
# https://github.com/udacity/ud330/tree/master/Lesson4/step2

# Import nedded modules
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


Base = declarative_base()


# Create User table
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


# Create Category table
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
            }


# Create Item table
class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    addition_dt = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('category.id'))
    # include bakref parameter to get all items in a category, guide from:
    # https://stackoverflow.com/questions/50011349/return-joined-tables-in-json-format-with-sqlalchemy-and-flask-jsonify
    category = relationship(Category,
                            backref=backref('items', cascade='all,delete'))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category_id': self.category_id
            }


engine = create_engine('sqlite:///catalog.db')
# Create database named catalog.db
Base.metadata.create_all(engine)
