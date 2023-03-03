Author:
**Pratik M Gumble**

I am Data science enthusiast, working for educational institute as a teaching professional. Currently 
learning data science and full stack development. 
**Description:**
Design a blog application where users can register and login. Users can able to post and do post 
management for user feed. User can see other authors, follow unfollow and like their post. 
Authentication & Authorization functionalities are integral part of blog management project.
Technologies used:
 Flask 2.2.2
 Flask-CKEditor 0.4.6 for editing text
 Flask-HTTPAuth 4.7.0 for API authentication
 Flask-Login 0.6.2 for login management
 Flask-Migrate 4.0.0 for database migration
 Flask-RESTful 0.3.9 for REST API
 Flask-SQLAlchemy 3.0.2 for ORM
 Jinja2 3.1.2 Dynamic templates
 MarkupSafe 2.1.1
 Werkzeug 2.2.2
 WTForms 3.0.1 for forms
 HTML, CSS, Bootstrap, Sqlite3
DB Schema Design:
Tables 
1. Users
 Id – Unique ID for user identification - Integer, PK, Unique
 Username – Username for User - string, Unique, Not Null
 Name – Name of Author – string, Not Null
 Email – email id of author – string, Not Null
 favorite_color – Fav color of author – string
 about_author – Author personal info – string
 date_added – user registration date – String, (default datetime now)
 profile_pic – user profile pic – string (profile pic file path string stored in folder)
 password_hash- Hashed password – string 
2. Posts
 Id - Unique ID for post identification - Integer, PK, Unique
 Title – Title of post – String
 Content – Content for the post – String 
 date_posted – Postdate – string (default datetime now)
 slug – Hashtag for the post – String
 poster_id – FK users.id – to identify user for the post 
 pic – post pic - string (post pic file path string stored in folder)
3. Like
 Id - Unique ID for post like identification - Integer, PK, Unique
 Author – FK users.id – to identify like by author
 post_id – FK posts.id – to identify post on which like is applied
 date_added - String, (default datetime now)
Association Table:
4. followers
 follower_id: FK users.id – to identify follower (to whom follows)
 followed_id: FK users.id - to identify followed user (to whom followed)
API Design
In API part HTTP Basic authorization is used to authorize and authenticate the user. API are 
implemented in two parts USER API and POST API. CRUD functionality designed for both parts.
User can be viewed, updated, deleted and New User is created with valid responses. Posts can be 
viewed, updated and deleted by respective authorize user, new post can be created by logged in 
user. Errors class and valid responses are created in API part.
Architecture and Features
Project folder consist of Bloglite consist all the required files. Inside the Bloglite folder 
consist of main.py file. One level up folder named application consists of files as api.py, config.py, 
controllers.py, database.py, models.py, and validation.py. db_directory folders consist of sqlite3
database for the project. Static folders has sub folders css, images, js consist of static files. Templates 
folder consist of all the required html files.
Index page shows the post by all the users who posted on bloglite application. One can 
register to post and post feed management on bloglite application with unique email id. User can 
view, update, delete, his personal information through the dashboard. Logged in user can then post 
the posts on bloglite application. Logged in user can view all the posts by other users, can update 
and delete its own post, not authorize to update and delete posts of other users. Logged in user can 
like or dislike posts of other users who posted post on bloglite. Logged in user can follow and 
unfollow other users on bloglite. 
Two search features are implemented in this project; one title search bar feature is 
implemented for search contents in posts. Second search feature is implemented to search users 
registered on bloglite.
CRUD API for User and Post management are implemented with basic HTTP authorization
