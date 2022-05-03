# App Dependencies
from flask import Flask
from flask import request, Response, render_template, url_for
import database

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        return Response('<h1>Thanks for registering</h1>')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    assert request.method == 'POST'
    usename = request.form['username']
    password = request.form['password']
    if usename == 'admin' and password == 'password':
        # Set cookie
        response = Response('<h1>You are logged in</h1>')
        response.set_cookie('username', usename, expires=None)
        return response
    return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/profile/edit')
def edit_profile():
    return render_template('edit_profile.html')

@app.route('/post/question')
def post_question():
    return render_template('post_question.html')

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
    user_cookie = request.cookies.get('user')
    # if user exists, populate g context
        # g.user = user

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
