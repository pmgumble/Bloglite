from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse, request
from application.models import Users, Posts
from application.database import db
from flask import current_app as app, jsonify, g, url_for
import werkzeug
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash
from application.validation import NotFoundError, BusinessValidationError


#--------------------  HHTP Basic Auth   --------------------
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


# -------------------  Username output fields  ---------------------
user__op = {
  "id": fields.Integer,
  "name": fields.String,
  "username": fields.String,
  "email": fields.String,
  "about_author": fields.String,
  "date_added": fields.String
}

# -------------------  Posts output fields  ---------------------

post__op = {
  "id": fields.Integer,
  "title": fields.String,
  "content": fields.String,
  "date_posted": fields.String,
  "slug": fields.String,
  "poster_id": fields.String,
  "likes": fields.Integer

}

# --------------------- Parser  -----------------------------

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument("username")
create_user_parser.add_argument("name")
create_user_parser.add_argument("email")
create_user_parser.add_argument("password")



update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument("name")
update_user_parser.add_argument("email")
update_user_parser.add_argument("password")



create_post_parser = reqparse.RequestParser()
create_post_parser.add_argument("title")
create_post_parser.add_argument("content")
create_post_parser.add_argument("slug")


update_post_parser = reqparse.RequestParser()
update_post_parser.add_argument("title")
update_post_parser.add_argument("content")
update_post_parser.add_argument("slug")


#--------------------  USer API  --------------------

class UserAPI(Resource):
    @marshal_with(user__op)
    def get(self, username):
        # Get the username 
        print(" In user API GET METHOD", username)

        # Get the username from database based on username 
        user = db.session.query(Users).filter(Users.username== username).first()

        if user:
            # reurn a valid user jason
            return user
        else:
            # return 404 error 
            raise NotFoundError(status_code=404)

        #Format the the return jason 

        # Return 
      

    @auth.login_required
    def delete(self, username):
        # Check user exist first
        if username == g.current_user.username:
            user = db.session.query(Users).filter(Users.username== username).first()
            if user is None:
                # return 404 error 
                raise NotFoundError(status_code=404)

            posts = Posts.query.filter(Posts.poster.has(username=username)).first()
            if posts:
                raise BusinessValidationError(status_code=400, error_code="BE1007", error_message="cant delete users as there are posts assosiated with the user")
            db.session.delete(user)
            db.session.commit()
            # Check if the current user in loged in , has permission to delete itself 

            # Check if there are post assosiate for this user, if yes
            # throw error 

            # if no depedency then delete

            return "", 200
        else:
            return "unauthorize"


    @marshal_with(user__op)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        name = args.get("name", None)
        email = args.get("email", None)
        password = args.get("password", None)

        if username is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")
        
        if name is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="name is required")
        
        if email is None:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="email is required")
        
        if password is None:
            raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="password is required")

        if "@" and "." in email:
            pass
        else:
            raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="invalid email")

        user = db.session.query(Users).filter((Users.username == username) | (Users.email == email)).first()

        if user:
            raise BusinessValidationError(status_code=400, error_code="BE1006", error_message="Duplicate user")
        
        new_user = Users(username=username, email=email, name=name)
        new_user.hash_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user, 201


    @auth.login_required
    @marshal_with(user__op)
    def put(self, username):
        if username == g.current_user.username:
            args = update_user_parser.parse_args()
            name = args.get("name", None)
            email = args.get("email", None)
            password = args.get("password", None)

            if username is None:
                raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")
            
            if name is None:
                raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="name is required")
            
            if email is None:
                raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="email is required")
            
            if password is None:
                raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="password is required")

            if "@" and "." in email:
                pass
            else:
                raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="invalid email")
            


            user = db.session.query(Users).filter(Users.email== email).first()
            if user:
                raise BusinessValidationError(status_code=400, error_code="BE1007", error_message="Duplicate email")

            # Check if user exists
            user = db.session.query(Users).filter(Users.username== username).first()
            if user is None:
                # return 404 error 
                raise NotFoundError(status_code=404)
            
            user.email = email
            user.name = name
            user.hash_password(password)

            db.session.add(user)
            db.session.commit()

            return user
        else:
            return "unauthorize"

