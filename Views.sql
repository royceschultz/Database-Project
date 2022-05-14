-- Drop all views
DROP VIEW IF EXISTS QuestionScore;
DROP VIEW IF EXISTS AnswerScore;

CREATE VIEW QuestionScore AS
SELECT Question.*, SUM(IF(QuestionRating.is_upvote IS NULL, 1, IF(QuestionRating.is_upvote, 10,-1))) AS score, User.username, COUNT(DISTINCT aid) as n_answers
FROM Question
LEFT JOIN QuestionRating ON Question.qid=QuestionRating.qid
JOIN User on Question.uid=User.uid
LEFT JOIN Answer on Question.qid=Answer.qid
GROUP BY qid;

CREATE VIEW AnswerScore AS
SELECT Answer.*, SUM(IF(AnswerRating.is_upvote IS NULL, 1, IF(AnswerRating.is_upvote, 10,-1))) AS score, SUM(IF(PinnedAnswer.aid IS NULL, 0, 1)) AS is_pinned, Question.title as q_title, User.username
FROM Answer
LEFT JOIN AnswerRating ON Answer.aid=AnswerRating.aid
LEFT JOIN PinnedAnswer ON Answer.aid=PinnedAnswer.aid
JOIN Question on Answer.qid=Question.qid
JOIN User on User.uid = Answer.uid
GROUP BY aid;
