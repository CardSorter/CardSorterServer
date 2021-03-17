CREATE TABLE USER_TABLE(
  ID BIGSERIAL NOT NULL,
  USERNAME CHAR(52) NOT NULL,
  PASS CHAR(120) NOT NULL,
  EMAIL CHAR(70) NOT NULL,
  PRIMARY KEY(ID)
);

CREATE TABLE STUDY(
  ID BIGSERIAL NOT NULL,
  USER_ID BIGINT NOT NULL,
  DESCRIPTION CHAR(400) NOT NULL,
  TITLE CHAR(120) NOT NULL,
  COMPLETED_NO INT NOT NULL,
  ABANDONED_NO INT NOT NULL,
  EDIT_DATE TIMESTAMP NOT NULL,
  LAUNCHED_DATE TIMESTAMP NOT NULL,
  END_DATE TIMESTAMP NULL,
  IS_LIVE BOOLEAN NOT NULL,
  MESSAGE_TEXT CHAR(400) NOT NULL, 
  PRIMARY KEY(ID),
  FOREIGN KEY(USER_ID) REFERENCES USER_TABLE(ID) ON DELETE CASCADE
);

CREATE TABLE STATS(
  ID BIGSERIAL NOT NULL,
  STUDY_ID BIGINT NOT NULL,
  AVERAGE_SORT REAL NOT NULL,
  COMPLETION REAL NOT NULL,
  CLUSTERS_CALCULATING BOOLEAN NOT NULL,
  CLUSTERS_CHANGED BOOLEAN NOT NULL,
  CLUSTERS JSON NOT NULL,
  SIMILARITY_MATRIX JSON NOT NULL,
  PRIMARY KEY(ID),
  FOREIGN KEY(STUDY_ID) REFERENCES STUDY(ID) ON DELETE CASCADE
);

CREATE TABLE PARTICIPANT(
  ID BIGSERIAL NOT NULL,
  STUDY_ID BIGINT NOT NULL,
  CARDS_SORTED INT NOT NULL,
  TIME_SPAN INT NOT NULL,
  CATEGORIES_NO INT NOT NULL,
  NOT_SORTED INT NOT NULL,
  COMMENTS CHAR(300) NOT NULL,
  PRIMARY KEY(ID),
  FOREIGN KEY(STUDY_ID) REFERENCES STUDY(ID) ON DELETE CASCADE
);

CREATE TABLE CARDS(
  ID BIGSERIAL NOT NULL,
  STUDY_ID BIGINT NOT NULL,
  CARD_NAME CHAR(30) NOT NULL,
  DESCRIPTION CHAR(100) NOT NULL,
  PRIMARY KEY(ID),
  FOREIGN KEY(STUDY_ID) REFERENCES STUDY(ID) ON DELETE CASCADE
);

CREATE TABLE CATEGORIES(
  ID BIGSERIAL NOT NULL,
  STUDY_ID BIGINT NOT NULL,
  CATEGORY_NAME CHAR(50) NOT NULL,
  FREQUENCY INT NOT NULL,
  PRIMARY KEY(ID),
  FOREIGN KEY(STUDY_ID) REFERENCES STUDY(ID) ON DELETE CASCADE
);

CREATE TABLE CARDS_CATEGORIES(
  CARD_ID BIGINT NOT NULL,
  CATEGORY_ID BIGINT NOT NULL,
  FREQUENCY REAL NOT NULL,
  PRIMARY KEY(CARD_ID, CATEGORY_ID),
  FOREIGN KEY(CARD_ID) REFERENCES CARDS(ID) ON UPDATE CASCADE,
  FOREIGN KEY(CATEGORY_ID) REFERENCES CATEGORIES(ID) ON UPDATE CASCADE
)