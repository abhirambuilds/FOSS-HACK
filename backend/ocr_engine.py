import logging
import io
from PIL import Image, UnidentifiedImageError
import pytesseract

logger = logging.getLogger(__name__)

# Tesseract config: LSTM engine, auto page segmentation
_TESS_CONFIG = "--psm 3 --oem 1"


def extract_text_from_image(image_file):
	"""
	Takes an image file and runs Tesseract OCR to extract raw text.
	Returns the entire text block from the image, prioritizing
	high-resolution (character-dense) blocks when multiple are detected.
	"""
	logger.info("Running OCR extraction...")
	try:
		if isinstance(image_file, bytes):
			image = Image.open(io.BytesIO(image_file))
		else:
			image = Image.open(image_file)

		image = image.convert("RGB")

		# Use image_to_data to get block-level information so we can
		# prioritize dense (high-resolution) text blocks.
		data = pytesseract.image_to_data(
			image,
			output_type=pytesseract.Output.DICT,
			config=_TESS_CONFIG,
		)

		# Group recognized words by their block number, skipping
		# low-confidence / empty tokens.
		blocks: dict[int, list[str]] = {}
		for i, block_num in enumerate(data["block_num"]):
			conf = int(data["conf"][i])
			word = data["text"][i].strip()
			if conf < 0 or not word:
				continue
			blocks.setdefault(block_num, []).append(word)

		if blocks:
			# Sort blocks by total character count descending so that the
			# richest (most information-dense) blocks appear first.
			sorted_blocks = sorted(
				blocks.values(),
				key=lambda words: sum(len(w) for w in words),
				reverse=True,
			)
			cleaned_text = "\n".join(" ".join(words) for words in sorted_blocks).strip()
		else:
			# Fallback: plain full-image extraction
			cleaned_text = pytesseract.image_to_string(image, config=_TESS_CONFIG).strip()

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
