from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS, cross_origin
from predict import DogCatClassifier
import resume_coach_main

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)

#@cross_origin()
class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"
        self.classifier = DogCatClassifier(self.filename)

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')

@app.route("/version", methods=['GET'])
@cross_origin()
def get_version():
    return "2.0"
    
@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRoute():
    results = resume_coach_main.main_method(from_browser=True)
    print(f"/predict: {results[0]}")
    return jsonify(results)

if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host='0.0.0.0', port=9000, debug=True)
