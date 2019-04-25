from datetime import datetime

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
    sort_percentages = 0
    for participant_id in study['participants']:
        participant = list(participants.find({'_id': ObjectId(participant_id)}))[0]
        if participant['cards_sorted'] == 100:
            completed += 1
        sort_percentages += participant['cards_sorted']

    completion = str(int(completed / total * 100)) + '%'
    studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'stats.completion': completion}})

    # Calculate average sort
    average_sort = int(sort_percentages/total)
    studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'stats.average_sort': average_sort}})


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


def update_categories_stats(study_id, new_participant_id):
    """
    Updates the statistic for the categories.
    !Important: this method should be called after the updated card stats.
    :return:
    """
    with current_app.app_context():
        studies = get_db()['studies']
        participants = get_db()['participants']

    participant = list(participants.find({'_id': ObjectId(new_participant_id)}))[0]
    study = list(studies.find({'_id': ObjectId(study_id)}))[0]
    for category_id in participant['categories']:
        category_name = participant['categories'][category_id]['title']

        try:
            study_categories = list(studies.find({'_id': ObjectId(study_id)}, {'categories': 1}))[0]['categories']
        except KeyError:
            studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'categories': {}}})
            study_categories = {}

        # Create different not set categories
        if category_name == 'not set':
            unique = False
            i = 0
            while not unique:
                name = 'not set #' + str(i)
                if name not in study_categories:
                    category_name = name
                    unique = True
                i += 1

        categories_category = 'categories.' + str(category_name)
        print('Category name:', categories_category)
        for card_id in participant['categories'][category_id]['cards']:
            card_name = study['cards'][str(card_id)]['name']
            try:
                found = False
                card_no = 0
                for study_card in study_categories[category_name]['cards']:
                    print('Card name:', card_name)
                    print('Matching card:', card_name)
                    if card_name == study_card:
                        print('MATCH')
                        found = True
                        break
                    card_no += 1
            except KeyError:
                print('Not found key:', card_name)
                found = False

            if not found:
                studies.update_one({'_id': ObjectId(study_id)}, {'$push': {categories_category + '.cards': card_name}})
                studies.update_one({'_id': ObjectId(study_id)}, {'$push': {categories_category + '.frequencies': 1}})
                print('Added')
            else:
                studies.update_one({'_id': ObjectId(study_id)}, {'$inc': {categories_category + '.frequencies.'
                                                                          + str(card_no): 1}})
                print('Incremented')

        studies.update_one({'_id': ObjectId(study_id)}, {'$inc': {categories_category + '.participants': 1}})
