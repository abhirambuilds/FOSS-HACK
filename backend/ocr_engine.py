import logging
import io
from PIL import Image, UnidentifiedImageError
import pytesseract

logger = logging.getLogger(__name__)


def extract_text_from_image(image_file):
	"""
	Takes an image file and runs Tesseract OCR to extract raw text.
	"""
	logger.info("Running OCR extraction...")
	try:
		if isinstance(image_file, bytes):
			image = Image.open(io.BytesIO(image_file))
		else:
			# Assuming it's an uploaded_file.file or similar file-like object
			image = Image.open(image_file)
			
		image = image.convert("RGB")
		
		# Run OCR
		extracted_text = pytesseract.image_to_string(image)
		
		cleaned_text = extracted_text.strip()
		
		if not cleaned_text:
			logger.warning("OCR completed but no text was found. Image might be blurry or blank.")
			
		return cleaned_text
		
	except UnidentifiedImageError:
		logger.error("Failed to process image: File is not a valid image format.")
		raise ValueError("Invalid image file format.")
	except pytesseract.TesseractNotFoundError:
		logger.error("Tesseract not found. Please ensure it is installed and in your PATH.")
		raise RuntimeError("OCR engine not configured properly.")
	except Exception as e:
		logger.error(f"Unexpected error during OCR extraction: {str(e)}")
		raise RuntimeError(f"OCR failed: {str(e)}")
