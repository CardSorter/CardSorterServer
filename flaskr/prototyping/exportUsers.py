# with app.app_context():
#     studies = get_db()['studies']
#     users = get_db()['participants']
#
# study_users = list(studies.find({'_id': ObjectId('5cdd8a498c16216f46ec13bc')}))[0]['participants']
#
# f = open('participants.csv', 'w+')
# writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
# writer.writerow(['comment', 'cards sorted', 'time taken'])
#
# for user in study_users:
#     u = users.find({'_id': user}, {'_id': 0, 'time': 1, 'cards_sorted': 1, 'comment': 1})
#     try:
#         u = list(u)[0]
#         writer.writerow([u['comment'], u['cards_sorted'], u['time']])
#     except IndexError:
#         continue
#
# f.close()