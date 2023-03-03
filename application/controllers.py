from flask import Flask, request,redirect,url_for,flash
from flask import render_template
from flask import current_app as app
from application.models import Users, Posts, Like
from application.database import db
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms .widgets import TextArea
from flask_login import UserMixin,  login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf.file import FileField  
from werkzeug.utils import secure_filename
import uuid as uuid
import os 

# -------------Login configuration----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#---------------- Add CKEditor -----------------
ckeditor = CKEditor(app)

# ----------- Upload Image path ----------------
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# --------------Create a Form Class --------------
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    about_author = TextAreaField("About Author")
    password_hash = PasswordField("Password",validators=[DataRequired(),EqualTo('password_hash2',message='Password Must match')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField("Submit")

# ---------------- Create a Password Form Class ----------------
class PasswordForm(FlaskForm):
    email = StringField("Whats Your Email", validators=[DataRequired()])
    password_hash = PasswordField("Whats Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class NamerForm(FlaskForm):
    name = StringField("Whats Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")



# ------------------------Create a Posts Form ----------------------
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")
    pic = FileField("Profile Pic")

# -------------------------Create a login form ------------------------
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

#--------------------------- Create a Search form ----------------------
class SearchForm(FlaskForm):
    searched = StringField("search", validators=[DataRequired()])
    submit = SubmitField("Submit")

# -------------------------- Create a UserSearch form -----------------------
class UserSearchForm(FlaskForm):
    searched = StringField("search", validators=[DataRequired()])
    submit = SubmitField("Submit")

# -------------------------- Empty form for following and unfollowing. ----------------
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


# --------------------------------- Create a login Page -------------------------------
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the Hasssed Password
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesfully")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password")
        else:
            flash("User Doesen't Exist")
    return render_template('login.html',form=form)

#-------------------------- Create Log Out Page -----------------------
@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Succesfully Logout")
    return redirect(url_for('login'))


# ---------------------------- Create Dashboard Page -------------------------
@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        # name_to_update.profile_pic = request.files['profile_pic']

        # Check for profile pic 
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']

            # Grab image name
            pic_filenmae = secure_filename(name_to_update.profile_pic.filename)
            # Set UUID 
            pic_name = str(uuid.uuid1()) + "_" + pic_filenmae
            # Save that image
            saver = request.files['profile_pic']
            

            # Change it to string to save it to db
            name_to_update.profile_pic = pic_name

            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("User Updated Succesfully")
                return render_template("dashboard.html", 
                form = form,name_to_update=name_to_update
                )
            except:
                flash("Error... Try Again ")
                return render_template("dashboard.html", 
                form = form,name_to_update=name_to_update
                )
        else:
            db.session.commit()
            flash("User Updated Succesfully")
            return render_template("dashboard.html", 
                form = form,name_to_update=name_to_update
                )
    else:
        return render_template("dashboard.html", 
            form = form,name_to_update=name_to_update, id=id
            )

    return render_template('dashboard.html')


# ------------------------------- Delete a Post by author ------------------------
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    # Get post by post id
    post_to_delete = Posts.query.get_or_404(id)
    # Check post made by logged in user
    if current_user.id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            # return Message
            flash("Blog Post Deleted Succesfully")
            # Grab all the post 
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        except:
        # Return a error message
            flash("Problem deleting post, Pls try again..")
            # Grab all the post 
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("YOu are not allowed to delete that post..")
        # Grab all the post 
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

# ----------------------------- Post page, order all the post by date descending ------------------------------
@app.route('/posts')
def posts():
    # Grab all the posts 
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template("posts.html", posts=posts)

# --------------------------------- Single Page post view with author info ----------------------------------
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

#-------------------------------------- Edit Post Page ----------------------------------------
@app.route('/posts/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit_posts(id):
    # Get post by its id 
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update to the database
        db.session.add(post)
        db.session.commit()
        flash("Post is Updated")
        return redirect(url_for('post', id=post.id))
    # Check for the author and its post ids
    if current_user.id == post.poster_id:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You arent alloed to edit this post")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)

# ------------------------------------------ Add Post Page ------------------------------------
@app.route('/add-post',methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()
    if request.method == 'POST':
        # validate form to submit the data requried with image & other data validation
        # if form.validate_on_submit():
            poster = current_user.id
            # Check for profile pic 
            # if request.files['pic']:
            # Grab image name
            pic_filenmae = secure_filename(request.files['pic'].filename)
            # Set UUID 
            pic_name = str(uuid.uuid1()) + "_" + pic_filenmae
            # Save that image
            saver = request.files['pic']   
            # Change it to string to save it to db
            post_pic = pic_name
            post = Posts(title=form.title.data, content=form.content.data,poster_id=poster, slug=form.slug.data, pic=post_pic)
            # Clear The Form
            form.title.data = ''
            form.content.data=''
            # form.author.data=''
            form.slug.data=''
            try:
                # Add Post data to database
                db.session.add(post)
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                #Return a message
                flash("Blog Post submitted Successfully! ")
            except:
                flash("Error... Try Again ")
                return render_template("add_post.html", form=form)
    # Redirect to the web page
    return render_template("add_post.html", form=form)


 # ------------------------------------ Delete User   ---------------------------------------     
@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    # check for logged in user as delete user 
    if id == current_user.id:
        # get user by user id
        user_to_delete = Users.query.get_or_404(id)
        name = None
        form=UserForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Succesfully")
            our_users= Users.query.order_by(Users.date_added)
            return render_template("add_user.html",form=form, name=name, our_users=our_users)
        except:
            flash("There is error in delete")
            return render_template("add_user.html",form=form, name=name, our_users=our_users)
    else:
        flash("Sorry You have not permission to delete that user.")
        return redirect(url_for('dashboard'))

# --------------------------- Update user Database Record ----------------------------------
@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    form = UserForm()
    # Get user by user id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Succesfully")
            return render_template("update.html", 
            form = form,name_to_update=name_to_update,id=id
            )
        except:
            flash("Error... Try Again ")
            return render_template("update.html", 
            form = form,name_to_update=name_to_update,id=id
            )
    else:
        return render_template("update.html", 
            form=form,name_to_update=name_to_update, id=id
            )

# ----------------Index page shows all the posts by users sorted by descending dates ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    # Grab all the posts 
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template("posts.html", posts=posts)

# ----------------Information about all users personal info along with number of posts, followers and following ------------------
@app.route('/user/<name>')
@login_required
def user(name):
    users = Users.query.all()
    form = EmptyForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    posts = Posts.query.all()

    return render_template("user.html", name_to_update=name_to_update, posts=posts, form=form, users=users)

# ----------------------------------------- Add the user into database ------------------------------------------
@app.route('/user/add', methods=["GET", "POST"])
def add_user():
    name = None
    form=UserForm()
    if form.validate_on_submit():
        # check for the existing user
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the Password !!!
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")

            user = Users(username=form.username.data, name=form.name.data,favorite_color=form.favorite_color.data, email=form.email.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data=''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash("User added Succesfully !")
    our_users= Users.query.order_by(Users.date_added)
    return render_template("add_user.html",form=form, name=name, our_users=our_users)

# -----------------------Create custom error pages -----------------------------

# Invlaid URl
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


# ------------------------------ Create Name Page ----------------------------------
@app.route('/name', methods=['GET','POST'])
def name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form Submitted Succesfully')

    return render_template("name.html", name=name, form=form)


# -------------------------- Create Password test Page ---------------------------
@app.route('/test_pw', methods=['GET','POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form
        form.email.data = ''
        form.password_hash.data = ''
        #Look up User by email Address 
        pw_to_check = Users.query.filter_by(email=email).first()
        # Check Hased password 
        passed=check_password_hash(pw_to_check.password_hash,password)

    return render_template("test_pw.html", email=email, password=password,
    pw_to_check=pw_to_check, passed=passed, form=form)

# ----------------------------- Passed stuff to Navbar ------------------------------
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# ------------------------------Create Search Function on navbar for the keyword searched form posts ---------------------------
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Qwery the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched=post.searched, posts=posts)
    else:
        redirect(url_for('index'))

# -------------------------------- Create Admin Page ----------------------------------------------
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    id = current_user.id
    # Assignment of user id =1 as Admin
    if id == 1:
        return render_template("admin.html")
    else:
        flash("Sorry only admin can access this page..")
        return redirect(url_for('dashboard'))


# --------------------------------- Create Home Page ---------------------------------
@app.route("/home/<id>", methods=["GET", "POST"])
@login_required
def home(id):
    id = current_user.id
    posts = Posts.query.filter_by(poster_id=current_user.id)
    return render_template("home.html", posts=posts)


# ---------------------------------------- Create Like post  ------------------------------------
@app.route("/like-post/<int:id>", methods=["GET", "POST"])
@login_required
def like(id):
    # Search post by id 
    post = Posts.query.filter_by(id=id)
    like = Like.query.filter_by(author=current_user.id, post_id=id).first()

    if not post:
        flash("Post does not exist")
    # if like exist already by user, delete like
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        # if like doesent exist already by user, delete like
        like = Like(author=current_user.id, post_id=id)
        db.session.add(like)
        db.session.commit()
    
    return redirect(url_for('posts'))


# ------------------------------ Follow and unfollow routes. ------------------------------------
@app.route('/follow/<username>', methods=['POST','GET'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        # Get user by username
        user = Users.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        # if follow user and current user logged in are same, you cant follow yourself
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', name=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', name=username))
    else:
        return redirect(url_for('index'))

# unfollowing the user
@app.route('/unfollow/<username>', methods=['POST','GET'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        # Get user by username
        user = Users.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        # if unfollow user and current user logged in are same, you cant unfollow yourself
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', name=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', name=username))
    else:
        return redirect(url_for('index'))


# -------------------------- get followers list of author ------------------------------------
@app.route('/followers/<username>', methods=['GET','POST'])
@login_required
def followers(username):
    # Get user by username
    user = Users.query.filter_by(username=username).first()
    users = user.followers.all() 
    users_all = Users.query.all()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if user is None:
        flash('Invalid user.')
    else:
        return render_template('followers.html', users=users,user=user,users_all=users_all, name_to_update=name_to_update )
    # return redirect(url_for('index'))


# ---------------------------- get followed list of author ----------------------------------------------
@app.route('/followed/<username>', methods=['GET','POST'])
@login_required
def followed(username):
    # Get user by username
    user = Users.query.filter_by(username=username).first()
    users = user.followed.all()
    users_all = Users.query.all()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if user is None:
        flash('Invalid user.')
    else:
        return render_template('followers.html', users=users, user=user,users_all=users_all, name_to_update=name_to_update )

# ---------------------------------- Search user option to search for the users -----------------------------------
@app.route('/search_user', methods=['GET','POST'])
@login_required
def search_user():
    form = UserSearchForm()
    users = Users.query
    if form.validate_on_submit():
        # Get data from submitted form
        searched = form.searched.data
        # Qwery the database
        users = users.filter(Users.username.like('%' + form.searched.data + '%'))
        users = users.order_by(Users.date_added.asc()).all()
        
    return render_template("search_user.html", form=form, searched=form.searched, users=users)

