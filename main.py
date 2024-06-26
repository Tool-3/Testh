import pytesseract
import cv2
from camelot import read_pdf
from flask import Flask, request, jsonify
import asyncio  # For asynchronous processing (optional)

def preprocess_image(img):
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  denoised = cv2.bilateralFiltering(gray, 11, 17, 17)
  cnts = cv2.findContours(denoised.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
  cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
  rect = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
  x, y, w, h = cv2.boundingRect(rect)
  roi = denoised[y:y+h, x:x+w]
  moments = cv2.moments(roi)
  skew = cv2.atan2(moments['mu11'], moments['mu02'])
  rows, cols, _ = roi.shape
  M = cv2.getRotationMatrix2D((cols/2, rows/2), -skew, 1)
  deskewed = cv2.warpAffine(roi, M, (cols, rows))
  thresh = cv2.adaptiveThreshold(deskewed, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
  return thresh

def extract_text(image_path):
  try:
    img = cv2.imread(image_path)
    if preprocess_image:
      img = preprocess_image(img)
    text = pytesseract.image_to_string(img)
    return text
  except Exception as e:
    return f"Error: {e}"

def extract_table_text(pdf_path):
  try:
    tables = read_pdf(pdf_path, flavor='stream')  # Adjust flavor as needed
    table_data = []
    for table in tables:
      table_data.append(table.df.to_csv(sep='\t'))  # Adjust separator as needed
    return table_data
  except Exception as e:
    return f"Error: {e}"

app = Flask(__name__)

@app.route("/", methods=["POST"])
def handle_ocr():
  if request.method == "POST":
    if "file" not in request.files:
      return jsonify({"error": "Missing file upload"})
    file = request.files["file"]
    if not allowed_file(file.filename):
      return jsonify({"error": "Unsupported file format"})
    if file.filename.endswith(".pdf"):
      text = extract_table_text(file.stream)
    else:
      text = extract_text(file.stream)
    return jsonify({"text": text})

def allowed_file(filename):
  # Define allowed file extensions here (e.g., .jpg, .png, .pdf)
  return True  # Replace with your logic

if __name__ == "__main__":
  app.run(debug=True)  # Set debug to False for deployment
