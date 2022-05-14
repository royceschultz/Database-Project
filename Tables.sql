DROP TABLE IF EXISTS AnswerRating;
DROP TABLE IF EXISTS QuestionRating;
DROP TABLE IF EXISTS PinnedAnswer;
DROP TABLE IF EXISTS Answer;
DROP TABLE IF EXISTS Question;
DROP TABLE IF EXISTS Topic;
DROP TABLE IF EXISTS UserSession;
DROP TABLE IF EXISTS User;


CREATE TABLE User (
    uid INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username varchar(64),
    password varchar(256) NOT NULL,
    email varchar(256) NOT NULL,
    city varchar(256),
    state varchar(256),
    country varchar(256),
    bio text,
    dt_created datetime DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE UserSession (
    uid int NOT NULL,
    session_id varchar(256) NOT NULL,
    dt_created datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (uid, session_id),
    FOREIGN KEY (uid) REFERENCES User(uid)
        ON DELETE CASCADE
);

CREATE TABLE Topic (
    topic_name varchar(64) PRIMARY KEY,
    parent_topic varchar(64),
    FOREIGN KEY (parent_topic) REFERENCES Topic(topic_name)
);

Create TABLE Question (
	qid int AUTO_INCREMENT PRIMARY KEY,
    uid int,
    title varchar(256) NOT NULL,
    body text NOT NULL,
    topic varchar(64) NOT NULL,
    dt_created datetime DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (uid, title),
    UNIQUE (title, topic),
    
    FOREIGN KEY (uid) REFERENCES User(uid)
        ON DELETE SET NULL, -- Allow questions to remain even if the author is deleted
    FOREIGN KEY (topic) REFERENCES Topic(topic_name)
);

Create TABLE Answer (
    aid int AUTO_INCREMENT PRIMARY KEY,
	qid int NOT NULL,
    uid int,
    body text NOT NULL,
    dt_created datetime DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (qid)
        REFERENCES Question(qid)
        ON DELETE CASCADE,
    FOREIGN KEY (uid)
        REFERENCES User(uid)
        ON DELETE SET NULL -- Allow answers to remain even if the author is deleted
);

CREATE TABLE PinnedAnswer (
    qid int NOT NULL,
    aid int NOT NULL,
    PRIMARY KEY (qid), -- Each question can have 0 or 1 pinned answers
    FOREIGN KEY (qid)
        REFERENCES Question(qid)
        ON DELETE CASCADE,
    FOREIGN KEY (aid)
        REFERENCES Answer(aid)
        ON DELETE CASCADE
);


CREATE TABLE QuestionRating (
	qid int,
    uid int,
    is_upvote bool, -- True if upvote, False if downvote, NOT EXIST if no vote

    PRIMARY KEY(qid, uid), -- Uniqueness enforces 1:1 relationship
    FOREIGN KEY(qid)
        REFERENCES Question(qid)
        ON DELETE CASCADE,
    FOREIGN KEY (uid)
        REFERENCES User(uid)
        ON DELETE CASCADE
);

CREATE TABLE AnswerRating (
    aid int,
    uid int,
    is_upvote bool,

    PRIMARY KEY(aid, uid),
    FOREIGN KEY (aid)
        REFERENCES Answer(aid)
        ON DELETE CASCADE,
    FOREIGN KEY (uid)
        REFERENCES User(uid)
        ON DELETE CASCADE
);


INSERT INTO Topic(topic_name) VALUES
('Programming'), ('Misc');

INSERT INTO Topic(topic_name, parent_topic) VALUES
('Python', 'programming'), ('Javascript', 'programming'), ('SQL', 'programming');
