import os, json
from PIL import Image
import pytesseract
from ..config import TESSERACT_CMD

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def extract_text(path):
    text = pytesseract.image_to_string(Image.open(path))
    return text

def basic_fields(text):
    fields={}
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    for line in lines[:50]:
        if ":" in line:
            k,v=line.split(":",1)
            fields[k.strip().lower().replace(" ","_")] = v.strip()
    return fields
