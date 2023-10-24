import datetime

from bson import ObjectId
from flask import current_app
from math import ceil

from flaskr.db import get_db
from flaskr.stats.Stats import build_similarity_matrix, calculate_clusters
from flaskr.Config import Config


class Study:
    def __init__(self):
        with current_app.app_context():
            self.users = get_db()['users']
            self.studies = get_db()['studies']
            self.participants = get_db()['participants']
        self.study_id = 0

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

        # Link study to the user
        self.users.update_one({'_id': ObjectId(user_id)}, {'$push': {'studies': self.study_id}})

    def get_studies(self, user_id):
        study_ids = list(self.users.find({'_id': ObjectId(user_id)}, {'_id': 0, 'studies': 1}))[0]['studies']
        studies = []
        for study_id in study_ids:
            study = list(self.studies.find({'_id': ObjectId(study_id)}, {
                'title': 1,
                'abandonedNo': 1,
                'completedNo': 1,
                'editDate': 1,
                'isLive': 1,
                'launchedDate': 1,
                'endDate': 1}))
            if len(study) > 0:
                study = study[0]
            else:
                print('Study not found:', study_id)
                continue
            study['id'] = str(study['_id'])
            study['_id'] = None
            studies.append(study)
        return studies

    def get_study(self, study_id, user_id):
        # Check if the study belongs to the user
        available_studies = list(self.users.find({'_id': ObjectId(user_id)}, {'_id': 0, 'studies': 1}))[0]['studies']

        if ObjectId(study_id) not in available_studies:
            return {'message': 'INVALID STUDY'}

        study = list(self.studies.find({'_id': ObjectId(study_id)}))[0]
        study['id'] = str(study['_id'])
        study['_id'] = None

        # Make full json structure
        # Calculate participants data

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
                'shareUrl': Config.url + '/sort/' + '?id=' + str(study['id'])
            }

        study['shareUrl'] = Config.url + '/sort/' + '?id=' + str(study['id'])

        study['participants'] = {
            'completion': study['stats']['completion'],
            'total': total,
            'completed': study['completedNo'],
            'data': participants
        }

        # Calculate cards data

        # Make the json array specified
        # data: 0: card_name 1: categories_no 2: categories names 3: frequency
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
            'total': len(categories),
            'similar': 0,
            'merged': 0,
            'data': categories,
        }
        study['similarityMatrix'] = self._convert_similarity_matrix(study)

        print("total participants: ", total)
        participants = []
        no = 1
        for participant_id in study_participants:
            participant = list(self.participants.find({'_id': participant_id}, {'_id': 0}))[0]
            
            # Extract categories and cards for the participant
            comment = participant['comment']
            for category_data in participant['categories'].items():
              
                category_name = category_data[1]['title']
                cards = category_data[1]['cards']

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
        study = list(self.studies.find({'_id': ObjectId(study_id)}, {'_id': 0, 'cards': 1, 'isLive': 1}))

        if len(study) == 0 or not study[0]['isLive']:
            return {'message': 'STUDY NOT FOUND'}
        study = study[0]

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
        # Check if the study belongs to the user
        available_studies = list(self.users.find({'_id': ObjectId(user_id)}, {'_id': 0, 'studies': 1}))[0]['studies']

        if ObjectId(study_id) not in available_studies:
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