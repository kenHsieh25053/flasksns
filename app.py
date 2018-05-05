from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_login import current_user


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://postgres:kw1984@localhost/snsdb'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = '$2a$16$PnnIgfMwkOjGX4SkHqSOPO'
app.config['SECURITY_REGISTERABLE'] = True


# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

class UserDetails(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer)
	username = db.Column(db.String(100))
	profile_pic = db.Column(db.String(300))
	location = db.Column(db.String(100))

	def __init__(self, user_id, username, profile_pic, location):
		self.user_id = user_id
		self.username = username
		self.profile_pic = profile_pic
		self.location = location

	def __respr__(self):
		return '<Userdetails %r>' % self.username

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	post_content = db.Column(db.String(200))
	posted_by = db.Column(db.String(100))

	def __init__(self, post_content, posted_by):
		self.post_content = post_content
		self.posted_by = posted_by

	def __respr__(self):
		return '<Posr %r>' % self.post_content


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.route('/')
@login_required
def index():
	return 'Welcome to mywebsite'

@app.route('/posting')
@login_required
def posting():
	now_user = User.query.filter_by(email = current_user.email).first()
	return render_template('add_post.html', now_user = now_user)

@app.route('/add_post', methods=['POST'])
def add_post():
	post = Post(request.form['pcontent'], request.form['pemail'])
	db.session.add(post)
	db.session.commit()
	return redirect(url_for('index'))

@app.route('/user_list')
@login_required
def get_user_list():
	users = User.query.all()
	userD = UserDetails.query.all()
	return render_template('user_list.html', users = users, userD = userD)

@app.route('/feed')
def get_post():
	singlePost = Post.query.all()
	return render_template('post_feed.html', singlePost = singlePost)

@app.route('/editprofile')
@login_required
def edit_profile():
	now_user = User.query.filter_by(email = current_user.email).first()
	return render_template('user_detail.html', now_user = now_user)

@app.route('/add_user_details', methods=['POST'])
def add_user_details():
	user_details = UserDetails(request.form['pid'], request.form['username'], 
		request.form['profile_pic'], request.form['location'])
	db.session.add(user_details)
	db.session.commit()
	return redirect(url_for('index'))

@app.route('/profile/<id>')
def user_profile(id):
	oneUser = UserDetails.query.filter_by(id = id).first()
	sUser = User.query.filter_by(id = oneUser.user_id).first()
	user_posts = Post.query.filter_by(posted_by = sUser.email)
	return render_template('user_profile.html', oneUser = oneUser, sUser = sUser, user_posts = user_posts)


if __name__ == '__main__':
	app.run(debug = True)