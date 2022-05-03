# App Dependencies
from flask import Flask
from flask import request, Response, render_template, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
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

@app.route('/question')
def question():
    return render_template('question.html')

@app.route('/post/answer')
def post_answer():
    return render_template('post_answer.html')

@app.route('/vote')
def vote():
    return render_template('vote.html')

@app.route('/search')
def search():
    return render_template('search.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
