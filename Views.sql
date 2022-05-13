-- Drop all views
DROP VIEW IF EXISTS QuestionScore;
DROP VIEW IF EXISTS AnswerScore;

CREATE VIEW QuestionScore AS
SELECT Question.*, SUM(IF(QuestionRating.is_upvote IS NULL, 1, IF(QuestionRating.is_upvote, 10,-1))) AS score
FROM Question
LEFT JOIN QuestionRating ON Question.qid=QuestionRating.question
GROUP BY qid;

CREATE VIEW AnswerScore AS
SELECT Answer.*, SUM(IF(AnswerRating.is_upvote IS NULL, 1, IF(AnswerRating.is_upvote, 10,-1))) AS score, SUM(IF(PinnedAnswer.answer IS NULL, 0, 1)) AS is_pinned
FROM Answer
LEFT JOIN AnswerRating ON Answer.aid=AnswerRating.answer
LEFT JOIN PinnedAnswer ON Answer.aid=PinnedAnswer.answer
GROUP BY aid;
