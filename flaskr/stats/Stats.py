from bson import ObjectId
from flask import current_app
from pymongo.errors import WriteError

from flaskr.db import get_db


def update_stats(study_id):
    with current_app.app_context():
        studies = get_db()['studies']
        participants = get_db()['participants']

    study = list(studies.find({'_id': ObjectId(study_id)}))[0]
    # Calculate completion
    total = len(study['participants'])
    completed = 0
    for participant_id in study['participants']:
        participant = list(participants.find({'_id': ObjectId(participant_id)}))[0]
        if participant['cards_sorted'] == '100%':
            completed += 1

    completion = str(int(completed / total * 100)) + '%'
    studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'stats.completion': completion}})


def update_card_stats(study_id, new_participant_id):
    with current_app.app_context():
        studies = get_db()['studies']
        participants = get_db()['participants']

    study = list(studies.find({'_id': ObjectId(study_id)}))[0]
    participant = list(participants.find({'_id': ObjectId(new_participant_id)}))[0]

    for category_id in participant['categories']:
        for card_id in participant['categories'][category_id]['cards']:
            # Check if the category has a frequencies array
            try:
                study['cards'][str(card_id)]['frequencies']
            except KeyError:
                studies.update_one({'_id': ObjectId(study_id)},
                                   {'$set': {'cards.' + str(card_id) + '.frequencies': []}})

            # Check if the category already exists
            category_name = participant['categories'][category_id]['title']
            try:
                categories = study['cards'][str(card_id)]['categories']
            except KeyError:
                categories = {}

            category_no = 0
            found = False
            for category in categories:
                if category == category_name:
                    found = True
                    break
                category_no += 1

            if not found:
                studies.update_one({'_id': ObjectId(study_id)}, {'$push': {'cards.' + str(card_id) + '.categories':
                                                                           category_name}})

            try:
                studies.update_one({'_id': ObjectId(study_id)}, {'$inc': {'cards.' + str(card_id) + '.frequencies.' +
                                                                          str(category_no): 1}})
            except WriteError:
                studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'cards.' + str(card_id) + '.frequencies.' +
                                                                          str(category_no): 1}})
