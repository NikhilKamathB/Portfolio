import os
import logging
from dotenv import load_dotenv
from transformers import BartTokenizer
from flask import Flask, jsonify, request
from model import BartForConditionalGeneration


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format="CM-MT || %(asctime)s || %(levelname)s || %(message)s")
load_dotenv()

ENCODER_TOKENIZER_PATH = "encoder_tokenizer"
DECODER_TOKENIZER_PATH = "facebook/bart-large"
MT_MODEL_PATH = "mt_model"
DEVICE = "cpu"
ADD_SPECIAL_TOKENS = True
MAX_LENGTH = 25
RETURN_TENSORS = "pt"
PADDING = "max_length"
TRUNCATION = True
VERBOSE = False
GENERATION_MAX_LENGTH = 50
GENERATION_NUM_BEAMS = 5
GENERATION_EARLY_STOPPING = True

def process_text(request):
    try:
        app.logger.info(f"Creating encoder tokenizer.")
        encoder_tokenizer = BartTokenizer.from_pretrained(ENCODER_TOKENIZER_PATH)
        app.logger.info(f"Creating decoder tokenizer.")
        decoder_tokenizer = BartTokenizer.from_pretrained(DECODER_TOKENIZER_PATH)
        app.logger.info(f"Creating model.")
        model = BartForConditionalGeneration(pretrained_path=MT_MODEL_PATH, device=DEVICE).model
        app.logger.info(f"Get text from request.")
        text = request.json.get("text")
        app.logger.info(f"Got text: {text}")
        if text is None or text == "":
            text = "hi tum kaisi ho? ye ek default text hai."
        app.logger.info(f"Get tokenize text.")
        src_tokenized = encoder_tokenizer(
            text,
            add_special_tokens=ADD_SPECIAL_TOKENS,
            max_length=MAX_LENGTH,
            return_tensors=RETURN_TENSORS,
            padding=PADDING,
            verbose=VERBOSE
        )
        app.logger.info(f"Get translation ids.")
        translation_ids = model.generate(
            src_tokenized['input_ids'],
            max_length=GENERATION_MAX_LENGTH,
            num_beams=GENERATION_NUM_BEAMS,
            early_stopping=GENERATION_EARLY_STOPPING
        )
        app.logger.info(f"Get translation text.")
        if translation_ids.shape[1] > 1:
            translation_text = decoder_tokenizer.decode(translation_ids[0], skip_special_tokens=True)
        else:
            translation_text = "Unable to translate! Sorry!"
        return {
            "success": True,
            "translation": translation_text
        }
    except Exception as e:
        app.logger.error(f"An error occurred: `{e}`. Please try again later.")
        return {
            "success": False,
            "error": f"An error occurred: `{e}`. Please try again later."
        }

@app.route("/", methods=['POST'])
def translate():
    return jsonify(process_text(request))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))