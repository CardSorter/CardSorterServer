import datetime

from bson import ObjectId
from flask import current_app
from math import ceil

from flaskr.db import get_db
from flaskr.stats.Stats import build_similarity_matrix, calculate_clusters
from flaskr.Config import Config
from ..db import conn

class Study:
    def __init__(self):
        with current_app.app_context():
            self.users = get_db()['users']
            self.studies = get_db()['studies']
            self.participants = get_db()['participants']
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
        self.study_id = self.cur.fetchone()[0]
        for ca in sanitized_cards:
            self.cur.execute("""INSERT INTO CARDS (STUDY_ID, CARD_NAME, DESCRIPTION) VALUES (%s, %s ,%s)""",
                             (self.study_id, sanitized_cards[ca]["name"], sanitized_cards[ca]["description"]))
        conn.commit()

        # Create the appropriate fields
        build_similarity_matrix(str(self.study_id))


    def get_studies(self, user_id):
        self.cur.execute("""SELECT ID, TITLE, ABANDONED_NO, COMPLETED_NO, EDIT_DATE, IS_LIVE, LAUNCHED_DATE, END_DATE
                            FROM STUDY WHERE USER_ID=%s""", (str(user_id),))
        studies = self.cur.fetchall()
        return studies

    def get_study(self, study_id, user_id):
        self.cur.execute("""SELECT * FROM STUDY WHERE USER_ID=%s AND ID=%s""", (str(user_id), str(study_id),))
        study = self.cur.fetchone()
        full_json = {}
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

        # # Check if the study belongs to the user
        # available_studies = list(self.users.find({'_id': ObjectId(user_id)}, {'_id': 0, 'studies': 1}))[0]['studies']
        #
        # if ObjectId(study_id) not in available_studies:
        #     return {'message': 'INVALID STUDY'}
        #
        # study = list(self.studies.find({'_id': ObjectId(study_id)}))[0]
        # study['id'] = str(study['_id'])
        # study['_id'] = None

        # Make full json structure
        # Calculate participants data

        # Make the json array specified
        # data: 0: participant_no id 1: time taken 2: cards sorted 3: categories created
        self.cur.execute("""SELECT * FROM PARTICIPANT WHERE STUDY_ID=%s""", (str(study_id),))
        unfiltered_participants = self.cur.fetchall()
        no = 1
        participants = []
        for participant in unfiltered_participants:
            time = participant[3]
            cards_sorted = participant[2]
            categories_no = participant[4]
            participants.append(['#' + str(no), time, str(cards_sorted) + '%', categories_no])
            no += 1
        total = len(participants)

        # participants = []
        # no = 1
        # try:
        #     for participant_id in study['participants']:
        #         participant = list(self.participants.find({'_id': participant_id},
        #                                                   {'_id': 0}))[0]
        #         try:
        #             time = participant['time']
        #         except KeyError:
        #             time = 'N/A'
        #
        #         participants.append(['#' + str(no), time, str(participant['cards_sorted']) + '%'
        #                             , participant['categories_no']])
        #         no += 1
        # except KeyError:
        #     return {
        #         'title': study['title'],
        #         'isLive': study['isLive'],
        #         'launchedDate': study['launchedDate'],
        #         'participants': 0,
        #         'shareUrl': Config.url + '/sort/' + '?id=' + str(study['id'])
        #     }
        # total = len(study['participants'])

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
        stats = self.cur.fetchone()

        full_json['participants'] = {
            'completion': stats[3],
            'total': total,
            'completed': study[4],
            'data': participants
        }

        # Calculate cards data

        # Make the json array specified
        # data: 0: card_name 1: categories_no 2: categories names 3: frequency
        self.cur.execute("""SELECT C.ID, C.CARD_NAME, CA.ID, CA.CATEGORY_NAME, K.FREQUENCY
                            FROM CARDS C LEFT JOIN CARDS_CATEGORIES K ON C.ID = K.CARD_ID
                            LEFT JOIN CATEGORIES CA ON K.CATEGORY_ID = CA.ID
                            WHERE C.STUDY_ID=%s""", (str(study_id),))
        cards_cats = self.cur.fetchall()
        self.cur.execute("""SELECT C.ID, C.CARD_NAME, COUNT(CA.ID)
                            FROM CARDS C LEFT JOIN CARDS_CATEGORIES K ON C.ID = K.CARD_ID
                            LEFT JOIN CATEGORIES CA ON K.CATEGORY_ID = CA.ID
                            WHERE C.STUDY_ID=%s
                            GROUP BY C.ID""", (str(study_id),))
        cats_no = self.cur.fetchone()[0]
        print(cards_cats, cats_no)

        cards = []
        for card_id in study['cards']:
            card = study['cards'][card_id]
            try:
                categories = study['cards'][card_id]['categories']
            except KeyError:
                categories = []
            try:
                frequencies = study['cards'][card_id]['frequencies']
            except KeyError:
                frequencies = []
            categories_no = len(categories)
            cards.append([card['name'], categories_no, categories, frequencies])

        study['cards'] = {
            'average': str(study['stats']['average_sort']) + '%',
            'total': len(study['cards']),
            'sorted': int(total * study['stats']['average_sort'] * (1 / 100)),
            'data': cards,
        }

        # Calculate categories data

        # Make the json array specified
        # data: 0: category name 1: cards no 2: cards 3: frequency 4: participants
        categories = []
        for category_name in study['categories']:
            category = study['categories'][category_name]
            categories.append([category_name, len(category['cards']), category['cards'],
                               category['frequencies'], category['participants']])

        study['categories'] = {
            'similarity': '0%',
            'total': len(categories),
            'similar': 0,
            'merged': 0,
            'data': categories,
        }
        study['similarityMatrix'] = self._convert_similarity_matrix(study)

        return study

    @staticmethod
    def _convert_similarity_matrix(study):
        """
        Converts the times each card was found in the same category to the actual percentage.
        This also includes the times that a card was not sorted. Meaning that a card can be sorted with it's self
        less than 100%.
        :param study: the study document
        :return: the similarity matrix
        """
        total_sorts = len(study['participants']['data'])
        card_names = study['stats']['similarities']['card_names']
        similarity_matrix = []
        no = 0
        for line in study['stats']['similarities']['times_in_same_category']:
            for i in range(0, len(line) - 1):
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
        study = self.cur.fetchall()
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
        message = list(self.studies.find({'_id': ObjectId(study_id)}, {'_id': 0, 'message': 1}))[0]
        return message

    def get_clusters(self, study_id, user_id):
        # Check if the study belongs to the user
        available_studies = list(self.users.find({'_id': ObjectId(user_id)}, {'_id': 0, 'studies': 1}))[0]['studies']

        if ObjectId(study_id) not in available_studies:
            return {'message': 'INVALID STUDY'}

        return calculate_clusters(study_id)