#--------------------  Post API  --------------------

class PostAPI(Resource):
    @auth.login_required
    def get(self, user_id):
        posts = Posts.query.filter_by(poster_id=user_id).all()
        print(posts)
        if len(posts)>0:
            data = []
            for post in posts   :
                d = {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "slug": post.slug,
                    "poster_id": post.poster_id,
                }
                data.append(d)
            return data, 200
        else:
            # return 404 error 
            raise NotFoundError(status_code=404)

    @auth.login_required
    def post(self, user_id):
        args = create_post_parser.parse_args()
        title = args.get("title", None)
        content = args.get("content", None)
        slug = args.get("slug", None)
        if user_id == g.current_user.id:
            ID = user_id
            user = Users.query.filter_by(id=ID).first()
            if user:
                if title is None:
                    raise BusinessValidationError(status_code=400, error_code="BE1008", error_message="Title is required")
                
                if content is None:
                    raise BusinessValidationError(status_code=400, error_code="BE1009", error_message="Content is required")

                if slug is None:
                    raise BusinessValidationError(status_code=400, error_code="BE1010", error_message="Slug is required")
                
                new_post = Posts(title=title, content=content,slug=slug, poster_id=user_id )
                db.session.add(new_post)
                db.session.commit()

                posts = Posts.query.filter_by(poster_id=user_id).all()
                if len(posts)>0:
                    data = []
                    for post in posts   :
                        d = {
                            "id": post.id,
                            "title": post.title,
                            "content": post.content,
                            "slug": post.slug,
                            "poster_id": post.poster_id,
                        }
                        data.append(d)
                    return data, 200
                else:
                    # return 404 error 
                    raise NotFoundError(status_code=404)

            else:
                # Invalid student id
                raise BusinessValidationError(status_code=400, error_code="BE1011", error_message="User not Found")
        else:
            return "Unauthorize"
        
    
    @auth.login_required
    def delete(self, user_id, post_id):
         # Check user exist first
        if user_id == g.current_user.id:
            user = db.session.query(Users).filter(Users.id== user_id).first()
            if user is None:
                # return 404 error 
                raise NotFoundError(status_code=404)

            post = Posts.query.get(post_id)
            db.session.delete(post)
            db.session.commit()
            # Check if the current user in loged in , has permission to delete itself 

            # Check if there are post assosiate for this user, if yes
            # throw error 

            # if no depedency then delete

            return "", 200
        else:
            return "Unauthorize"

    
    @auth.login_required
    def put(self, user_id, post_id):
        if user_id == g.current_user.id:
            args = update_post_parser.parse_args()
            title = args.get("title", None)
            content = args.get("content", None)
            slug = args.get("slug", None)

            ID = user_id
            post = Posts.query.filter_by(id=post_id).first()
            if post:
                if title is None:
                    raise BusinessValidationError(status_code=400, error_code="BE1008", error_message="Title is required")
                
                if content is None:
                    raise BusinessValidationError(status_code=400, error_code="BE1009", error_message="Content is required")

                if slug is None:
                    raise BusinessValidationError(status_code=400, error_code="BE1010", error_message="Slug is required")
                
                post = db.session.query(Posts).filter(Posts.id== post_id).first()
                post.title = title
                post.content = content
                post.slug = slug

                db.session.add(post)
                db.session.commit()
                return '', 200
        else:
            return "Unauthorize"



# ---------------- Login and Verification of password -----------------------
@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

@auth.verify_password
def verify_password(username, password):
    user = Users.query.filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    g.current_user = user
    return user.verify_password(password)

