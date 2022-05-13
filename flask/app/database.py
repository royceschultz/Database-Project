from sqlalchemy import create_engine, MetaData, Table

engine = create_engine('mysql+pymysql://root:example@db:3306/QueueOverflow')
metadata = MetaData()
User = Table('User', metadata, autoload=True, autoload_with=engine)
UserSession = Table('UserSession', metadata, autoload=True, autoload_with=engine)
Topic = Table('Topic', metadata, autoload=True, autoload_with=engine)
Question = Table('Question', metadata, autoload=True, autoload_with=engine)
Answer = Table('Answer', metadata, autoload=True, autoload_with=engine)
PinnedAnswer = Table('PinnedAnswer', metadata, autoload=True, autoload_with=engine)
QuestionRating = Table('QuestionRating', metadata, autoload=True, autoload_with=engine)
AnswerRating = Table('AnswerRating', metadata, autoload=True, autoload_with=engine)

# Views
QuestionScore = Table('QuestionScore', metadata, autoload=True, autoload_with=engine)
AnswerScore = Table('AnswerScore', metadata, autoload=True, autoload_with=engine)

def Connect():
    return engine.connect()
