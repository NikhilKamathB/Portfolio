import io
import os
import sys
import logging
from PIL import Image
from base64 import b64encode
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from model import CRAFTModel, TrOCRModel
from utils import text_detect, text_recognize


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s || %(levelname)s || %(message)s")
load_dotenv()

DEFAULT_IMAGE_PATH = "ocr_sample.png"
DEFAULT_CRAFT_MODEL_PATH = "craft_mlt_25k.pth"
DEFAULT_TROCR_MODEL_PATH = None
OCR_MAX_RECOGNITIONS = 16

def process_image(request):
    try:
        app.logger.info(f"Loading image from request.")
        if "ocr-file" not in request.files:
            image = Image.open(DEFAULT_IMAGE_PATH)
        else:
            image = Image.open(request.files["ocr-file"])
        app.logger.info(f"Image opened successfully.")
        # Set render params
        ocr_image_buffered = io.BytesIO()
        app.logger.info(f"Buffer created successfully.")
        # Get image
        image_format = image.format
        image = image.convert("RGB")
        app.logger.info(f"Image converted to RGB successfully.")
        # Get models
        craft_model = CRAFTModel(saved_model=DEFAULT_CRAFT_MODEL_PATH).model
        trocr_model = TrOCRModel(saved_model=DEFAULT_TROCR_MODEL_PATH).model
        app.logger.info(f"Model loaded successfully.")
        # Get detected texts
        detected_text_image, detections = text_detect(image=image, model=craft_model)
        app.logger.info(f"Text detected successfully.")
        # Get recognized texts
        recognized_texts = text_recognize(image=image, model=trocr_model, detections=detections, max_instances=OCR_MAX_RECOGNITIONS)
        app.logger.info(f"Text recognized successfully.")
        # Save image
        detected_text_image_pil_image = Image.fromarray(detected_text_image)
        detected_text_image_pil_image.save(ocr_image_buffered, format=image_format)
        app.logger.info(f"Image saved successfully.")
        # Prep render
        base64_og_image = b64encode(ocr_image_buffered.getvalue()).decode()
        base64_og_image_mime = f"image/{image_format.lower()};"
        app.logger.info(f"Image encoded successfully.")
        special_message = ""
        if len(detections.items()) > OCR_MAX_RECOGNITIONS:
            special_message = f"OCR performed successfully! Due to may text blobs and reduce response time, only the first {OCR_MAX_RECOGNITIONS}/{len(detections.items())} detected texts are mentioned in the table, rest all are skipped."
        return {
            "success": True,
            "ocr_image": "data:%sbase64,%s" % (base64_og_image_mime, base64_og_image),
            "recognized_texts": recognized_texts,
            "special_message": special_message
        }
    except Exception as e:
        app.logger.error(f"An error occurred: `{e}`. Please try again later.")
        return {
            "success": False,
            "error": f"An error occurred: `{e}`. Please try again later."
        }

@app.route("/", methods=['POST'])
def ocr():
    return jsonify(process_image(request))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))