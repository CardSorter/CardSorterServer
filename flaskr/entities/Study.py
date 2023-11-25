import datetime

from flask import current_app
from math import ceil

from flaskr.stats.Stats import build_similarity_matrix, calculate_clusters
from flaskr.Config import Config
from ..db import conn
from pandas import DataFrame
from numpy import ndarray
from ..general import *

class Study:
    def __init__(self):
        self.study_id = 0
        with current_app.app_context():
            self.cur = conn.cursor()

    def create_study(self, title, description, cards, message, user_id):
        """
        :param title:
        :param description:
        :param cards: [{"name": str,
                        "id": int,
                        "description": str}]
        :param message:
        :param user_id:
        :return:
        """
        if not isinstance(cards, dict):
            return "Cards is not an array"

        date = datetime.datetime.utcnow()

        # Remove undefined cards
        sanitized_cards = cards.copy()
        for card_id in cards:
            try:
                cards[card_id]['name']
            except KeyError:
                sanitized_cards.pop(card_id, None)


        self.cur.execute("""INSERT INTO STUDY (TITLE, DESCRIPTION, MESSAGE_TEXT, ABANDONED_NO,
                            COMPLETED_NO, EDIT_DATE, IS_LIVE, LAUNCHED_DATE, USER_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id;""",
                         (title, description, message, 0, 0, date, True, date, user_id))
        self.study_id = fetchoneClean(self.cur)[0]
        for ca in sanitized_cards:
            self.cur.execute("""INSERT INTO CARDS (STUDY_ID, CARD_NAME, DESCRIPTION) VALUES (%s, %s ,%s)""",
                             (self.study_id, sanitized_cards[ca]["name"], sanitized_cards[ca]["description"]))
        conn.commit()

        # Create the appropriate fields
        build_similarity_matrix(str(self.study_id))


    def get_studies(self, user_id):
        self.cur.execute("""SELECT ID, TITLE, ABANDONED_NO, COMPLETED_NO, EDIT_DATE, IS_LIVE, LAUNCHED_DATE, END_DATE
                            FROM STUDY WHERE USER_ID=%s""", (str(user_id),))
        studies = fetchallClean(self.cur)
        return studies

    def get_study(self, study_id, user_id):
        self.cur.execute("""SELECT * FROM STUDY WHERE USER_ID=%s AND ID=%s""", (str(user_id), str(study_id),))
        study = [i.strip() if isinstance(i, str) else i for i in fetchoneClean(self.cur)]
        if not study:
            return {'message': 'INVALID STUDY'}

        full_json = {
            "id": study[0],
            "title": study[2],
            "completed_no": study[3],
            "abandoned_no": study[4],
            "edit_date": study[5],
            "launched_date": study[6],
            "end_date": study[7],
            "is_live": study[8],
            "message_text": study[9]
        }
        # Make the json array specified
        # data: 0: participant_no id 1: time taken 2: cards sorted 3: categories created
        self.cur.execute("""SELECT * FROM PARTICIPANT WHERE STUDY_ID=%s""", (str(study_id),))
        unfiltered_participants = fetchallClean(self.cur)
        no = 1
        participants = []
        for participant in unfiltered_participants:
            time = participant[3]
            cards_sorted = participant[2]
            categories_no = participant[4]
            participants.append(['#' + str(no), time, str(cards_sorted) + '%', categories_no])
            no += 1
        total = len(participants)

        # Return no participants json
        if total == 0:
            return {
                'title': study[3],
                'isLive': study[9],
                'launchedDate': study[7],
                'participants': 0,
                'shareUrl': Config.url + '/sort/' + '?id=' + str(study_id)
            }

        full_json['shareUrl'] = Config.url + '/sort/' + '?id=' + str(study_id)

        self.cur.execute("""SELECT * FROM STATS WHERE STUDY_ID=%s""", (str(study_id),))
        stats = fetchoneClean(self.cur)

        full_json['participants'] = {
            'completion': stats[3],
            'total': total,
            'completed': study[4],
            'data': participants
        }

        self.cur.execute("""SELECT DISTINCT C.CARD_NAME, CATS.CATEGORY_NAME, CC.FREQUENCY
                            FROM CARDS C
                            LEFT JOIN CARDS_CATEGORIES CC
                            ON C.ID = CC.CARD_ID
                            LEFT JOIN CATEGORIES CATS
                            ON CATS.ID = CC.CATEGORY_ID
                            WHERE C.STUDY_ID = %s""", (str(study_id),))

        strippedFetchall = fetchallClean(self.cur)
        cont = DataFrame(strippedFetchall, columns=['card_name', 'cat_name', 'freq'])
        cards = cont.groupby(['card_name']).agg({'cat_name': ['count', list], 'freq': list}).reset_index().values.tolist()

        self.cur.execute("""SELECT AVERAGE_SORT FROM STATS WHERE STUDY_ID=%s""", (str(study_id),))
        average_sort = fetchoneClean(self.cur)[0]
        self.cur.execute("""SELECT COUNT(ID) FROM CARDS WHERE STUDY_ID=%s""", (str(study_id),))
        lencards = fetchoneClean(self.cur)[0]
        full_json['cards'] = {
            'average': str(average_sort) + '%',
            'total': lencards,
            'sorted': int(total * average_sort * (1 / 100)),
            'data': cards
        }

        # Calculate categories data
        self.cur.execute("""SELECT DISTINCT CATS.CATEGORY_NAME, CATS.FREQUENCY, CAR.CARD_NAME, CC.FREQUENCY
                            FROM CATEGORIES CATS
                            LEFT JOIN CARDS_CATEGORIES CC
                            ON CATS.ID = CC.CATEGORY_ID
                            LEFT JOIN CARDS CAR
                            ON CAR.ID = CC.CARD_ID
                            WHERE CATS.STUDY_ID = %s""", (str(study_id),))
        cont = DataFrame(fetchallClean(self.cur), columns=['cat_name', 'cat_freq', 'card_name', 'card_freq'])
        cats = cont.groupby(['cat_name', 'cat_freq']).agg({'card_name': ['nunique', 'unique'], 'card_freq': list}).reset_index()
        tot = cats.cat_name.agg('nunique')
        # reorder
        cats.columns = [' '.join(col).strip() for col in cats.columns.values]
        cats = cats[['cat_name', 'card_name nunique', 'card_name unique', 'cat_freq', 'card_freq list']]
        # some things get returned as numpy ndarrays so the code below changes ndarrays to lists
        cats = [[i.tolist() if isinstance(i, ndarray) else i for i in j] for j in cats.values.tolist()]


        full_json['categories'] = {
            'similarity': '0%',
            'total': int(tot),
            'similar': 0,
            'merged': 0,
            'data': cats,
        }

        full_json['similarityMatrix'] = self._convert_similarity_matrix(study_id, self.cur)

        return full_json

    @staticmethod
    def _convert_similarity_matrix(study_id, curr):
        """
        Converts the times each card was found in the same category to the actual percentage.
        This also includes the times that a card was not sorted. Meaning that a card can be sorted with it's self
        less than 100%.
        :param study_id: the study id
        :param curr: conn.cur() of psycopg2
        :return: the similarity matrix
        """
        curr.execute("""SELECT SIMILARITY_MATRIX FROM STATS WHERE STUDY_ID=%s""", (str(study_id),))
        sm = fetchoneClean(curr)[0]
        matrix = sm['matrix']
        card_names = sm['cardNames']
        curr.execute("""SELECT COUNT(ID) FROM PARTICIPANT WHERE STUDY_ID=%s""", (str(study_id),))
        total_sorts = fetchoneClean(curr)[0]

        similarity_matrix = []
        no = 0
        for line in matrix:
            for i in range(len(line) - 1):
                line[i] = ceil((line[i]/total_sorts) * 100)

            line[len(line) - 1] = card_names[no]
            similarity_matrix.append(line)
            no += 1
        return similarity_matrix

    def get_cards(self, study_id):
        self.cur.execute("""SELECT IS_LIVE, CARD_NAME, C.DESCRIPTION, C.ID
                             FROM STUDY S
                             LEFT JOIN CARDS C
                             ON S.ID = C.STUDY_ID
                             WHERE S.ID=%s""", (str(study_id),))
        study = fetchallClean(self.cur)
        print(study)

        if len(study) == 0 or not study[0][0]:
            return {'message': 'STUDY NOT FOUND'}

        lod = []
        for i in range(len(study)):
            lod.append({
                    'name': study[i][1].strip(),
                    'description': study[i][2].strip(),
                    'id': study[i][3],
            })
        return lod

    def get_thanks_message(self, study_id):
        self.cur.execute("""SELECT MESSAGE_TEXT FROM STUDY WHERE ID=%s""", (str(study_id),))
        message = fetchoneClean(self.cur)
        return message

    def get_clusters(self, study_id, user_id):
        self.cur.execute("""SELECT TITLE FROM STUDY WHERE ID=%s AND USER_ID=%s""", (str(study_id), str(user_id)))
        if not fetchoneClean(self.cur):
            return {'message': 'INVALID STUDY'}
        return calculate_clusters(study_id)
