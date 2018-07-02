from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin #,LoginManager
from app import login, app
from hashlib import md5
from time import time
import jwt

followers = db.Table('followers', 
    db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
    )

# lm = LoginManager(app)
# lm.login_view = 'index'

@login.user_loader #@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #backref argument defines the name of a field that will be added to the objects of the "many" class that points back at the "one" object.
    #lazy argument defines how the database query for the relationship will be issued
    #mode of dynamic sets up the query to not run until specifically requested
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id==id),
        secondaryjoin=(followers.c.followed_id ==id),
        backref=db.backref('followers', lazy='dynamic'),lazy='dynamic'
    )

    def __repr__(self): #__repr__() tells Python how to print objects of this class
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
    def social_photo(self):
        social_id_list=self.social_id.split("$")
        return 'https://graph.facebook.com/v3.0/{}/picture?type=large'.format(social_id_list[1])
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0 #追蹤user的人們
            #looks for items in the association table that have the left side foreign key set to the self user, and the right side set to the user argument.

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password':self.id, 'exp':time()+expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
            ).decode('utf-8')# convert byte to string
    
    @staticmethod # invoked directly from the class
    # A static method is similar to a class method, with the only difference that static methods do not receive the class as a first argument.
    def verify_reset_password_token(token):
        try:
            id=jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)