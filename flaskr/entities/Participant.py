from bson import ObjectId
from flask import current_app, jsonify

from flaskr.db import get_db
from flaskr.stats.Stats import update_card_stats, update_categories_stats, update_similarity_matrix, calculate_clusters


class Participant:
    def __init__(self):
        with current_app.app_context():
            self.studies = get_db()['studies']
            self.participants = get_db()['participants']
        self.participant_id = 0

    def post_categorization(self, study_id, categories, non_sorted, time, comment, new_categories=None):

      study = list(self.studies.find({'_id': ObjectId(study_id)}))
      if len(study) == 0:
        return {'message': 'STUDY NOT FOUND'}

    # Merge new categories for hybrid sorts
      if new_categories:
        categories.update(new_categories)

    # Calculate basic stats
      categories_no = len(categories)
      cards_sorted = sum(len(c['cards']) for c in categories.values())
      cards_sorted_percent = int((cards_sorted / len(study[0]['cards'])) * 100)



    # Insert the participant's result
      item = self.participants.insert_one({
        'categories': categories,
        'not_sorted': non_sorted,
        'cards_sorted': cards_sorted_percent,
        'categories_no': categories_no,
        'time': time,
        'comment': comment,
        
    })

      self.participant_id = ObjectId(item.inserted_id)

    # Link participant to study
      self.studies.update_one({'_id': ObjectId(study_id)}, {'$addToSet': {'participants': self.participant_id}})

    # Update counters
      if cards_sorted_percent == 100:
        completed = study[0].get('completedNo', 0)
        self.studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'completedNo': completed + 1}})
      else:
        abandoned = study[0].get('abandonedNo', 0)
        self.studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'abandonedNo': abandoned + 1}})

    # Mark stats as changed
      self.studies.update_one({'_id': ObjectId(study_id)}, {'$set': {'stats.clusters_changed': True}})

    # Update local study doc again after changes
      study_doc = self.studies.find_one({'_id': ObjectId(study_id)})
      categories_stats = study_doc.get('categories', {})
      cards_stats = study_doc['cards']

      
      for cat in categories_stats.values():
         if 'participant_ids' in cat and str(self.participant_id) in cat['participant_ids']:
           cat['participant_ids'].remove(str(self.participant_id))
           cat['participants'] = max(cat['participants'] - 1, 0)

         if 'category_participant_keys' in cat:
           cat['category_participant_keys'] = [
            k for k in cat['category_participant_keys']
            if not k.startswith(str(self.participant_id))
        ]

      for card in cards_stats.values():
         if 'card_category_keys' in card:
          card['card_category_keys'] = [
            k for k in card['card_category_keys']
            if not k.startswith(str(self.participant_id))
        ]


    # Aggregate participant result into study-level categories/cards
      for cat_id, cat_data in categories.items():
        card_ids = cat_data['cards']
        title = cat_data['title']
        normalized_title=title.strip().lower()
        

        # Categories
        if normalized_title not in categories_stats:
            categories_stats[normalized_title] = {
                'cards': [],
                'frequencies': [],
                'participants': 0,
                'participant_ids': [],
                'category_participant_keys': [],
                'display_title': title
            }
        # if some key doesnt exist at the moment create with default value(filling missing category fields)
        cat_stat = categories_stats[normalized_title]
        cat_stat.setdefault('cards', [])
        cat_stat.setdefault('frequencies', [])
        cat_stat.setdefault('participants', 0)
        cat_stat.setdefault('participant_ids', [])
        cat_stat.setdefault('category_participant_keys', [])
        cat_stat.setdefault('display_title', title)

            
        participant_ids = set(categories_stats[normalized_title].get('participant_ids', []))
        if str(self.participant_id) not in participant_ids:
               participant_ids.add(str(self.participant_id))
               categories_stats[normalized_title]['participants'] += 1
               categories_stats[normalized_title]['participant_ids'] = list(participant_ids)

        # Count cards and frequencies
        for card_id in card_ids:
           card_name = cards_stats[str(card_id)]['name']
           key = f"{str(self.participant_id)}__{normalized_title}__{card_name.lower()}"


           if key not in categories_stats[normalized_title]['category_participant_keys']:
             categories_stats[normalized_title]['category_participant_keys'].append(key)

             if card_name not in categories_stats[normalized_title]['cards']:
               categories_stats[normalized_title]['cards'].append(card_name)
               categories_stats[normalized_title]['frequencies'].append(0)
               

           if 'participant_ids' not in cards_stats[str(card_id)]:
             cards_stats[str(card_id)]['participant_ids'] = []


            # Cards
           card_stat = cards_stats[str(card_id)]

           # Ensure structure
           if 'categories' not in card_stat:
             card_stat['categories'] = []
             card_stat['frequencies'] = []

           if 'card_category_keys' not in card_stat:
             card_stat['card_category_keys'] = []  # tracks unique (participant, category)


           card_key = f"{str(self.participant_id)}__{normalized_title}__{card_name.lower()}"


           if card_key not in card_stat['card_category_keys']:
             card_stat['card_category_keys'].append(card_key)

             existing_titles = [t.lower() for t in card_stat['categories']]
             if normalized_title not in existing_titles:
              display_title = categories_stats[normalized_title]['display_title']
              card_stat['categories'].append(display_title)
              card_stat['frequencies'].append(0)  # placeholder

              
        #Cleanup before store data into DB
      for cat in categories_stats.values():
        if 'category_participant_keys' in cat:
         cat['category_participant_keys'] = list(set(cat['category_participant_keys']))

      for card in cards_stats.values():
        if 'card_category_keys' in card:
         card['card_category_keys'] = list(set(card['card_category_keys']))

    


    # Save updates to study
      self.studies.update_one(
        {'_id': ObjectId(study_id)},
        {'$set': {
         'categories': categories_stats,
         'cards': cards_stats
        }}
    )

    # Recompute global stats
      update_card_stats(study_id, str(self.participant_id))
      update_categories_stats(study_id, str(self.participant_id))
      update_similarity_matrix(study_id, str(self.participant_id))
