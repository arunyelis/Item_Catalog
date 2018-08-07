# **Item Catalog Application**

Item Catalog application  provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

# **Prerequisites**

1. python 3.x  downloaded and installed 
2. Flask  installed (pip install flask)
3. request module installed (pip install request)

# **Getting Started **

1. Open CMD/Terminal
2. Navigate to Item-catalog folder
3. type ` python database_setup.py ` (This will setup database)
4. type `python load_sample_data.py ` (This will load sample data in our database)
5. Now type `python application.py ` (This will run our application)
6. After doing previous step our server will start on port 8080
7. Now Open your browser and type `http://localhost:8080`
8. Make sure "client_secrets.json" file is inside item_catalog folder
9. Don't Delete or modify "cilent_secret.json" file
10. Login with google plus
11. Now create, update, delete own categories, items and offers.

**Note:** For more information about running python in terminal/cmd  [Click Here](https://en.wikibooks.org/wiki/Python_Programming/Creating_Python_Programs "How to run application using cmd/terminal").

# **Built With**

1. Language/Framework/tool used
   - Python3
   - Flask
   - sublime


## **JSON Endpoints**

**JSON **: `/catalog/json`

(This endpoint will give complete json data of categories, items, offers)

