from flask import Flask, request, jsonify
from io import BytesIO
import os

from processor import processImage

app = Flask(__name__)
CORS_ORIGIN = 'http://localhost:8080'
OUTPUT_PATH = 'assets'

class InvalidFiletype(Exception):
  status_code = 400

  def __init__(self, message, status_code=None, payload=None):
    Exception.__init__(self)
    self.message = message
    if status_code is not None:
      self.status_code = status_code
    self.payload = payload

  def to_dict(self):
    rv = dict(self.payload or ())
    rv['message'] = self.message
    return rv

@app.errorhandler(InvalidFiletype)
def handle_invalid_filetype(error):
  response = jsonify(error.to_dict())
  response.status_code = error.status_code
  return response


@app.route('/api/upload', methods=['OPTIONS'])
def upload_options():
    print('setting up response for options')
    resp = jsonify({'foo': 'bar baz'})
    resp.headers.add('Access-Control-Allow-Origin', CORS_ORIGIN)
    resp.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    resp.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    resp.status_code = 200
    return resp

@app.route("/api/upload/<int:id>", methods=["POST"])
def upload(id):
  print('Received uploads')
  outputs = []

  for upload in request.files.getlist('images'):
    filename = upload.filename
    print('processing file: ', filename)

    ext = os.path.splitext(filename)[1][1:].strip().lower()
    if ext in set(['jpg', 'jpeg', 'png']):
      print('File supported moving on.')
    else:
      raise InvalidFiletype('Unsupported file type {}'.format(ext), status_code=415)

    imageInBytes = BytesIO(upload.read())
    outputImageProcessing = processImage(imageInBytes, OUTPUT_PATH)
    outputs.append(outputImageProcessing)

  response = jsonify({ 'uploaded': outputs })
  response.headers.add('Access-Control-Allow-Origin', CORS_ORIGIN)
  response.status_code = 200

  # print(uploaded_files)
  return response

if __name__ == '__main__':
  app.run(port=5001)
