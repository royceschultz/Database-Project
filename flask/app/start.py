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
    PAGE_SIZE = 5
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PAGE_SIZE
    query = database.QuestionScore.select().order_by(database.QuestionScore.c.dt_created.desc()).offset(offset).limit(PAGE_SIZE)
    questions = []
    with database.Connect() as connection:
        res = connection.execute(query)
        for row in res:
            questions.append(row)
    return render_template('index.html', questions=questions, page=page, next_page=(len(questions) == PAGE_SIZE))

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
    username = request.form['username']
    password = request.form['password']
    # Query database for user
    query = database.User.select().where(database.User.c.username == username)
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
    session_query = database.UserSession.insert().values(session_id=session_id, uid=user.uid)
    with database.Connect() as connection: # Save new session to database
        connection.execute(session_query)
    # Set user cookie
    response = redirect(url_for('home'))
    response.set_cookie('session_token', ';'.join([str(user.uid), session_id]))
    return response

@app.route('/logout')
@auth.require_login
def logout():
    # Delete UserSession from Database, if it exists
    # Then redirect to login page
    if g.session_id:
        delete_query = database.UserSession.delete().where(database.UserSession.c.session_id == g.session_id, database.UserSession.c.uid == g.user)
        database.Connect().execute(delete_query)
        g.bad_cookie = True
    return redirect(url_for('login'))

@app.route('/profile/<username>', methods=['GET', 'POST'])
@auth.require_login
def profile(username):
    query = database.User.select().where(database.User.c.username == username)
    res = database.Connect().execute(query)
    user = res.fetchone()
    is_self = False
    if 'user' in g:
        is_self = (g.user == username)
    return render_template('profile.html', is_self=is_self, user=user)

@app.route('/profile/questions/<username>', methods=['GET', 'POST'])
@auth.require_login
def profile_questions(username):
    conn = database.Connect()
    # Lookup uid
    query = database.User.select().where(database.User.c.username == username)
    uid = conn.execute(query).fetchone().uid
    query = database.QuestionScore.select().where(database.QuestionScore.c.uid == uid)
    questions = conn.execute(query).fetchall()
    return render_template('profile_questions.html', questions=questions, username=username)

@app.route('/profile/answers/<username>', methods=['GET', 'POST'])
@auth.require_login
def profile_answers(username):
    conn = database.Connect()
    # Lookup uid
    query = database.User.select().where(database.User.c.username == username)
    uid = conn.execute(query).fetchone().uid
    query = database.AnswerScore.select().where(database.AnswerScore.c.uid == uid)
    answers = conn.execute(query).fetchall()
    return render_template('profile_answers.html', answers=answers, username=username)



@app.route('/profile/edit', methods=['GET', 'POST'])
@auth.require_login
def edit_profile():
    if request.method == 'GET':
        query = database.User.select().where(database.User.c.uid == g.user)
        with database.Connect() as connection:
            res = connection.execute(query)
            user = res.fetchone()
        return render_template('profile_edit.html', user=user)
    if request.method == 'POST':
        # get form data
        new_username = request.form['username']
        new_email = request.form['email']
        old_password = request.form['old_password']
        new_password = request.form.get('new_password', None)
        confirm_password = request.form.get('password_confirmation', None)
        new_state = request.form['state']
        new_country = request.form['country']
        new_city = request.form['city']
        new_bio = request.form['bio']

        conn = database.Connect()

        # Obscure old password in form data (returned back to user)
        new_password = None
        # verify old password
        query = database.User.select().where(database.User.c.uid == g.user, database.User.c.password == old_password)
        res = conn.execute(query)
        user = res.fetchone()
        messages = []
        has_errors = False
        if user is None:
            has_errors = True
            return render_template('profile_edit.html', message='Incorrect Password', has_errors=has_errors, user=request.form)
        # check if new username is taken
        if new_username != user.username:
            query = database.User.select().where(database.User.c.username == new_username)
            res = conn.execute(query)
            other_user = res.fetchone()
            if other_user is not None:
                messages.append('Username already taken')
                has_errors = True
        # check if new email is taken
        if new_email != user.email:
            query = database.User.select().where(database.User.c.email == new_email)
            res = conn.execute(query)
            other_user = res.fetchone()
            if other_user is not None:
                messages.append('Email already taken')
                has_errors = True
        # check if new password is correct (if given)
        if new_password and new_password != new_password_confirmation:
            messages.append('Passwords do not match')
            has_errors = True
        else: # If no new password, keep old password
            new_password = old_password
        if has_errors:
            return render_template('profile_edit.html', message='.'.join(messages), user=user)
        # update user
        update_query = database.User.update().where(database.User.c.uid == g.user).values(username=new_username, email=new_email, password=new_password, state=new_state, country=new_country, city=new_city, bio=new_bio)
        with database.Connect() as connection:
            try:
                connection.execute(update_query)
            except Exception as e:
                return render_template('profile_edit.html', message=e, user=request.form) 
        return redirect(url_for('profile', username=new_username))

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
        insert_query = database.Question.insert().values(title=title, body=body, topic=topic, uid=g.user)
        try:
            res = database.Connect().execute(insert_query)
            data = []
            for r in res:
                data.append(r)
            # TODO Get question id, redirect to question page
            return render_template('new_question.html', message=res.keys())
        except Exception as e:
            return render_template('new_question.html', message=e)

