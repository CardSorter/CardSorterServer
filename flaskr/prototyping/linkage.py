from scipy.cluster import hierarchy
import scipy.spatial.distance as ssd
import numpy as np
import matplotlib.pyplot as plt
# 
# 
# def calculate_square_form(diagonal_matrix, total_sorts):
#     """
#     Takes a diagonal matrix converts it to it's full form
#     :param diagonal_matrix: a diagonal matrix
#     :param total_sorts
#     :return: the nxn redundant matrix
#     """
#     n = len(diagonal_matrix)
# 
#     matrix = np.ndarray(shape=(n,n))
# 
#     for i in range(n):
#  ,for j in range(len(diagonal_matrix[i], )):
# ,   matrix[i], [j],  = 100 - 100 * diagonal_matrix[i], [j],  / total_sorts
# ,   matrix[j], [i],  = 100 - 100 * diagonal_matrix[i], [j],  / total_sorts
# ,   if i == j:
# , , matrix[i], [j],  = 0
# 
#     return matrix


# Runtime

# times = [[24], , [16, 16], , [7, 1, 9], , [6, 1, 1, 9], , [0, 0, 1, 0, 3], , [1, 0, 0, 2, 0, 3], , [0, 0, 0, 0, 2, 0, 3], , [0, 1, 1, 0, 0, 0, 0, 1], , [0, 0, 0, 0, 0, 1, 0, 0, 1], , [0, 0, 0, 0, 0, 1, 0, 0, 1, 1], , [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1], , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], , [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1], , [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1], , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], , [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], , [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1], ], 
# # times = [[3], , [3, 3], , [0, 0, 3], ], 
# 
# distance_matrix = calculate_square_form(times, 29)
# distArray = ssd.squareform(distance_matrix)
# 
# clusters = hierarchy.linkage(distArray, method='average')
# print(clusters)

clusters = np.array([[0., 1., 43.75,  2.],
 [2., 20., 85.9375, 3.],
 [3., 21., 90.625, 4.],
 [4., 6., 90.625, 2.],
 [5., 8., 93.75,  2.],
 [7., 10., 93.75,  2.],
 [9., 24., 93.75,  3.],
 [15., 17., 93.75,  2.], 
 [22., 25., 96.875, 6.],
 [11., 23., 96.875, 3.], 
 [12., 26., 96.875, 4.], 
 [13., 18., 96.875, 2.], 
 [19., 31., 96.875, 3.], 
 [16., 27., 96.875, 3.], 
 [28., 29., 97.91666667, 9.], 
 [30., 34., 98.69791667, 13.], 
 [32., 33., 99.30555556, 6.], 
 [14., 35., 99.75961538, 14.], 
 [36., 37., 99.85119048, 20.]])

card_names = ['Card 1', 'Card 2', 'Card 3', 'Card 4', 'Card 5', 'Card 6', 'Card 7', 'Card 8', 'Card 9', 'Card 10',
              'Card 11', 'Card 12', 'Card 13', 'Card 14', 'Card 15', 'Card 16', 'Card 17', 'Card 18', 'Card 19', 'Card 20']


# Create a nested dictionary from the ClusterNode's returned by SciPy
def add_node(node, parent):
    # First create the new node and append it to its parent's children
    newNode = dict(children=[])
    # Append the name only if the node is a leaf
    if node.id < len(card_names):
        newNode.update(name=card_names[node.id])

    parent["children"].append(newNode)

    # Recursively add the current node's children
    if node.left:
        add_node(node.left, newNode)
    if node.right:
        add_node(node.right, newNode)


tree = hierarchy.to_tree(clusters, rd=False)
d3Dendro = dict(children=[], name="Root1")
add_node(tree, d3Dendro)

print(d3Dendro)

fig = plt.figure(figsize=(25, 10))
dn = hierarchy.dendrogram(clusters)
plt.show()