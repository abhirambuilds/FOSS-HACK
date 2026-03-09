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


# ---------------------------------------------------------------------------
# Nutrition Facts parsing
# ---------------------------------------------------------------------------

# Each entry: (output_key, list_of_label_patterns)
_NUTRITION_PATTERNS: list[tuple[str, list[str]]] = [
    ("calories",   [r"calories"]),
    ("fat_g",      [r"total\s+fat", r"(?<!trans\s)(?<!saturated\s)fat"]),
    ("sat_fat_g",  [r"saturated\s+fat"]),
    ("trans_fat_g",[r"trans\s+fat"]),
    ("sodium_mg",  [r"sodium"]),
    ("carbs_g",    [r"total\s+carbohydrate", r"carbohydrates?"]),
    ("fiber_g",    [r"dietary\s+fiber", r"fiber"]),
    ("sugar_g",    [r"total\s+sugars?", r"sugars?"]),
    ("protein_g",  [r"protein"]),
]


def parse_nutrition_facts(raw_text: str) -> dict:
    """
    Scans *raw_text* (OCR output) for common Nutrition Facts anchors and
    extracts the numerical value that follows each label.

    Returns a dictionary such as::

        {
            'calories': 250,
            'fat_g': 9.0,
            'sugar_g': 24.0,
            'protein_g': 5.0,
            ...
        }

    Keys whose values cannot be found are omitted from the result.
    """
    result: dict[str, float] = {}

    for key, label_patterns in _NUTRITION_PATTERNS:
        for label in label_patterns:
            # Match the label then the first number (integer or decimal) that
            # follows on the same line, optionally separated by whitespace or
            # common OCR artefacts like '|' or ':'.
            pattern = (
                rf"{label}\s*[:\|]?\s*(\d+(?:\.\d+)?)"
            )
            m = re.search(pattern, raw_text, re.IGNORECASE)
            if m:
                result[key] = float(m.group(1))
                break  # found via this label; no need to try alternatives

    return result
