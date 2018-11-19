#!/usr/bin/env python3
# Development guide from udacity classroom:
# https://github.com/udacity/ud330/tree/master/Lesson4/step2

# Import nedded modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import datetime

# Connect to catalog database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Create session object
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Add data to database

User1 = User(name="Lujain Sul", email="lujain.sul@gmail.com")
session.add(User1)
session.commit()

User2 = User(name="Lujain Ghul", email="lujain.ghul@gmail.com")
session.add(User2)
session.commit()

# Category for Soccer
category1 = Category(name="Soccer")
session.add(category1)
session.commit()

category1_item1 = Item(title="Soccer Cleats", description="The shoes",
                       addition_dt=datetime.datetime(2018, 11, 1, 1, 0),
                       user=User1,
                       category=category1)
session.add(category1_item1)
session.commit()

category1_item2 = Item(title="Jersey", description="The shirt",
                       addition_dt=datetime.datetime(2018, 11, 2, 10, 0),
                       user=User1,
                       category=category1)
session.add(category1_item2)
session.commit()


# Category for Basketball
category2 = Category(name="Basketball")
session.add(category2)
session.commit()


# Category for Baseball
category3 = Category(name="Baseball")
session.add(category3)
session.commit()

category3_item1 = Item(title="Bat", description="The bat",
                       addition_dt=datetime.datetime(2018, 11, 2, 3, 0),
                       user=User2,
                       category=category3)
session.add(category3_item1)
session.commit()


# Category for Frisbee
category4 = Category(name="Frisbee")
session.add(category4)
session.commit()


# Category for Snowboarding
category5 = Category(name="Snowboarding")
session.add(category5)
session.commit()

category5_item1 = Item(title="Snowboard",
                       description="TBest for any terrain and conditions.",
                       addition_dt=datetime.datetime(2018, 11, 5, 1, 0),
                       user=User2,
                       category=category5)
session.add(category5_item1)
session.commit()


# Category for Rock Climbing
category6 = Category(name="Rock Climbing")
session.add(category6)
session.commit()


# Category for Foosball
category7 = Category(name="Foosball")
session.add(category7)
session.commit()


# Category for Skating
category8 = Category(name="Skating")
session.add(category8)
session.commit()


# Category for Hockey
category9 = Category(name="Hockey")
session.add(category9)
session.commit()


print("catalog items added!")
