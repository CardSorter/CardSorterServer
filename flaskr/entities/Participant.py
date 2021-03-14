from flask import current_app
from ..db import conn
import json
# todo create participant weird structure
class Participant:
    def __init__(self):
        self.participant_id = 0
        with current_app.app_context():
            self.cur = conn.cursor()

    def post_categorization(self, study_id, categories, non_sorted, time, comment):
        self.cur.execute("""SELECT COUNT(ID) FROM CARDS WHERE STUDY_ID=%s""", (str(study_id),))
        study_cards = self.cur.fetchone()[0]

        if not study_cards:
            return {'message': 'STUDY NOT FOUND'}

        # Calculate some (very) small statistics
        categories_no = len(categories)
        cards_sorted = 0
        for category in categories:
            cards_sorted += len(categories[category]['cards'])

        # Calculate percentage
        cards_sorted = int((cards_sorted / study_cards) * 100)
        # creates participant and puts him inside
        self.cur.execute("""INSERT INTO PARTICIPANT (NOT_SORTED, CARDS_SORTED, CATEGORIES_NO,
                            TIME_SPAN, COMMENTS, STUDY_ID) VALUES (%s, %s, %s, %s, %s, %s) RETURNING ID""",
                         (len(non_sorted), cards_sorted, categories_no, time, comment, str(study_id),))
        conn.commit()
        self.participant_id = self.cur.fetchone()[0]

        # Increment completed / abandoned
        if cards_sorted == 100:
            self.cur.execute("""UPDATE STUDY SET COMPLETED_NO = COMPLETED_NO + 1 WHERE ID = %s""", (str(study_id),))
        else:
            self.cur.execute("""UPDATE STUDY SET ABANDONED_NO = ABANDONED_NO + 1 WHERE ID = %s""", (str(study_id),))
        conn.commit()

        # Clusters have been changed
        self.cur.execute("""UPDATE STATS SET CLUSTERS_CHANGED = TRUE WHERE STUDY_ID = %s""", (str(study_id),))
        conn.commit()

        # Update frequencies or insert frequency = 1 for new cat-card pair.
        for category in categories:
            t = categories[category]['title']
            c = categories[category]['cards']
            self.cur.execute("""SELECT ID FROM CATEGORIES WHERE CATEGORY_NAME = %s AND STUDY_ID = %s""",
                             (t, str(study_id),))
            _id = self.cur.fetchone()
            if _id:
                _id = _id[0]
                self.cur.execute("""UPDATE CATEGORIES SET FREQUENCY = FREQUENCY + 1 WHERE STUDY_ID = %s AND ID = %s""",
                                 (str(study_id), _id,))
                conn.commit()
            else:
                self.cur.execute("""INSERT INTO CATEGORIES (CATEGORY_NAME, STUDY_ID, FREQUENCY) VALUES (%s, %s, 1) RETURNING ID""",
                                 (t, str(study_id),))
                _id = self.cur.fetchone()[0]
                conn.commit()
            for card_id in c:
                self.cur.execute("""UPDATE CARDS_CATEGORIES SET FREQUENCY = FREQUENCY + 1 WHERE CARD_ID = %s
                                    AND CATEGORY_ID = %s""", (card_id, _id,))
                if self.cur.rowcount == 0:
                    self.cur.execute("""INSERT INTO CARDS_CATEGORIES (FREQUENCY, CARD_ID, CATEGORY_ID) VALUES (1, %s, %s)""",
                                     (card_id, _id,))
                conn.commit()

        # U/update similarity matrix
        self.cur.execute("""SELECT SIMILARITY_MATRIX FROM STATS WHERE STUDY_ID = %s""",
                         (str(study_id),))
        sim_json = self.cur.fetchone()[0]

        card_ids = sim_json['cardId']
        times_in_same_category = sim_json['matrix']
        # Increase frequencies of times in same category based on the categorization of this participant
        for category in categories:
            cards = categories[category]['cards']
            for card_id in cards:
                index = card_ids.index(card_id)
                for card_id2 in cards:
                    index2 = card_ids.index(card_id2)
                    if index < index2:
                        break
                    times_in_same_category[index][index2] += 1

        sim_json['matrix'] = times_in_same_category

        self.cur.execute("""UPDATE STATS SET SIMILARITY_MATRIX = %s WHERE STUDY_ID = %s""", (json.dumps(sim_json), study_id,))
        conn.commit()
