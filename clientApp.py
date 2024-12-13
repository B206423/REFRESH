from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS, cross_origin
import resume_coach_main
import uuid
import toml

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
    return render_template('index.html')

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

    # TODO: read pdf and convert to text
    resume_file_content = resume_file.read().decode('utf-8')
    jd_file_content = jd_file.read().decode('utf-8')
    session_id = str(uuid.uuid4())

    # TODO: store the file contents into a DB
    response = {
        'resume_file_content': resume_file_content,
        'jd_file_content': jd_file_content,
        'session_id': session_id
    }

    return jsonify(response)

@app.route('/report', methods=['POST'])
def report():
    global resume_file_content, jd_file_content

    data = request.get_json()
    resume_file_content = data.get('resume_file_content')
    jd_file_content = data.get('jd_file_content')
    session_id = data.get('session_id')

    resume_report= resume_coach_main.resume_report(session_id, resume_file_content)
    jd_compatibility_report = resume_coach_main.jd_compatibility_report(session_id, jd_file_content)
    # TODO: Suresh: add matching jobs
    #jobs_reports = q_and_a(rec_prompt, chat_history)

    response = {
        'resume_report': resume_report,
        'jd_compatibility_report': jd_compatibility_report
    }

    return jsonify(response)

if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host='0.0.0.0', port=9000, debug=True)
