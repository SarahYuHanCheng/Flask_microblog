from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin #,LoginManager
from hashlib import md5
from time import time
import jwt
from flask import current_app, url_for
import base64
import os
from app import db, login

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


followers = db.Table('followers', 
    db.Column('follower_id',db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id',db.Integer, db.ForeignKey('user.id'))
    )

# ranks = db.Table('ranks', 
#     db.Column('player_id',db.Integer, db.ForeignKey('user.id')),
#     db.Column('game_id',db.Integer, db.ForeignKey('game.id'))
#     )



# lm = LoginManager(app)
# lm.login_view = 'index'

@login.user_loader #@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    social_id = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #backref argument defines the name of a field that will be added to the objects of the "many" class that points back at the "one" object.
    #lazy argument defines how the database query for the relationship will be issued
    #mode of dynamic sets up the query to not run until specifically requested
    
    # about_me =db.deferred( db.Column(db.String(140)))
    # last_seen = db.deferred(db.Column(db.DateTime, default=datetime.utcnow))
    
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
            current_app.config['SECRET_KEY'], algorithm='HS256'
            ).decode('utf-8')# convert byte to string
    
    @staticmethod # invoked directly from the class
    # A static method is similar to a class method, with the only difference that static methods do not receive the class as a first argument.
    def verify_reset_password_token(token):
        try:
            id=jwt.decode(token, current_app.config['SECRET_KEY'],algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def to_dict(self, include_email=False):
        print('self:',self.id)
        data = {
            'id':self.id,
            'username': self.username,
            'last_seen':self.about_me,
            'post_count': self.posts.count(),
            'follower_count':self.followers.count(),
            'followed_id': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email']=self.email 
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me','id']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token   
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user   

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1024))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    commit_msg = db.Column(db.String(140))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id')) 
    log_id = db.Column(db.Integer, db.ForeignKey('log.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # comment = db.relationship('Comment', backref='code', lazy='dynamic')
    
    def get_comments(self):
        comment_list = Comment.query.filter_by(code_id = self.id).order_by(Comment.timestamp.desc())
        return comment_list

    def __repr__(self):
        return '<Code {}>'.format(self.body)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_content = db.Column(db.String(1024),default='record_content')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer,default='100200')
    code_id_list = db.Column(db.Integer, db.ForeignKey('code.id'))
    # codes = db.relationship('Code', backref='to_log', lazy='dynamic')
    
    def __repr__(self):
        return '<Log {}>'.format(self.game_id)
    
    def get_rank_list(self):
        game_log = Log.query.filter_by(game_id = self.game_id)
        # rank_list = 
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_codes(self):
        codes = Code.query.filter_by(log_id = self.id).order_by(Comment.timestamp.desc())
        return comment_list

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gamename = db.Column(db.String(30))
    descript = db.Column(db.String(1024))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_lib = db.Column(db.String(10240))
    example_code = db.Column(db.String(1024))
    # codes = db.relationship('Code', backref='game', lazy='dynamic')
    
    
    def __repr__(self):
        return '<Game {}>'.format(self.descript)

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return

    def get_commited_codes(self):
        #若code只有log_id沒有game_id 就要用 in(game_logs)
        game_logs = Log.query.filter_by(game_id= self.id).order_by(Game.timestamp.desc())
        
        code_list = Code.query.filter_by(game_id = self.id).order_by(Game.timestamp.desc())
        return code_list
    

class Comment(db.Model):
    """docstring for Comment"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    code_id = db.Column(db.Integer, db.ForeignKey('code.id'))

    def __repr__(self):
        return '<Comment {}>'.format(self.body)
   
        
