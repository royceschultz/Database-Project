# App Dependencies
from flask import Flask
from flask import request, Response, render_template, url_for, redirect, g
import database
import random

app = Flask(__name__)

@app.route("/")
def home():
    query = database.Question.select().order_by(database.Question.c.qid.desc()).limit(10)
    with database.Connect as connection:
        res = connection.execute(query)
        questions = []
        for row in res:
            questions.append(row)
    return render_template('index.html', questions=questions)

@app.route('/register', methods=['GET', 'POST'])
def register():
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
    if request.method == 'GET':
        return render_template('login.html')
    assert request.method == 'POST'
    usename = request.form['username']
    password = request.form['password']
    query = database.User.select().where(database.User.c.username == usename)
    res = database.Connect().execute(query)
    user = res.fetchone()
    if user is None:
        return render_template('login.html', message='User Not Found')
    if user.password == password:
        # TODO: Create a user session
        session_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=128))
        session_query = database.UserSession.insert().values(session_id=session_id, username=user.username)
        try:
            database.Connect().execute(session_query)
            # set user cookie
            response = redirect(url_for('home'))
            response.set_cookie('session_token', ';'.join([user.username, session_id]))
            return response
        except Exception as e:
            return render_template('login.html', message=e)
        return url_for('home')
    return render_template('login.html', message='Incorrect Password')

@app.route('/logout')
def logout():
    if g.session_id:
        delete_query = database.UserSession.delete().where(database.UserSession.c.session_id == g.session_id, database.UserSession.c.username == g.user)
        database.Connect().execute(delete_query)
        g.bad_cookie = True
        return redirect(url_for('login'))
    return render_template('logout.html')

@app.route('/profile/<username>')
def profile(username):
    return render_template('profile.html')

@app.route('/profile/edit')
def edit_profile():
    return render_template('edit_profile.html')

@app.route('/post/question', methods=['GET', 'POST'])
def new_question():
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
    query = database.Question.select().where(database.Question.c.qid == question_id)
    question = database.Connect().execute(query).fetchone()
    return render_template('question.html', question=question)

@app.route('/post/answer')
def post_answer():
    return render_template('post_answer.html')

@app.route('/vote')
def vote():
    return render_template('vote.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/test')
def test():
    conn = database.Connect()
    res = conn.execute('SELECT * FROM User')
    users = []
    for row in res:
        users.append(row)
        if len(users) > 10:
            break
    template = ' '.join(['<p>%s</p>' % user for user in users])
    return Response(template)

@app.before_request
def before_request():
    # Verify or create user, populate g context, log request
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
