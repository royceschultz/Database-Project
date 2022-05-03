DROP TABLE IF EXISTS AnswerRating;
DROP TABLE IF EXISTS QuestionRating;
DROP TABLE IF EXISTS PinnedAnswer;
DROP TABLE IF EXISTS Answer;
DROP TABLE IF EXISTS Question;
DROP TABLE IF EXISTS Topic;
DROP TABLE IF EXISTS UserSession;
DROP TABLE IF EXISTS User;


CREATE TABLE User (
    username varchar(64) PRIMARY KEY,
    password varchar(256) NOT NULL,
    email varchar(256) NOT NULL,
    city varchar(256),
    state varchar(256),
    country varchar(256),
    bio text,
    dt_created datetime DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE UserSession (
    username varchar(64) PRIMARY KEY,
    session_id varchar(256) NOT NULL,
    dt_created datetime DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Topic (
    topic_name varchar(64) PRIMARY KEY,
    parent_topic varchar(64),
    FOREIGN KEY (parent_topic) REFERENCES Topic(topic_name)
);

Create TABLE Question (
	qid int AUTO_INCREMENT PRIMARY KEY,
    username varchar(64),
    title varchar(256) NOT NULL,
    body text NOT NULL,
    topic varchar(64) NOT NULL,
    dt_created datetime DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (username, title),
    UNIQUE (title, topic),
    
    FOREIGN KEY (username) REFERENCES User(username)
        ON DELETE SET NULL, -- Allow questions to remain even if the author is deleted
    FOREIGN KEY (topic) REFERENCES Topic(topic_name)
);

Create TABLE Answer (
    aid int AUTO_INCREMENT PRIMARY KEY,
	question int NOT NULL,
    username varchar(64),
    body text NOT NULL,
    dt_created datetime DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question)
        REFERENCES Question(qid)
        ON DELETE CASCADE,
    FOREIGN KEY (username)
        REFERENCES User(username)
        ON DELETE SET NULL -- Allow answers to remain even if the author is deleted
);

CREATE TABLE PinnedAnswer (
    question int NOT NULL,
    answer int NOT NULL,
    PRIMARY KEY (question), -- Each question can have 0 or 1 pinned answers
    FOREIGN KEY (question)
        REFERENCES Question(qid)
        ON DELETE CASCADE,
    FOREIGN KEY (answer)
        REFERENCES Answer(aid)
        ON DELETE CASCADE
);


CREATE TABLE QuestionRating (
	question int,
    username varchar(64),
    is_upvote bool, -- True if upvote, False if downvote, NOT EXIST if no vote

    PRIMARY KEY(question, username), -- Uniqueness enforces 1:1 relationship
    FOREIGN KEY(question)
        REFERENCES Question(qid)
        ON DELETE CASCADE,
    FOREIGN KEY (username)
        REFERENCES User(username)
        ON DELETE CASCADE
);

CREATE TABLE AnswerRating (
    answer int,
    username varchar(64),
    is_upvote bool,

    PRIMARY KEY(answer, username),
    FOREIGN KEY (answer)
        REFERENCES Answer(aid)
        ON DELETE CASCADE,
    FOREIGN KEY (username)
        REFERENCES User(username)
        ON DELETE CASCADE
);


INSERT INTO Topic(topic_name) VALUES
('Programming'), ('Misc');

INSERT INTO Topic(topic_name, parent_topic) VALUES
('Python', 'programming'), ('Javascript', 'programming'), ('SQL', 'programming');
