from sqlalchemy import create_engine
from database_setup import Base, User, Category, Item, Offer
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///itemCatalog.db")

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# FIRST USER
user1 = User(name="shivam sharma",
             email="talk2shivamsharma19597@gmail.com",
             picture="link1")
session.add(user1)
session.commit()

# First User Category 1
category1 = Category(name="Mobile", user=user1)

session.add(category1)
session.commit()

# item of category 1

item1 = Item(name="Redmi Note 5",
             description='''
                         How does a day with the Redmi Note 5 phone look like?
                         You will probably wake up admiring the beautiful 15.2
                         cm 18:9 full-screen display with rounded corners. You
                         can download various apps and store media files
                         without a worry owing to the 64 GB memory along with a
                         RAM of 4 GB. You keep yourself occupied en-route by
                         playing your favorite games with absolutely no lags.
                         You then capture your favorite moments of the day with
                         the 12 MP camera with a 12-micrometer large pixel-size
                         that lets you take stunning images even in
                         low-lighting conditions. Not to forget about the
                         must-take selfies with your loved ones, which too, can
                         be captured in low-light using the LED selfie-light
                         feature. And as you come to the end of the day after
                         working, surfing,gaming and chatting, you would be
                         pleased to see the 4000 mAh battery still strong in
                         charge.
            ''',
             price="₹11,999",
             category=category1)
session.add(item1)
session.commit()

item2 = Item(name="Samsung Galaxy J2 ",
             description='''
                        Samsung brings to you the J2 2018 which comes with an
                        array of features that are meant to provide you with
                        the complete smartphone experience. Powered by a 1.4
                        GHz Quad-core Processor, this smartphone lets you play
                        games, watch videos, and connect with your friends
                        effortlessly on a 12.64-cm (5.0) Super AMOLED Display.
                        ''',
             price="₹15,990",
             category=category1)
session.add(item2)
session.commit()

item3 = Item(name="Samsung Galaxy J7 Duo",
             description='''
                         Say hello to the Samsung J7 Duo who’s delightful Dual
                         Camera with Live Focus will make every picture of
                         yours, a memorable one. Performance too is this
                         phone’s forte as it runs on the Android Oreo Operating
                         System powered by the Exynos 7 Series Octa Core
                         Processor.
                         ''',
             price="₹8,190",
             category=category1)
session.add(item3)
session.commit()

item4 = Item(name="Samsung Galaxy S9 Plus",
             description='''
                         Galaxy S9+ Sleek and stunning the latest flagship from
                         Samsung comes with a revolutionary camera that adapts
                         like the human eye. It allows one to take photos
                         without thinking twice no matter the time of day. With
                         two f-stop modes, the category-defining Dual Aperture
                         adapts to bright light and super low light
                         automatically with ease making your photos look great
                         whether it's bright or dark, day or night.
                         ''',
             price="₹60,190",
             category=category1)
session.add(item4)
session.commit()

item5 = Item(name="Mi Mix 2 (Black, 128 GB)",
             description='''
                         The Mi MIX 2, with its Snapdragon 835 processor and 6
                         GB of RAM, packs quite a punch while its immersive
                         full display design, that has an 18:9 aspect ratio,
                         makes entertainment more lifelike.
                         ''',
             price="₹29,999",
             category=category1)
session.add(item5)
session.commit()

category2 = Category(name="Tv & Appliances", user=user1)

session.add(category2)
session.commit()

item6 = Item(name="Samsung HD Ready LED TV",
             description='''
                         Offering clear HD picture quality, and equipped with
                         two 10W speakers, this 32-inch Samsung Series 4 TV set
                         is designed to enhance your TV-viewing experience. Its
                         triple protect (anti-lightning, anti-surge, and
                         anti-humidity) features have been added to ensure its
                         complete safety.
                        ''',
             price="₹17,499",
             category=category2)
session.add(item6)
session.commit()

item7 = Item(name="Sony Bravia 101.6cm",
             description='''
                         Featuring a large Full HD screen, this Sony Bravia
                         smart LED TV makes all the visuals come to life.
                         Whether you’re watching a Blu-ray movie or a football
                         match on the sports channel, the X-Reality PRO picture
                         processing engine renders every image in lifelike
                         quality, and that too with reduced picture noise, for
                         an immersive viewing experience. The superior picture
                         quality is complemented by rich and deep bass, all
                         thanks to the powerful inbuilt subwoofer of this TV.
                        ''',
             price="₹41,999",
             category=category2)
session.add(item7)
session.commit()

