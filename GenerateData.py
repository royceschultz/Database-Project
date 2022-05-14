from sqlalchemy import create_engine, MetaData, Table
from faker import Faker
import random

engine = create_engine('mysql+pymysql://root:example@localhost:3306/QueueOverflow') # , echo=True)
metadata = MetaData()
User = Table('User', metadata, autoload=True, autoload_with=engine)
Topic = Table('Topic', metadata, autoload=True, autoload_with=engine)
Question = Table('Question', metadata, autoload=True, autoload_with=engine)
Answer = Table('Answer', metadata, autoload=True, autoload_with=engine)
PinnedAnswer = Table('PinnedAnswer', metadata, autoload=True, autoload_with=engine)
QuestionRating = Table('QuestionRating', metadata, autoload=True, autoload_with=engine)
AnswerRating = Table('AnswerRating', metadata, autoload=True, autoload_with=engine)

N = 32
N_USERS = N
N_QUESTIONS = 2*N
N_ANSWERS = 4*N
N_QUESTION_RATINGS = 8*N
N_ANSWER_RATINGS = 8*N
N_PINNED_ANSWERS = 2*N

USERS = []
TOPICS = ['Programming', 'Python', 'Javascript', 'SQL', 'Announcements', 'General', 'Misc']
QUESTIONS = []
ANSWERS = []

F = Faker()

with engine.connect() as connection:
    # Generate users
    print("Generating users...")
    for i in range(N_USERS):
        username = F.user_name()
        ins = User.insert().values(username=username, email=F.email(), password=F.password(), city=F.city(), state=F.state_abbr(), country=F.country_code(), bio=F.text())
        try:
            res = connection.execute(ins)
            uid = res.inserted_primary_key[0]
            USERS.append(uid)
        except Exception as e:
            print(e)
            pass

    # Pull topics
    print("Pulling topics...")
    res = connection.execute(Topic.select())
    for row in res:
        TOPICS.append(row.topic_name)

    # Generate questions
    print("Generating questions...")
    for i in range(N_QUESTIONS):
        ins = Question.insert().values(uid=random.choice(USERS), title=F.sentence(), body=F.text(), topic=random.choice(TOPICS))
        result = connection.execute(ins)
        QUESTIONS.append(result.inserted_primary_key[0])
    
    # Generate answers
    print("Generating answers...")
    for i in range(N_ANSWERS):
        ins = Answer.insert().values(uid=random.choice(USERS), qid=random.choice(QUESTIONS), body=F.text())
        result = connection.execute(ins)
        ANSWERS.append(result.inserted_primary_key[0])

    # Generate question ratings
    print("Generating question ratings...")
    for i in range(N_QUESTION_RATINGS):
        ins = QuestionRating.insert().values(qid=random.choice(QUESTIONS), uid=random.choice(USERS), is_upvote=random.random() < 0.7)
        try:
            result = connection.execute(ins)
        except Exception as e:
            print(e)
            pass

    # Generate answer ratings
    print("Generating answer ratings...")
    for i in range(N_ANSWER_RATINGS):
        ins = AnswerRating.insert().values(aid=random.choice(ANSWERS), uid=random.choice(USERS), is_upvote=random.random() < 0.7)
        try:
            result = connection.execute(ins)
        except Exception as e:
            print(e)
            pass

    # Pin answers
    print("Generating pinned answers...")
    for i in range(N_PINNED_ANSWERS):
        rand_question = random.choice(QUESTIONS)
        query_questions = Answer.select().where(Answer.c.qid == rand_question)
        res = connection.execute(query_questions)
        local_answers = []
        for row in res:
            local_answers.append(row.aid)
        if len(local_answers) == 0:
            continue
        ins = PinnedAnswer.insert().values(qid=rand_question, aid=random.choice(local_answers))
        try:
            result = connection.execute(ins)
        except Exception as e:
            print(e)
            pass
