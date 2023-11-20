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


    def create_study(self, title, description, cards, message, link, user_id):
        date = datetime.datetime.utcnow()

        # Remove undefined cards
        sanitized_cards = cards.copy()
        for card_id in cards:
            try:
                cards[card_id]['name']
            except KeyError:
                sanitized_cards.pop(card_id, None)

        study = {
            'title': title,
            'description': description,
            'cards': sanitized_cards,
            'message': message,
            'link':link,
            'abandonedNo': 0,
            'completedNo': 0,
            'editDate': date,
            'isLive': True,
            'launchedDate': date,
            'participants': [],
        }
        self._post_study(study)

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

        study_participants = study['participants']
        
        participants = []
        no = 1
        try:
            for participant_id in study['participants']:
                participant = list(self.participants.find({'_id': participant_id},
                                                          {'_id': 0}))[0]
                try:
                    time = participant['time']
                except KeyError:
                    time = 'N/A'

                participants.append(['#' + str(no), time, str(participant['cards_sorted']) + '%'
                                    , participant['categories_no']])
                no += 1
        except KeyError:
            return {
                'title': study['title'],
                'isLive': study['isLive'],
                'launchedDate': study['launchedDate'],
                'participants': 0,
                'shareUrl': Config.url + '/sort/' + '?id=' + str(study['id'])
            }

        total = len(study['participants'])
        # Return no participants json
        if total == 0:
            return {
                'title': study['title'],
                'description': study['description'],
                'isLive': study['isLive'],
                'launchedDate': study['launchedDate'],
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

        # Calculate cards data

        # Make the json array specified
        # data: 0: card_name 1: categories_no 2: categories names 3: frequency
        cards = []
        study_cards = study['cards']
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
            try:
                description = study['cards'][card_id]['description']
            except KeyError:
                description = []
            categories_no = len(categories)
            cards.append([card['name'], categories_no, categories, frequencies,description])

        study['cards'] = {
            'average': str(study['stats']['average_sort']) + '%',
            'total': len(study['cards']),
            'sorted': int(total * study['stats']['average_sort'] * (1 / 100)),
            'data': cards,
        }

        # Calculate categories data

        # Make the json array specified
        # data: 0: category name 1: cards no 2: cards 3: frequency 4: participants
        
        study_categories = study['categories']
        categories = []
       
        for category_name in study['categories']:
            category = study['categories'][category_name]
            categories.append([category_name, len(category['cards']), category['cards'],
                               category['frequencies'], category['participants']])

        study['categories'] = {

            'similarity': '0%',
            'total': int(tot),
            'similar': 0,
            'merged': 0,
            'data': cats,
        }

        print("total participants: ", total)
        participants = []
        no = 1
        for participant_id in study_participants:
            participant = list(self.participants.find({'_id': participant_id}, {'_id': 0}))[0]
            
            # Extract categories and cards for the participant
            comment = participant['comment']
            for category_data in participant['categories'].items():
              
                category_name = category_data[1]['title']
                cardsid = category_data[1]['cards']
                cards = []
                for id in cardsid:
                   cards.append(study_cards[str(id)]['name'])
                participant_data = {
                    'no': f'#{no}',
                    'category': category_name,
                    'cards': cards,
                    'comment': comment,
                }
                comment = ''
                participants.append(participant_data)

            no += 1

        # Assign the 'participants' array to your 'study' object
        study['sorting'] = {
            'data': participants,
        }
        return study

    def get_title_description(self, study_id):
        study = list(self.studies.find({'_id': ObjectId(study_id)}))[0]
        return {
            'title': study['title'],
            'description': study['description'],
        }
    
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

        if len(study) == 0 or not study[0][0]:
            return {'message': 'STUDY NOT FOUND'}

        cards = []
        for card in study['cards'].values():
            cards.append(card)
        return cards
    
    def get_thanks_message_and_link(self, study_id):

        return     list(self.studies.find({'_id': ObjectId(study_id)}, {'_id': 0, 'message': 1}))[0],list(self.studies.find({'_id': ObjectId(study_id)}, {'_id': 0, 'link': 1}))[0]



    # def get_link(self, study_id):
    #     link = list(self.studies.find({'_id': ObjectId(study_id)}, {'_id': 0, 'link': 1}))[0]
    #     return link
    
    def get_clusters(self, study_id, user_id):
        self.cur.execute("""SELECT TITLE FROM STUDY WHERE ID=%s AND USER_ID=%s""", (str(study_id), str(user_id)))
        if not fetchoneClean(self.cur):
            return {'message': 'INVALID STUDY'}
        return calculate_clusters(study_id)

    def _post_study(self, study):
        item = self.studies.insert_one(study)
        self.study_id = ObjectId(item.inserted_id)

    def update_study(self, study_id,editDate,endDate=None, title=None, is_live=None,description=None):
            """
            Update a study's title or isLive status.
            :param study_id: ID of the study to update
            :param title: New title (optional)
            :param is_live: New isLive status (optional)
            """
            update_data = {}
            
            if title is not None:
                update_data['title'] = title
            
            if is_live is not None:
                update_data['isLive'] = is_live
            if description is not None:
                update_data['description'] = description

            if update_data:  
                result = self.studies.update_one({'_id': ObjectId(study_id)},{'$set': {'endDate': endDate,'editDate':editDate,**update_data}})
                
                if result.modified_count > 0:
                    return True
            
            return False
    def delete_study(self, study_id):
        """
        Delete a study from the database.
        :param study_id: ID of the study to delete
        :return: True if deleted successfully, False otherwise
        """
        # First, delete the study from the studies collection
        result = self.studies.delete_one({'_id': ObjectId(study_id)})
        if result.deleted_count > 0:
            # Remove the study from users' study lists
            self.users.update_many({}, {'$pull': {'studies': ObjectId(study_id)}})
            return True
        
        return False 

