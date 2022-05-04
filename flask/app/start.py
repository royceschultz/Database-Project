# App Dependencies
from flask import Flask
from flask import request, Response, render_template, url_for, redirect, g
import random

# local imports
import database
import auth

app = Flask(__name__)

@app.route("/")
def home():
    # Home page for all users
    # Shows recently posted questions
    query = database.Question.select().order_by(database.Question.c.qid.desc()).limit(10)
    with database.Connect() as connection:
        res = connection.execute(query)
        questions = []
        for row in res:
            questions.append(row)
    return render_template('index.html', questions=questions)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Register page for new users to create an account
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['password_confirmation']

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")
        
        insert_query = database.User.insert().values(username=username, email=email, password=password)
        try:
            database.Connect().execute(insert_query)
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            return render_template('register.html', message=e)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login page for existing users to log in
    if request.method == 'GET': 
        return render_template('login.html')
    assert request.method == 'POST'
    # Get username and password from form
    usename = request.form['username']
    password = request.form['password']
    # Query database for user
    query = database.User.select().where(database.User.c.username == usename)
    res = database.Connect().execute(query)
    user = res.fetchone()
    if user is None: # User not found
        return render_template('login.html', message='User Not Found')
    if user.password != password: # Incorrect password
        return render_template('login.html', message='Incorrect Password')
    # User found, log them in
    # Genarate a new session id
    session_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=128))
    # Insert session id into database
    session_query = database.UserSession.insert().values(session_id=session_id, username=user.username)
    with database.Connect() as connection: # Save new session to database
        connection.execute(session_query)
    # Set user cookie
    response = redirect(url_for('home'))
    response.set_cookie('session_token', ';'.join([user.username, session_id]))
    return response

@app.route('/logout')
@auth.require_login
def logout():
    # Delete UserSession from Database, if it exists
    # Then redirect to login page
    if g.session_id:
        delete_query = database.UserSession.delete().where(database.UserSession.c.session_id == g.session_id, database.UserSession.c.username == g.user)
        database.Connect().execute(delete_query)
        g.bad_cookie = True
    return redirect(url_for('login'))

@app.route('/profile/<username>')
@auth.require_login
def profile(username):
    query = database.User.select().where(database.User.c.username == username)
    with database.Connect() as connection:
        res = connection.execute(query)
        user = res.fetchone()
    is_self = False
    if 'user' in g:
        if g.user == username:
            is_self = True
    return render_template('profile.html', is_self=is_self, user=user)

@app.route('/edit/profile/')
def edit_profile():
    return render_template('edit_profile.html')

@app.route('/post/question', methods=['GET', 'POST'])
@auth.require_login
def new_question():
    # Page for users to post a new question
    if request.method == 'GET':
        return render_template('new_question.html')
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        topic = request.form['topic']
        insert_query = database.Question.insert().values(title=title, body=body, topic=topic, username=g.user).returning(database.Question.c.qid)
        try:
            res = database.Connect().execute(insert_query)
            data = []
            for r in res:
                data.append(r)
            return render_template('new_question.html', message=data)
        except Exception as e:
            return render_template('new_question.html', message=e)

@app.route('/question/<int:question_id>')
def question(question_id):
    # View for a specific question
    query = database.Question.select().where(database.Question.c.qid == question_id)
    question = database.Connect().execute(query).fetchone()
    assert question is not None
    # Get all answers for this question
    answers_query = database.Answer.select().where(database.Answer.c.question == question_id)
    answers = database.Connect().execute(answers_query).fetchall()
    return render_template('question.html', question=question, answers=answers)

@app.route('/post/answer', methods=['POST'])
@auth.require_login
def submit_answer():
    question_id = request.form['question_id']
    body = request.form['answer']
    # Validate answer
    assert(len(body) > 10)
    insert_query = database.Answer.insert().values(question=question_id, body=body, username=g.user)
    try:
        database.Connect().execute(insert_query)
        return redirect(url_for('question', question_id=question_id))
    except Exception as e:
        return redirect(url_for('home'))

@app.route('/vote')
@auth.require_login
def vote():
    return render_template('vote.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.before_request
def before_request():
    # Check if user is logged in via session_token cookie
    session_token = request.cookies.get('session_token')
    if session_token is not None:
        session_token = session_token.split(';')
        if len(session_token) == 2:
            username, session_id = session_token
            query = database.UserSession.select().where(database.UserSession.c.session_id == session_id, database.UserSession.c.username == username)
            res = database.Connect().execute(query)
            user_session = res.fetchone()
            if user_session is not None:
                g.user = user_session.username
                g.session_id = user_session.session_id
            else:
                g.bad_cookie=True
        else:
            g.bad_cookie=True

@app.after_request
def after_request(response):
    # Maintain user cookies
    if 'bad_cookie' in g:
        response.set_cookie('session_token', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
