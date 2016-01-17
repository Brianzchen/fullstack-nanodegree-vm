from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Catagory, Item

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
catagories = session.query(Catagory).all()
for c in catagories:
    session.delete(c)
    session.commit()

items = session.query(Item).all()
for i in items:
    session.delete(i)
    session.commit()

# Items for Soccer
catagory1 = Catagory(name="Soccer")

session.add(catagory1)
session.commit()

item1 = Item(name="Soccer ball", description="A ball for kicking around",
             catagory=catagory1)

session.add(item1)
session.commit()


item1 = Item(name="Soccer cleats",
             description="Gives optimum grip when running around a field",
             catagory=catagory1)

session.add(item1)
session.commit()


# Items for Snowboarding
catagory1 = Catagory(name="Snowboarding")

session.add(catagory1)
session.commit()


item1 = Item(name="Snowboard",
             description="The bread and butter of the sport. The board you ride as you go down the mountains",  # noqa
             catagory=catagory1)

session.add(item1)
session.commit()

item1 = Item(name="Goggles",
             description="Protects the user from so much in life, the refelction of the sun and the ice and you shred like a madman down the slopes",  # noqa
             catagory=catagory1)

session.add(item1)
session.commit()


# Items for Basketball
catagory1 = Catagory(name="Basketball")

session.add(catagory1)
session.commit()


# Items for Baseball
catagory1 = Catagory(name="Baseball")

session.add(catagory1)
session.commit()


# Items for Frisbee
catagory1 = Catagory(name="Frisbee")

session.add(catagory1)
session.commit()


# Items for Rockclimbing
catagory1 = Catagory(name="Rockclimbing")

session.add(catagory1)
session.commit()


# Items for Foosball
catagory1 = Catagory(name="Foosball")

session.add(catagory1)
session.commit()


# Items for Skating
catagory1 = Catagory(name="Skating")

session.add(catagory1)
session.commit()


# Items for Hockey
catagory1 = Catagory(name="Hockey")

session.add(catagory1)
session.commit()

print "added items!"
