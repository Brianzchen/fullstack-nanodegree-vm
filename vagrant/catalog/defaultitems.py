from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///itemlist.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Deletes all the old data from the database
categories = session.query(Category).all()
for c in categories:
    session.delete(c)
    session.commit()

items = session.query(Item).all()
for i in items:
    session.delete(i)
    session.commit()

# Items for Soccer
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

item1 = Item(name="Soccer ball", description="A ball for kicking around",
             category=category1)

session.add(item1)
session.commit()


item1 = Item(name="Soccer cleats",
             description="Gives optimum grip when running around a field",
             category=category1)

session.add(item1)
session.commit()


# Items for Snowboarding
category1 = Category(name="Snowboarding")

session.add(category1)
session.commit()


item1 = Item(name="Snowboard",
             description="The bread and butter of the sport. The board you ride as you go down the mountains",  # noqa
             category=category1)

session.add(item1)
session.commit()

item1 = Item(name="Goggles",
             description="Protects the user from so much in life, the refelction of the sun and the ice and you shred like a madman down the slopes",  # noqa
             category=category1)

session.add(item1)
session.commit()


# Items for Basketball
category1 = Category(name="Basketball")

session.add(category1)
session.commit()


# Items for Baseball
category1 = Category(name="Baseball")

session.add(category1)
session.commit()


# Items for Frisbee
category1 = Category(name="Frisbee")

session.add(category1)
session.commit()


# Items for Rockclimbing
category1 = Category(name="Rockclimbing")

session.add(category1)
session.commit()


# Items for Foosball
category1 = Category(name="Foosball")

session.add(category1)
session.commit()


# Items for Skating
category1 = Category(name="Skating")

session.add(category1)
session.commit()


# Items for Hockey
category1 = Category(name="Hockey")

session.add(category1)
session.commit()

print "added items!"
