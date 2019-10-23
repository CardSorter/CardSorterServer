import categories


card_names = []
times_in_same_category = [[]]

for caterogy in categories:
  cards = category.cards
  
  for card in cards:
    if card not in card_names:
      card_names.append(card)

    index = card_names.index(card)

    for card2 in cards:
      # Calculate only the upper triangle
      if card < card2:
        break

      if card2 not in card_names:
        card_names.append(card2)

      index2 = card_names.index(card2)

      times_in_same_category[index][index2] += 1


      