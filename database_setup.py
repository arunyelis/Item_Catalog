from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id_ = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    email = Column(String(50), nullable=False)
    picture = Column(String(200), nullable=False)


class Category(Base):
    __tablename__ = "category"

    id_ = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id_'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            "id": self.id_,
            "name": self.name
        }


class Item(Base):
    __tablename__ = "item"

    name = Column(String(30), nullable=False)
    id_ = Column(Integer, primary_key=True)
    description = Column(String(5000), nullable=False)
    price = Column(String(8), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id_'))
    category = relationship(Category)

    @property
    def serialize(self):
        return {
            "id": self.id_,
            "cat_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "price": self.price
        }


class Offer(Base):
    __tablename__ = "offer"

    id_ = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    description = Column(String(5000), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id_'))
    validity = Column(String(4), nullable=False)
    item = relationship(Item)


@property
def serialize(self):
    return {
        "id": self.id_,
        "name": self.name,
        "description": self.description,
        "validity": self.validity,
        "item_id": self.item_id
    }

engine = create_engine("sqlite:///itemCatalog.db")
Base.metadata.create_all(engine)