item8 = Item(name="Samsung HD Ready LED TV",
             description='''
                         Offering clear HD picture quality, and equipped with
                         two 10W speakers, this 32-inch Samsung Series 4 TV set
                         is designed to enhance your TV-viewing experience. Its
                         triple protect (anti-lightning, anti-surge, and anti-
                         humidity) features have been added to ensure its
                         complete safety.
                        ''',
             price="₹17,499",
             category=category2)
session.add(item7)
session.commit()

item9 = Item(name="LG 80cm HD Ready LED TV ",
             description='''
                         This TV comes with an IPS panel that offers wide
                         viewing angles. It allows multiple people to watch
                         content with no loss in image quality from almost any
                         corner of the living room. The panel also offers
                         better colours and clarity.
                        ''',
             price="₹18,799",
             category=category2)
session.add(item9)
session.commit()

item10 = Item(name="LG Full HD LED Smart TV (49LJ617T)",
              description='''
                          Experience non-stop entertainment with this LG Smar
                          TV. Whether you just want to watch news or explore
                          premium content from the Internet, with this TV, you
                          can do both. That’s not all, it comes with an IPS
                          panel and a Color Master Engine which offer picture-
                          perfect clarity.
                        ''',
              price="₹54,999",
              category=category2)
session.add(item10)
session.commit()

category3 = Category(name="Watches", user=user1)

session.add(category3)
session.commit()

item11 = Item(name="Fossil Blue3813",
              description='''
                          Fossil Fsw7006 Swiss Fs-5 Series Gmt Three-Hand
                          Date Watch Brown.
                            ''',
              price="₹63,406",
              category=category3)
session.add(item11)
session.commit()

item12 = Item(name="Fossil Blue3804",
              description='''
                          Fossil Fsw1003 Swiss Made Automatic Leather Watch
                          Brown.
                          ''',
              price="₹51,625",
              category=category3)
session.add(item12)
session.commit()

item13 = Item(name="Titan Silver 15117 ",
              description='''
                          The thinnest watch in the universe | Contemporary
                          skeletal edge case design | Quartz movement | Case
                          diameter: 31mm | Water resistant to 99  feet.
                          ''',
              price="₹43,696",
              category=category3)
session.add(item13)
session.commit()

item14 = Item(name="Titan 1653NP03 Edge Watch ",
              description='''
                          Style Code: 1653NP03
                          Series: Edge
                          Occasion: Casual
                          Watch Type: Wrist Watch
                          Pack of: 1
                          Mechanism: Quartz
                          ''',
              price="₹19,970",
              category=category3)
session.add(item14)
session.commit()

category4 = Category(name="Small Home Appliances", user=user1)

session.add(category4)
session.commit()

item15 = Item(name="Livpure LIV-PEP-PRO-PLUS ",
              description='''Access to clean drinking water is a basic need,
              and you can enjoy the same with this Livpure water purifier. It
              puts water under a six-stage purification process – the first
              filter removes fine and coarse particulate matter from water, the
              second filter absorbs harmful pesticides and odor-causing organic
              compounds from water, the third filter prevents salts from
              scaling on membrane layers hich improves the membrane's
              purification capacity and increases its longevity, the fourth
              stage is where hazardous chemicals and tiny microbes are removed,
              the fifth filter disinfects water with UV radiation, and the
              sixth filter improves the clarity of water by removing fine
              suspended impurities from it. Additionally, this water purifier
              also enhances the taste of water by removing volatile organic
              impurities from it. What you get in the end is clean, odorless,
              and better-quality drinking water
              ''',
              price="₹10,499",
              category=category4)
session.add(item15)
session.commit()

category5 = Category(name="Health and Nutrition CLP", user=user1)

session.add(category5)
session.commit()

item16 = Item(name="JYM Pro Supplement Science Protein Blends ",
              description='''
                          Brand: JYM
                          Model Number: 817047020331
                          Quantity: 1814 g
                          Flavor: Banana Cream Pie
                          Protein Type: Protein Blends
                          Usage Timings: Pre-workout
                          Form: Powder
                          Dietary Preference: NA
                          Composition: Calories - 140, Total Fat - 3 g, Total
                                       Carbohydrate - 3 g,
                          Sugars - 1 g, Calcium - 324 mg, Potassium - 100 mg
                          Number of Scoops per Container: 52
                          Ayurvedic: No
                          Container Type: Bottle
                          Food Preference: Non-vegetarian
                          Serving Size: 35 g
                          Model Name: Pro Supplement Science
                          ''',
              price="₹5,270",
              category=category5)
session.add(item16)
session.commit()
