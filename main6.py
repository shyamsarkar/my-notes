from flask import Flask,request,render_template,jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/mynotes'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = 'This_is_a_secret_key'
app.permanent_session_lifetime = timedelta(minutes=100)
db = SQLAlchemy(app)


class Information(db.Model):
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
    return render_template('ajax2.html')

@app.route('/create',methods= ['POST'])
def createac():
    name = request.form['name']
    password = request.form['password']
    mobile = request.form['mobile']
    bio = request.form['bio']
    date = datetime.now()
    if (name != '' and password != '' and mobile != ''):
        hashed_pass = sha256_crypt.encrypt(password)
        entered_data = Information(name=name, password=hashed_pass, mobile=mobile, date=date, bio=bio)
        db.session.add(entered_data)
        db.session.commit()
        return jsonify({'output':'<div><h4>SignUp Successful</h4></div>'})
    return jsonify({'error' : 'Missing data!'})

@app.route('/login', methods=['GET','POST'])
def login():
    if ('mobilenum' in session) and ('password' in session):
        details = Information.query.filter_by(mobile=session['mobilenum'])
        for elements in details:
            if (sha256_crypt.verify(session['password'], elements.password)):
                name_of_user = elements.name
                return jsonify({'output': f'<div><h4>Already Logged in as {name_of_user}</h4></div>'+
                                '<div ><button class="mx-4 btn btn-primary" id="myNotes">My Notes</button>'+
                                '<button class="mx-4 btn-primary" id="sharedNotes">Shared Notes</button>'+
                                '<button class="mx-4 btn btn-primary" id="AddNote">Add Note</button></div>'})
    mobile = request.form['mobile']
    password = request.form['password']
    if (password != '' and mobile != ''):
        details = Information.query.filter_by(mobile=mobile)
        for elements in details:
            if (sha256_crypt.verify(password, elements.password)):
                session.permanent = True
                session['mobilenum'] = mobile
                session['password'] = password
                name_of_user = elements.name
                return jsonify({'output': f'<div><h4>Logged in as {name_of_user}</h4></div>' +
                                          '<div ><button class="mx-4 btn btn-primary" id="myNotes">My Notes</button>' +
                                          '<button class="mx-4 btn-primary" id="sharedNotes">Shared Notes</button>' +
                                          '<button class="mx-4 btn btn-primary"  id="AddNote" onclick="toggleHide()">Add Note</button></div>'})
    return jsonify({'error' : 'Missing data!'})


@app.route('/logout', methods=['GET','POST'])
def logout():
    if ('mobilenum' in session) and ('password' in session):
        session.pop('mobilenum', None)
        session.pop('password', None)
    return redirect(url_for('home'))


@app.route('/mynotes', methods=['POST'])
def mynotes():
    pass

@app.route('/addnote', methods=['POST'])
def addnote():
    return jsonify({'output': '<form id="add_form">' +
                              '<input type="text" name="title" placeholder="Title" required>' +
                              '<br>' +
                              '<textarea name="content" id="content" cols="30" rows="10" placeholder="Notes" required></textarea>' +
                              '<br>' +
                              '<label for="Yes">Share</label>' +
                              '<input type="radio" name="share" id="Yes" value="1">' +
                              '<br>' +
                              '<label for="No">Do not Share</label>' +
                              '<input type="radio" name="share" id="No" value="0" checked>' +
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