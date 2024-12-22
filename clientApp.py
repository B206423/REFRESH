from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from flask_cors import CORS, cross_origin
import resume_coach_main
import uuid
import toml
import pdfplumber

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)

#@cross_origin()
class ClientApp:
  def __init__(self):
      self.dummy = None

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    #return render_template('index.html')
    return send_from_directory('static', 'index.html')


@app.route("/version", methods=['GET'])
@cross_origin()
def get_version():
    pyproject = toml.load("pyproject.toml")
    version = pyproject.get("tool", {}).get("poetry", {}).get("version", "Version not found")
    return jsonify({"version": get_version()})

@app.route('/upload', methods=['POST'])
def upload_files():
    resume_file = request.files.get('resume_file')
    jd_file = request.files.get('jd_file')

    if not resume_file or not jd_file:
        return jsonify({'error': 'Both files are required'}), 400

    resume_file_content = extract_text_from_file(resume_file)
    jd_file_content = extract_text_from_file(jd_file)
    session_id = str(uuid.uuid4())

    # TODO: store the file contents into a DB
    response = {
        'resume_file_content': resume_file_content,
        'jd_file_content': jd_file_content,
        'session_id': session_id
    }

    return jsonify(response)

def extract_text_from_file(file):
    if file.filename.endswith('.pdf'):
        return pdf_to_text(file)
    else:
        return file.read().decode('utf-8')

def pdf_to_text(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        return text    

@app.route('/report', methods=['POST'])
def report():
    global resume_file_content, jd_file_content

    data = request.get_json()
    resume_file_content = data.get('resume_file_content')
    jd_file_content = data.get('jd_file_content')
    session_id = data.get('session_id')

    resume_report= resume_coach_main.resume_report(session_id, resume_file_content)
    jd_compatibility_report = resume_coach_main.jd_compatibility_report(session_id, jd_file_content)

    jobs_reports = resume_coach_main.jobs_report(session_id, resume_file_content)

    response = {
        'resume_report': resume_report,
        'jd_compatibility_report': jd_compatibility_report,
        'jobs_reports': jobs_reports
    }

    return jsonify(response)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    session_id = data.get('session_id')

    reply = resume_coach_main.q_and_a(session_id=session_id, question=message)
    return jsonify({'reply': reply})

if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host='0.0.0.0', port=9000, debug=True)
