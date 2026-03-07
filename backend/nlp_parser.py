import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.blank("en")

# Markers that signal the end of the ingredients section
_END_MARKERS = re.compile(
    r"(contains:|may contain|allergen|nutrition facts|manufactured|distributed)",
    re.IGNORECASE,
)


def clean_ingredient_text(raw_text: str) -> list:
    """
    Takes raw OCR text and uses NLP (spaCy) to clean and separate ingredients.
    Finds the 'Ingredients:' section and extracts a clean list of ingredient strings.
    """
    match = re.search(r"ingredients\s*[:\-]?\s*(.+)", raw_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return []

    ingredients_text = match.group(1)

    # Truncate at end-of-section markers
    cut = _END_MARKERS.search(ingredients_text)
    if cut:
        ingredients_text = ingredients_text[: cut.start()]

    # Split on commas and clean each token with spaCy
    cleaned = []
    for raw_item in ingredients_text.split(","):
        raw_item = raw_item.strip()
        if not raw_item:
            continue
        doc = nlp(raw_item)
        tokens = [t.text for t in doc if not t.is_punct]
        cleaned_item = " ".join(tokens).strip()
        if cleaned_item:
            cleaned.append(cleaned_item)

    return cleaned


def match_allergies(ingredients_list: list, user_allergies: list) -> list:
    """
    Checks each ingredient against user dietary restrictions/allergies.
    Returns the list of flagged ingredients.
    """
    lower_allergies = [a.lower() for a in user_allergies]
    return [
        ing
        for ing in ingredients_list
        if any(allergen in ing.lower() for allergen in lower_allergies)
    ]
