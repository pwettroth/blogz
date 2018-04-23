from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(15))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/new-blog')
        else:
            flash('Incorrect password or user does not exist', 'error')

    return render_template('login.html')            

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        retype_password = request.form['retype_password']

        if len(username) < 3 or len(username) > 20 or ' ' in username:
            username_error = "Not a valid username"
            return render_template('signup.html', username=username, username_error = username_error)
        if len(password) < 3 or len(password) > 20 or ' ' in password:
            password_error = "Not a valid password"
            return render_template('signup.html', username = username, password_error = password_error)
        if retype_password != password:
            retype_password_error = "Passwords do not match"
            return render_template('signup.html', username = username, retype_password_error = retype_password_error)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/new-blog')
        else:
            flash('Username already exists')
    return render_template('/signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

# TODO Need to fix
@app.route('/', methods =['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods =['GET'])
def list_blogs():
    users = User.query.all()
    if request.args:
        # List a specific blog
        if 'id' in request.args:
            index = request.args['id']
            blog = Blog.query.filter_by(id=index).first()
            if not blog:
                flash("No blog found")
                return redirect('/')
            else:
                blogs = [blog]
                return render_template('blog.html', title=blog.title, blogs=blogs, users=users)
        # List all blogs by a specific user
        elif 'user_id' in request.args:
            user_id = request.args['user_id']
            user = User.query.filter_by(id=user_id).first()
            if not user:
                flash("No user found")
                return redirect('/')
            else:
                blogs = Blog.query.filter_by(owner_id=user_id).all()
                return render_template('blog.html', title=user.username, blogs=blogs, users=users)
    # List all blogs by all users
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", blogs=blogs, users=users)
        

@app.route('/new-blog', methods=['GET', 'POST'])
def new_blog():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        owner = User.query.filter_by(username=session['username']).first()    

        if title and content:
            new_blog = Blog(title, content, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id=" + str(new_blog.id))
        else:
            flash('Must enter title and content', 'error')
            return redirect('/blog')
    else:
        return render_template('new-blog.html', title="Add a Blog")
        
if __name__ == '__main__':
    app.run()

    