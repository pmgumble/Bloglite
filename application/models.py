from .database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context


#--------------------  DB Model Classes  --------------------


# Followers association table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)


# Users Database table
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    favorite_color = db.Column(db.String(150))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String())
    password_hash = db.Column(db.String(128),nullable=True)
    # User can have many Posts
    posts = db.relationship('Posts', backref='poster')
    likes = db.relationship('Like', backref='user', passive_deletes=True)

    #Many-to-many followers relationship
    followed = db.relationship(
        'Users', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')


    def follow(self, users):
        if not self.is_following(users):
            self.followed.append(users)

    def unfollow(self, users):
        if self.is_following(users):
            self.followed.remove(users)

    def is_following(self, users):
        return self.followed.filter(
            followers.c.followed_id == users.id).count() > 0

    # Followed posts query
    def followed_posts(self):
        followed = Posts.query.join(
            followers, (followers.c.followed_id == Posts.id)).filter(
                followers.c.follower_id == self.id)
        own = Posts.query.filter_by(id=self.id)
        return followed.union(own).order_by(Posts.date_posted.desc())

    @property
    def password(self):
        raise AttributeError('Password is not a redable Attribute! ')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)


    # create a string 
    def __repr__(self):
        return '<Name %r>' %self.name

    

# Create Blog Post Model

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(225))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #Foregin key to link Users (refer to the primary key of user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    likes = db.relationship('Like', backref='post', passive_deletes=True)
    pic = db.Column(db.String())

# Create Like Post Model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer,db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)



