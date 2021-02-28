from scipy.cluster import hierarchy
import scipy.spatial.distance as ssd
import numpy as np

from bson import ObjectId
from flask import current_app
from pymongo.errors import WriteError

from flaskr.db import get_db
from ..db import conn
import json

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


def build_similarity_matrix(study_id):
    with current_app.app_context():
        cur = conn.cursor()

    cur.execute("""SELECT CARD_NAME, ID FROM CARDS WHERE STUDY_ID = %s""", (study_id,))
    _ = cur.fetchall()
    card_names = [i[0].strip() for i in _]
    card_ids = [i[1] for i in _]

    # Build the padding array
    times_in_same_category = []
    siblings = 1
    i = 0

    for c in range(len(card_names)):
        times_in_same_category.append([])
        for j in range(siblings):
            times_in_same_category[i].append(0)
        siblings += 1
        i += 1

    similarmat = {'matrix': times_in_same_category, 'cardNames': card_names, 'cardId': card_ids}
    cur.execute("""INSERT INTO STATS (STUDY_ID, AVERAGE_SORT, COMPLETION, CLUSTERS_CALCULATING, CLUSTERS_CHANGED,
                                      CLUSTERS, SIMILARITY_MATRIX) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (study_id, 0, 0, False, False, json.dumps({}), json.dumps(similarmat)))
    conn.commit()



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

    # matrix = np.tril(diagonal_matrix, k=-1)
    # matrix = matrix + matrix.T
    # matrix = matrix * (-100 / total_sorts) + 100
    # np.fill_diagonal(matrix, 0)

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
