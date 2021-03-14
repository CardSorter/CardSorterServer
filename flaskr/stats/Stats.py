from scipy.cluster import hierarchy
import scipy.spatial.distance as ssd
import numpy as np

from bson import ObjectId
from flask import current_app

from flaskr.db import get_db
from ..db import conn
import json

def update_stats(study_id):
    with current_app.app_context():
        cur = conn.cursor()

    cur.execute("""SELECT (CAST(SUM(CASE WHEN CARDS_SORTED = 100 THEN 1 ELSE 0 END) AS FLOAT)/COUNT(*))*100 AS 
                   COMPLETION FROM PARTICIPANT WHERE STUDY_ID=%s""", (str(study_id),))
    completion = cur.fetchone()[0]
    cur.execute("""SELECT (CAST(SUM(CARDS_SORTED) AS FLOAT)/COUNT(*)) AS 
                   COMPLETION FROM PARTICIPANT WHERE STUDY_ID=%s""", (str(study_id),))
    average_sort = cur.fetchone()[0]

    cur.execute("""UPDATE STATS SET COMPLETION = %s WHERE STUDY_ID = %s""", (completion, str(study_id),))
    cur.execute("""UPDATE STATS SET AVERAGE_SORT = %s WHERE STUDY_ID = %s""", (average_sort, str(study_id),))
    conn.commit()


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
        cur = conn.cursor()

    cur.execute("""SELECT * FROM STATS WHERE STUDY_ID=%s""", (str(study_id),))
    study = cur.fetchone()
    clusters_calculating = study[4]
    clusters_changed = study[5]

    if clusters_changed:
        if clusters_calculating:
            return {'message': 'calculating'}
        cur.execute("""UPDATE STATS SET CLUSTERS_CALCULATING = TRUE WHERE STUDY_ID = %s""", (str(study_id),))
        conn.commit()

        distance = study[7]['matrix']
        card_names = study[7]['cardNames']
        cur.execute("""SELECT COUNT(ID) FROM PARTICIPANT WHERE STUDY_ID = %s""", (str(study_id),))
        total_participants = cur.fetchone()[0]

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

        cur.execute("""UPDATE STATS SET CLUSTERS = %s WHERE STUDY_ID = %s""", (json.dumps(dendro), str(study_id),))
        cur.execute("""UPDATE STATS SET CLUSTERS_CALCULATING = FALSE WHERE STUDY_ID = %s""", (str(study_id),))
        cur.execute("""UPDATE STATS SET CLUSTERS_CHANGED = FALSE WHERE STUDY_ID = %s""", (str(study_id),))
        conn.commit()
    else:
        dendro = json.loads(study[6])

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

    # matrix = np.tril(diagonal_matrix, k=-1)
    # matrix = matrix + matrix.T
    # matrix = matrix * (-100 / total_sorts) + 100
    # np.fill_diagonal(matrix, 0)
    # return matrix


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
