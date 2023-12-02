import cv2
import copy
import torch
import numpy as np
from PIL import Image
from transformers import TrOCRProcessor


OCR_IMAGE_RESIZE = (768, 768)
OCR_CV2_THRESHOLD_LOW = 100
OCR_CV2_THRESHOLD_HIGH = 255
OCR_CV2_DILATE_KERNEL_SIZE = (3, 3)
OCR_CV2_DILATE_ITERATION = 1
OCR_CV2_DETECTION_BUFFER = 2
OCR_TEXT_RECOGNITION_PROCESSOR = "microsoft/trocr-base-handwritten"

def resize(image: object, size: tuple = (768, 768)) -> np.ndarray:
    '''
        Resize the image.
        Input params: 
            image: Image to resize.
            size: Size to resize to.
        Output params:
            image: Resized image.
    '''
    og_image = copy.deepcopy(image)
    if isinstance(image, np.ndarray):
        og_image = Image.fromarray(og_image)
    return np.asarray(og_image.resize((size[1], size[0])))

def normalize_image(image: np.ndarray, mean: tuple = (0.485, 0.456, 0.406),
                    variance: tuple = (0.229, 0.224, 0.225)) -> np.ndarray:
    '''
        Normalize image.
        Input params:
            image: np.ndarray of shape (image_height, image_width, channels[optional]).
            mean: mean of image.
            variance: variance of image.
        Returns: normalized image.
    '''
    image = image - np.array([mean[0]*255, mean[1]*255, mean[2]*255], dtype=np.float32)
    image = image / np.array([variance[0]*255, variance[1]*255, variance[2]*255], dtype=np.float32)
    image = np.clip(image, 0, 1).astype(np.float32)
    return image

def get_bbox(image: Image, region_map: np.ndarray) -> tuple:
    '''
        Get bounding box for the image, given a region map.
        Input params:
            image: Image to get bounding box for.
            region_map: Region map of the image.
        Output params: (tuple)
            image: Image with bounding box.
            detections: Bounding box for the image.
    '''
    region_map *= 255.0
    region_map = region_map.astype(np.uint8)    
    _, region_map = cv2.threshold(region_map, OCR_CV2_THRESHOLD_LOW, OCR_CV2_THRESHOLD_HIGH, cv2.THRESH_BINARY)
    region_map_dilated = cv2.dilate(region_map, np.ones(OCR_CV2_DILATE_KERNEL_SIZE, np.uint8), iterations=OCR_CV2_DILATE_ITERATION)
    region_map_contours, region_map_hierarchy = cv2.findContours(region_map_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    detections = {}
    for idx, contour in enumerate(region_map_contours):
        if contour.shape[0] <= 1:
            continue
        x_min, y_min = np.inf, np.inf
        x_max, y_max = -np.inf, -np.inf
        for point in contour:
            x_min = min(x_min, point[0][0])
            y_min = min(y_min, point[0][1])
            x_max = max(x_max, point[0][0])
            y_max = max(y_max, point[0][1])
        detections[f"bbox_{idx+1}"] = { "actual_bbox": (
                (int(x_min - OCR_CV2_DETECTION_BUFFER), int(y_min - OCR_CV2_DETECTION_BUFFER)),
                (int(x_max + OCR_CV2_DETECTION_BUFFER), int(y_max + OCR_CV2_DETECTION_BUFFER))
            ),
            "normalized_bbox": (
                (int(x_min - OCR_CV2_DETECTION_BUFFER)/region_map.shape[1], int(y_min - OCR_CV2_DETECTION_BUFFER)/region_map.shape[0]),
                (int(x_max + OCR_CV2_DETECTION_BUFFER)/region_map.shape[1], int(y_max + OCR_CV2_DETECTION_BUFFER)/region_map.shape[0])
            )
        }
    image_resized = resize(image=image, size=(region_map.shape[0], region_map.shape[1]))
    for _, v in detections.items():
        x1, y1 = int(v["normalized_bbox"][0][0] * region_map.shape[1]), int(v["normalized_bbox"][0][1] * region_map.shape[0])
        x2, y2 = int(v["normalized_bbox"][1][0] * region_map.shape[1]), int(v["normalized_bbox"][1][1] * region_map.shape[0])
        image_resized = cv2.rectangle(image_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return (image_resized, detections)

def text_detect(image: Image, model: object) -> tuple:
    '''
        Process the image.
        Input params:
            image: Image to process.
            model: Model to use for processing.
        Output params: (tuple)
            image: Image with bounding box.
            detections: Bounding box for the image.
    '''
    # Get the image in model readable format.
    model.eval()
    og_image = copy.deepcopy(image)
    image = resize(image=image, size=OCR_IMAGE_RESIZE)
    og_resized_image = copy.deepcopy(image)
    image = normalize_image(image=image)
    image = torch.from_numpy(image) # image shape - h, w, c
    image = image.unsqueeze(0) # image shape - 1, h, w, c
    image = image.permute(0, 3, 1, 2) # image shape - 1, c, h, w
    image = torch.autograd.Variable(image)
    # Feed this image into the model.
    output, _ = model(image)
    output = output.cpu().detach().numpy()
    region_map, _ = output[0, :, :, 0], output[0, :, :, 1]
    # Get bounding boxes from the output for this image.
    image, detections = get_bbox(image=og_resized_image, region_map=region_map)
    res_image = resize(image=image, size=(og_image.size[1], og_image.size[0]))
    return (res_image, detections)

def text_recognize(image: Image, model: object, detections: dict, processor: str = OCR_TEXT_RECOGNITION_PROCESSOR, max_instances: int = 16) -> list:
    '''
        Process the image.
        Input params:
            image: Image to process.
            model: Model to use for processing.
            detections: Bounding box for the image (detected texts).
            processor: Processor to use for processing.
        Output params:
            result: List of tuples containing the bounding box and the text.
    '''
    # Get the image in model readable format.
    model.eval()
    image = np.asarray(image)
    image_w, image_h = image.shape[1], image.shape[0]
    processor = TrOCRProcessor.from_pretrained(processor)
    result = []
    for idx, detection in enumerate(detections.values()):
        x1, y1 = int(detection["normalized_bbox"][0][0] * image_w), int(detection["normalized_bbox"][0][1] * image_h)
        x2, y2 = int(detection["normalized_bbox"][1][0] * image_w), int(detection["normalized_bbox"][1][1] * image_h)
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(image_w, x2)
        y2 = min(image_h, y2)
        query_image = image[y1:y2, x1:x2]
        processed_query_image = processor(query_image, return_tensors="pt").pixel_values
        output = model.generate(processed_query_image)
        output = output.cpu().detach().numpy()
        output = processor.batch_decode(output, skip_special_tokens=True)[0]
        result.append((x1, y1, x2, y2, output))
        if idx+1 >= max_instances:
            break
    sorted_result = sorted(result, key=lambda x: (x[1], x[0]))
    return sorted_result