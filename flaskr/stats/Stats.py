from scipy.cluster import hierarchy
import scipy.spatial.distance as ssd
import numpy as np

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
            try:
                category_name = participant['categories'][category_id]['title']
            except KeyError:
                category_name = 'not set'

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
        try:
            category_name = participant['categories'][category_id]['title']
        except KeyError:
            category_name = 'not set'

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
        for card_id in participant['categories'][category_id]['cards']:
            card_name = study['cards'][str(card_id)]['name']

            found = False
            card_no = 0
            try:
                for study_card in study_categories[category_name]['cards']:
                    if card_name == study_card:
                        found = True
                        break
                    card_no += 1
            except KeyError:
                found = False

            if not found:
                studies.update_one({'_id': ObjectId(study_id)}, {'$push': {categories_category + '.cards': card_name}})
                studies.update_one({'_id': ObjectId(study_id)}, {'$push': {categories_category + '.frequencies': 1}})
            else:
                studies.update_one({'_id': ObjectId(study_id)}, {'$inc': {categories_category + '.frequencies.'
                                                                          + str(card_no): 1}})

        studies.update_one({'_id': ObjectId(study_id)}, {'$inc': {categories_category + '.participants': 1}})


def build_similarity_matrix(study_id):
    with current_app.app_context():
        studies = get_db()['studies']

    study = list(studies.find({'_id': ObjectId(study_id)}))[0]

    # Build the padding array
    card_names = []
    times_in_same_category = []
    siblings = 1
    i = 0
    for card in study['cards']:
        card_name = study['cards'][card]['name']
        card_names.append(card_name)
        times_in_same_category.append([])
        for j in range(0, siblings):
            times_in_same_category[i].append(0)
        siblings += 1
        i += 1

    studies.update({'_id': ObjectId(study_id)}, {'$set': {
        'stats.clusters': {},
        'stats.clusters_changed': False,
        'stats.clusters_calculating': False,
        'stats.similarities.card_names': card_names,
        'stats.similarities.times_in_same_category': times_in_same_category,
    }})


def update_similarity_matrix(study_id, new_participant_id):
    with current_app.app_context():
        studies = get_db()['studies']
        participants = get_db()['participants']

    participant = list(participants.find({'_id': ObjectId(new_participant_id)}))[0]
    study = list(studies.find({'_id': ObjectId(study_id)}))[0]

    card_names = study['stats']['similarities']['card_names']
    times_in_same_category = study['stats']['similarities']['times_in_same_category']
    all_cards = study['cards']

    for category_name in participant['categories']:
        category = participant['categories'][category_name]
        cards = category['cards']

        for card_id in cards:
            # Get the name corresponding to the id
            card_name = all_cards[str(card_id)]['name']
            index = card_names.index(str(card_name))

            for card2_id in cards:
                # Get the name corresponding to the id
                card2_name = all_cards[str(card2_id)]['name']
                index2 = card_names.index(str(card2_name))

                # Calculate only the left triangle
                if index < index2:
                    break

                times_in_same_category[index][index2] += 1

    studies.update_one({'_id': ObjectId(study_id)}, {'$set': {
        'stats.similarities.times_in_same_category': times_in_same_category
    }})


def calculate_clusters(study_id):
    """
    Calculates the clusters based on the average-linkage hierarchical clustering.
    The calculation happens only if something has been changed from the previous calculation.
    :param study_id:
    :return: the clusters
    """
    with current_app.app_context():
        studies = get_db()['studies']

    study = list(studies.find({'_id': ObjectId(study_id)}))[0]
    if study['stats']['clusters_changed']:

        if study['stats']['clusters_calculating']:
            return {'message': 'calculating'}

        studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'stats.calculating': True}})
        distance = study['stats']['similarities']['times_in_same_category']
        card_names = study['stats']['similarities']['card_names']
        total_participants = len(study['participants'])

        distance_matrix = calculate_square_form(distance, total_participants)
        distArray = ssd.squareform(distance_matrix)

        try:
            clusters = hierarchy.linkage(distArray, method='average')
        except ValueError:
            return {'message': 'not enough data'}

        tree = hierarchy.to_tree(clusters, rd=False)
        # TODO Distance 0 on root
        dendro = dict(children=[], hierarchy=0, distance=100)

        add_node(tree, dendro, card_names)
        studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'stats.clusters': dendro}})
        studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'stats.calculating': False}})

        studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'stats.clusters_changed': False}})
    else:
        dendro = study['stats']['clusters']

    return dendro


def calculate_square_form(diagonal_matrix, total_sorts):
    """
    Takes a diagonal matrix converts it to it's full form
    :param diagonal_matrix: a diagonal matrix
    :param total_sorts
    :return: the nxn redundant matrix
    """
    n = len(diagonal_matrix)

    matrix = np.ndarray(shape=(n,n))

    for i in range(n):
        for j in range(len(diagonal_matrix[i])):
            # Also calculate the dissimilarity matrix
            matrix[i][j] = 100 - 100 * diagonal_matrix[i][j] / total_sorts
            matrix[j][i] = 100 - 100 * diagonal_matrix[i][j] / total_sorts
            if i == j:
                matrix[i][j] = 0

    return matrix


def add_node(node, parent, card_names):
    """
    Create a nested dictionary from the ClusterNode's returned by SciPy
    :param node:
    :param parent:
    :param card_names
    :return:
    """
    # First create the new node and append it to its parent's children
    new_node = dict(children=[], hierarchy=1, distance=node.dist)
    # Append the name only if the node is a leaf
    if node.id < len(card_names):
        new_node.update(name=card_names[node.id])

    parent['children'].append(new_node)

    for child in parent['children']:
        if child['hierarchy'] >= parent['hierarchy']:
            parent['hierarchy'] = child['hierarchy'] + 1

    # Recursively add the current node's children
    if node.left:
        add_node(node.left, new_node, card_names)
    if node.right:
        add_node(node.right, new_node, card_names)