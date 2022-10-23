from datetime import datetime

from flask import Flask, render_template, session, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config['SECRET_KEY'] = 'This is secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://henry:cooper229@127.0.0.1:5432/prac_01'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)

class Client(db.Model):
    __tablename__ = 'client'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    profile_image = db.Column(db.String, default='default.png')
    
    # posts = db.relationship('Post', backref='author', lazy=True)
    
class ClientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'password', 'profile_image')

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    
    # user_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    
    # def __repr__(self):
        # return f"<Post('{self.id}','{self.title}')>"
      
class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'content', 'date_posted')

@app.cli.command('create')
def create_db():
    db.create_all()
    print('Tables created successfully')
    
@app.cli.command('drop')
def drop_db():
    db.drop_all()
    print('All tables dropped successfully')

@app.cli.command('seed')
def seed_db():
    client = [
        Client(
            username = "Henry Chun",
            email = "cooper@email.com",
            password = bcrypt.generate_password_hash('1234').decode('utf-8')
        )
    ]
    post = [
        Post(
            title = 'The first post',
            content = 'Contents of the first thing',
            # author = client
        ),
        Post(
            title = 'The second post',
            content = 'Contents of the second thing',
            # author = client
        )
    ]
    
    db.session.add_all(client)
    db.session.add_all(post)
    db.session.commit()
    print('Tables inserted')
    
@app.route('/')
def homepage():
    if session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')
      
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        stmt = db.select(Client).filter_by( email=request.form['email'] )
        user = db.session.scalar(stmt)
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            # return UserSchema(exclude=['password']).dump(user)
            # token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
            session['logged_in'] = True
            return redirect(url_for('homepage'))
        else:
            return {'error': 'Wrong userID or password'}, 444
    else:
        return render_template('login.html')
      
@app.route('/register/', methods=['GET', 'POST'])
def register():
    # user_info = ClientSchema().load(request.json)
    # print('****YOGIDA1', user_info)
    if request.method == 'POST':
        try:
            client = Client(
                email= request.json['email'],
                password=bcrypt.generate_password_hash(request.json['password']).decode('utf-8'),
                username=request.json['username']
            )
            db.session.add(client)
            db.session.commit()
            return redirect(url_for('login'))
            # return UserSchema(exclude=['password']).dump(user), 201
        except IntegrityError:
            return {'error': 'Email address already in use'}, 409
    else:
        return render_template('register.html')
      
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('index.html')
