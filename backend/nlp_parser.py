def clean_ingredient_text(raw_text: str):
	"""
	Takes raw OCR text and uses NLP (spaCy) to clean and separate ingredients.
	"""
	# TODO: Implement actual NLP cleaning logic
	# Find "INGREDIENTS:" or "Ingredients:" and split by commas
	# For now, returning dummy array
	return ["Enriched flour", "Sugar", "Palm Oil", "Maltodextrin", "Yellow 5"]


def match_allergies(ingredients_list, user_allergies):
	# Dummy matcher
	return [ing for ing in ingredients_list if ing.lower() in user_allergies]
