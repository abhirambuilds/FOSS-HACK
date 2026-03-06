import logging

logger = logging.getLogger(__name__)


def extract_text_from_image(image_file):
	"""
	Takes an image file and runs Tesseract OCR to extract raw text.
	"""
	logger.info("Running OCR extraction...")
	# TODO: Implement actual pytesseract logic here
	# For now, returning dummy text
	return "INGREDIENTS: Enriched flour, Sugar, Palm Oil, Maltodextrin, Yellow 5"
