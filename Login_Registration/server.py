from flask import Flask, flash, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
import re
from mysqlconnection import connectToMySQL

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'supersupersecret'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration', methods=['POST'])
def registration():
    error = False

    mysql = connectToMySQL('users_db')
    query = "SELECT email FROM users WHERE email = %(email)s"
    data = {
        "email": request.form['email']
    }
    email = mysql.query_db(query, data)
    if len(email) != 0 or len(request.form['email'])==0:
        error = True
        
    if not EMAIL_REGEX.match(request.form['email']): 
        error = True
    
    if len(request.form['first_name']) < 2 or len(request.form['last_name']) < 2:
        error = True
    
    if len(request.form['password']) < 8:
        error = True

    if request.form['password'] != request.form['confirm_pw']:
        error = True
    
    if error:
        flash('Invalid Registration Credentials','registration')
        return redirect('/')

    mysql = connectToMySQL('users_db')
    query = "INSERT INTO users (users.first_name, users.last_name, users.email, users.password, users.created_at, users.updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(hashed_pw)s, NOW(), NOW());"
    hashed_pw = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "hashed_pw": hashed_pw
    }
    mysql.query_db(query, data)
    flash("Thanks for Registering", 'registration')
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL('users_db')
    query = "SELECT * FROM users WHERE email = %(email)s"
    data = {
        "email": request.form['email']
    }
    users = mysql.query_db(query, data)
    if len(users) == 0:
        flash ("Invalid Login Credentials",'login')
        return redirect ('/')
    user = users[0]
    if bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Successful Login','login')
    else:
        flash("Invalid Login Attempt", 'login')
    return redirect ('/')


if __name__=="__main__":   
    app.run(debug=True)    