from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(500))

    def __init__(self, title, content):
        self.title = title
        self.content = content

@app.route('/', methods =['POST', 'GET'])
def index():    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if title and content:
            new_blog = Blog(title, content)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id=" + str(new_blog.id))
        else:
            flash('Must enter title and content', 'error')
            return redirect('/new-blog')

    blogs = Blog.query.all()
    return render_template('main-page.html', title="Build a Blog", blogs=blogs)

@app.route('/blog', methods =['GET'])
def blog():
    index = request.args['id']
    blog = Blog.query.filter_by(id=index).first()

    if not blog:
        flash("No blog found")
        return redirect('/')
    
    return render_template('blog.html', title=blog.title, blog=blog)


@app.route('/new-blog', methods=['GET'])
def new_blog():
    return render_template('new-blog.html', title="Add a Blog")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()