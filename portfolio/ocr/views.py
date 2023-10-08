import io
from PIL import Image
from base64 import b64encode
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.templatetags.static import static
from ocr.net import *
from ocr.utils import *


def index(request):
    return render(request, "ocr/ocr.html", {"show_result": False})

def process_image(request):
    if request.method == "POST":
        if "ocr-file" not in request.FILES:
            image = Image.open(settings.BASE_DIR / settings.STATIC_BASE / "img/ocr_sample.png")
        else:
            image = Image.open(request.FILES["ocr-file"])
        try:
            # Set render params
            ocr_image_buffered = io.BytesIO()
            # Get image
            image_format = image.format
            image = image.convert("RGB")
            # Get models
            craft_model = CRAFTModel(saved_model=settings.OCR_TEXT_DETECTION_MODEL_SAVE_PATH).model
            trocr_model = TrOCRModel(saved_model=settings.OCR_TEXT_RECOGNITION_MODEL_SAVE_PATH).model
            # Get detected texts
            detected_text_image, detections = text_detect(image=image, model=craft_model)
            # Get recognized texts
            recognized_texts = text_recognize(image=image, model=trocr_model, detections=detections)
            # Save image
            detected_text_image_pil_image = Image.fromarray(detected_text_image)
            detected_text_image_pil_image.save(ocr_image_buffered, format=image_format)
            # Prep render
            base64_og_image = b64encode(ocr_image_buffered.getvalue()).decode()
            base64_og_image_mime = f"image/{image_format.lower()};"
            if len(detections.items()) > settings.OCR_MAX_RECOGNITIONS:
                messages.success(request, f"OCR performed successfully! Due to may text blobs, only the first {settings.OCR_MAX_RECOGNITIONS}/{len(detections.items())} detected texts are mentioned in the table, rest all are skipped.")
            else:
                messages.success(request, f"OCR performed successfully!")
            return render(request, "ocr/ocr.html", {
                "show_result": True,
                "ocr_image": "data:%sbase64,%s" % (base64_og_image_mime, base64_og_image),
                "recognized_texts": recognized_texts
            })
        except Exception as e:
            messages.error(request, f"An error occurred: `{e}`. Please try again later.")
    return redirect("ocr:ocr")