from flask import Flask,request,render_template,jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/mynotes'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = 'This_is_a_secret_key'
app.permanent_session_lifetime = timedelta(minutes=100)
db = SQLAlchemy(app)


class UserInfo(db.Model):
    serial=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80), nullable=False, unique=True)
    password=db.Column(db.String(25), nullable=False)
    mobile=db.Column(db.Integer, nullable=False, unique=True)
    date=db.Column(db.String(12), nullable=False)
    bio = db.Column(db.String(100), nullable=False)


class Posts(db.Model):
    serial = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    mobile = db.Column(db.Integer, nullable=False)
    share = db.Column(db.Integer, nullable=False)




@app.route('/')
def home():
    if ('mobilenum' in session) and ('password' in session):
        session.pop('mobilenum', None)
        session.pop('password', None)
    return render_template('index.html')

@app.route('/create',methods= ['POST'])
def createac():
    name = request.form['name']
    password = request.form['password']
    mobile = request.form['mobile']
    bio = request.form['bio']
    date = datetime.now()
    if (name != '' and password != '' and mobile != ''):
        hashed_pass = generate_password_hash(password, method='sha256')
        entered_data = Information(name=name, password=hashed_pass, mobile=mobile, date=date, bio=bio)
        db.session.add(entered_data)
        db.session.commit()
        return jsonify({'output':'<div><h4>SignUp Successful</h4></div>'})
    return jsonify({'error' : 'Missing data!'})

@app.route('/login', methods=['GET','POST'])
def login():
    mobile = request.form['mobile']
    password = request.form['password']
    if (password != '' and mobile != ''):
        details = Information.query.filter_by(mobile=mobile)
        for elements in details:
            if (check_password_hash(password, elements.password)):
                session.permanent = True
                session['mobilenum'] = mobile
                session['password'] = password
                name_of_user = elements.name
                return jsonify({'output': f'<div><h4>Logged in as {name_of_user}</h4></div>' +
                                          '<div ><form id="myNotes" id="add_note" style="display:inline-block"><button '+
                                          ' type="submit" class="mx-4 btn btn-primary" >My Notes</button></form>' +
                                          '<button class="mx-4 btn-primary" id="sharedNotes">Shared Notes</button>' +
                                          '<form id="add_note" style="display:inline-block"><button type="submit" class="mx-4 btn'+
                                          ' btn-primary">Add Note</button></form></div>'})
    return jsonify({'error' : 'Missing data!'})


@app.route('/logout', methods=['GET','POST'])
def logout():
    if ('mobilenum' in session) and ('password' in session):
        session.pop('mobilenum', None)
        session.pop('password', None)
    return redirect(url_for('home'))


@app.route('/mynotes', methods=['POST'])
def mynotes():
    all_post = Posts.query.filter_by(mobile=session['mobilenum'])
    for element in all_post:
        title = element.title
        content = element.content
        date = element.date
        share = element.share
    return jsonify({'output': '<div class="container">'+
			'<div class="row">'+
				'{% for post in element %}'+
				'<div class="col-lg-4 border border-primary mx-2 my-4">'+
					f'<p>{title}</p>'+
					f'<p>{content}</p>'+
					f'<p>Date = {date}</p>'+
					f'<p>Mobile = {session["mobilenum"]}</p>'+

					'<div class="d-flex">'+
						'<form class=" mx-2" action="/edit/{{post.serial}}" method="POST">'+
							'<button type="submit" class="btn btn-primary">Edit</button>'+
						'</form>'+
						'<form class=" mx-2" action="/delete/{{post.serial}}" method="POST">'+
							'<button type="submit" class="btn btn-danger">Delete</button>'+
						'</form>'+
					'</div>'+
				'</div>'+
				'{% endfor %}'+
			'</div>'+
		'</div>'})

@app.route('/addnote', methods=['POST'])
def addnote():
    return jsonify({'output': '<form class="container d-flex flex-column justify-content-center my-4" id="add_form">' +
                              '<input type="text" id="title" name="title" placeholder="Title" required>' +
                              '<br>' +
                              '<textarea id="content" name="content" id="content" cols="30" rows="10" placeholder="Notes" required></textarea>' +
                              '<br>' +
                              '<label for="Yes">Share</label>' +
                              '<input type="radio" id="share" name="share" id="Yes" value="1">' +
                              '<br>' +
                              '<label for="No">Do not Share</label>' +
                              '<input type="radio" id="share" name="share" id="No" value="0" checked>' +
                              '<br>' +
                              '<button type="submit">Submit</button>' +
                              '</form>'})






@app.route('/add', methods=['GET','POST'])
def add():
    if request.method=='POST':
        title = request.form['title']
        content = request.form['content']
        share = request.form['share']
        date = datetime.now()
        add_post = Posts(title=title, content=content, share=share, date=date, mobile=session['mobilenum'])
        db.session.add(add_post)
        db.session.commit()
        return jsonify({'output':'Post Added'})





if __name__ == '__main__':
    app.run(debug=True)