@app.route('/question/<int:question_id>')
def question(question_id):
    # View for a specific question
    query = database.Question.select().where(database.Question.c.qid == question_id)
    query = database.QuestionScore.select().where(database.QuestionScore.c.qid == question_id)
    question = database.Connect().execute(query).fetchone()
    assert question is not None
    # Get all answers for this question
    answers_query = database.AnswerScore.select().where(database.AnswerScore.c.qid == question_id)
    answers = database.Connect().execute(answers_query).fetchall()
    print(len(answers))
    return render_template('question.html', question=question, answers=answers)

@app.route('/post/answer', methods=['POST'])
@auth.require_login
def submit_answer():
    question_id = request.form['question_id']
    body = request.form['answer']
    # Validate answer
    assert(len(body) > 10)
    insert_query = database.Answer.insert().values(qid=question_id, body=body, uid=g.user)
    try:
        database.Connect().execute(insert_query)
        return redirect(url_for('question', question_id=question_id))
    except Exception as e:
        return redirect(url_for('home', message=e))

@app.route('/vote/question')
@auth.require_login
def vote_question():
    # get user and question and vote
    user = g.user
    question_id = request.args.get('question_id')
    vote = int(request.args.get('vote'))
    assert vote in [1, -1]
    vote_bool = vote > 0
    # Check if user has already voted on this question
    query = database.QuestionRating.select().where(database.QuestionRating.c.qid == question_id, database.QuestionRating.c.uid == user)
    conn = database.Connect()
    existing_rating = conn.execute(query).fetchone()
    # If vote exists and is the same as the new vote, delete the vote
    if existing_rating is not None and existing_rating.is_upvote == vote_bool:
            # Undo vote
            delete_query = database.QuestionRating.delete().where(database.QuestionRating.c.qid == question_id, database.QuestionRating.c.uid == user)
            conn.execute(delete_query)
    else: # Update users vote to new vote
        vote_query = f'''
            REPLACE INTO QuestionRating (qid, is_upvote, uid)
                VALUES ({question_id}, {vote==1}, {g.user})
        '''
        database.Connect().execute(vote_query)
    return redirect(url_for('question', question_id=question_id))

@app.route('/vote/answer')
@auth.require_login
def vote_answer():
    # get user, answer and vote
    user = g.user
    answer_id = request.args.get('answer_id')
    vote = int(request.args.get('vote'))
    assert vote in [1, -1]
    vote_bool = vote > 0
    # Check if user has already voted on this question
    query = database.AnswerRating.select().where(database.AnswerRating.c.aid == answer_id, database.AnswerRating.c.uid == user)
    conn = database.Connect()
    existing_rating = conn.execute(query).fetchone()
    # If vote exists and is the same as the new vote, delete the vote
    if existing_rating is not None and existing_rating.is_upvote == vote_bool:
            # Undo vote
            delete_query = database.AnswerRating.delete().where(database.AnswerRating.c.aid == answer_id, database.AnswerRating.c.uid == user)
            conn.execute(delete_query)
    else: # Update users vote to new vote
        vote_query = f'''
            REPLACE INTO AnswerRating (aid, is_upvote, uid)
            VALUES ({answer_id}, {vote==1}, {g.user})
        '''
        database.Connect().execute(vote_query)

    # Get question id from answer
    query = database.Answer.select().where(database.Answer.c.aid == answer_id)
    question_id = database.Connect().execute(query).fetchone().qid
    return redirect(url_for('question', question_id=question_id))

@app.route('/pin/answer')
@auth.require_login
def pin_answer():
    # get user and answer
    user = g.user
    answer_id = request.args.get('answer_id')
    conn = database.Connect()
    # Get question from answer
    query = database.Answer.select().where(database.Answer.c.aid == answer_id)
    question_id = conn.execute(query).fetchone().question
    # Check user is op of question
    query = database.Question.select().where(database.Question.c.qid == question_id, database.Question.c.uid == user)
    if conn.execute(query).fetchone() is None:
        # ERROR: User is not op of question
        return
    else:
        # Check if answer is already pinned
        query = database.PinnedAnswer.select().where(database.PinnedAnswer.c.aid == answer_id)
        if conn.execute(query).fetchone() is not None:
            # Already pinned, remove it
            delete_query = database.PinnedAnswer.delete().where(database.PinnedAnswer.c.aid == answer_id)
            conn.execute(delete_query)
        else:
            # Pin answer
            insert_query = f'''
                REPLACE INTO PinnedAnswer (question, answer)
                VALUES ({question_id}, {answer_id})
            '''
            conn.execute(insert_query)
    return redirect(url_for('question', question_id=question_id))



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
            uid, session_id = session_token
            query = database.UserSession.select().where(database.UserSession.c.session_id == session_id, database.UserSession.c.uid == uid)
            res = database.Connect().execute(query)
            user_session = res.fetchone()
            if user_session is not None:
                g.user = user_session.uid
                g.session_id = user_session.session_id

                # lookup username
                query = database.User.select().where(database.User.c.uid == g.user)
                res = database.Connect().execute(query)
                g.username = res.fetchone().username
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
