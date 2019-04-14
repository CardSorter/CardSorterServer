from flask_restful import Api

from flaskr.endpoints.StudyResource import StudyResource as Studies
from flaskr.endpoints.CardSorterResource import CardSorterResource as CardSorter


class InitializeEndpoints:
    def __init__(self, app, db):
        self.api = Api(app)
        self.db = db

        self.add_card_resource()
        self.add_study_resource()

    def add_card_resource(self):
        self.api.add_resource(CardSorter, '/sort_endpoint')

    def add_study_resource(self):
        self.api.add_resource(Studies, '/studies_endpoint')
