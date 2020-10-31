from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'secret-key'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = 'True',
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']

)
mail=Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contact(db.Model):
    s_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_no = db.Column(db.String(120), unique=True, nullable=False)
    mes = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(120),nullable=True)
class Posts(db.Model):
    SNo = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    sub_title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(120),nullable=True)
    img_file = db.Column(db.String(120), nullable=True)
@app.route("/")
def home():
    posts=Posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template('index.html', params=params,posts=posts)
@app.route("/about")
def about():
    return render_template('about.html', params=params)
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user']== params['admin-user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params,posts=posts)
    if request.method=='POST':
        username=request.form.get('uname')
        userpass = request.form.get('Pass')
        if (username== params['admin-user'] and userpass == params['admin-password']):
            session['user'] = username
            posts=Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)
    return render_template('admin.html', params=params)

@app.route("/edit/<string:SNo>", methods = ['GET', 'POST'])
def edit(SNo):
    if ('user' in session and session['user'] == params['admin-user']):
        if request.method == 'POST':
            name = request.form.get('name')
            title=request.form.get('title')
            sub_title=request.form.get('sub_title')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            date=datetime.now()
            if SNo == '0':
                posts=Posts(title=title,sub_title=sub_title,slug=slug,content=content,img_file=img_file, date=date, name=name)
                db.session.add(posts)
                db.session.commit()
            else:
                posts = Posts.query.filter_by(SNo=SNo).first()
                posts.name=name
                posts.title=title
                posts.sub_title=sub_title
                posts.slug=slug
                posts.content=content
                posts.img_file=img_file
                posts.date=date
                db.session.commit()
                return redirect('/edit/'+SNo)
        posts=Posts.query.filter_by(SNo=SNo).first()
        return render_template('edit.html', params=params,posts=posts)




@app.route("/contact", methods=['GET','POST'])
def contact():
    if request.method == "POST":
        email = request.form.get('email')
        name_s = request.form.get('name')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(name=name_s, email=email, phone_no=phone, mes=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from '+ name_s,
                          sender=email, recipients=[params['gmail-user']], body = message + "\n + phone")
    return render_template('contact.html', params=params)
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    posts = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, posts=posts)

app.run(debug=True)