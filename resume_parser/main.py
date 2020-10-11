from pyresparser import ResumeParser
from parser import resume_parser
import os
import requests

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '\xd9\xa5\xf9Y/\xb819]\xad\xecbE\xfc\x89\xe2\xa1\x97\xc55\xab\xc5\xa8o\xb2\xf1\xfdbA\xc1'

UPLOAD_FOLDER = \
    os.path.dirname(os.path.realpath(__file__)) + '/parsed_resumes/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'doc', 'pdf', 'docx'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    """
    Default form when called the server directly.
    """
    form = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <form action="/upload_resume" method="post" enctype=multipart/form-data>
                <input type="file" name="resume">
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
    '''
    return form


@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_file():
    """
        Resume handler to parse and return the data from resume.
    """
    if request.method == 'POST':
        json_data = request.get_json()
        if 'resume' not in json_data:
            return jsonify({
                'error': 'No file part please upload \
                    a file on "resume" parameter',
                'data': {}}), 400
        filename = json_data['resume']
        if filename == '':
            return jsonify({
                'error': 'No selected file',
                'data': {}}), 400
        if filename and allowed_file(filename):
            file_path = os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(filename))

            # Temporary save the file in parsed_resumes folder
            resume = requests.get(filename, allow_redirects=True)
            open(file_path, 'wb').write(resume.content)

            # Parse the data from resume
            data = ResumeParser(file_path).get_extracted_data()

            # Delete the file in parsed_resumes folder after fetching the data
            os.remove(file_path)

            return jsonify({
                'error': 'Success',
                'data': data}), 200
        else:
            return jsonify({
                'error': 'File format not supported. \
                    Please upload .pdf, .dox or .docx file.',
                'data': {}}), 400
    return jsonify({
        'error': 'Request Method is not supported, \
            please use request method as POST',
        'data': {}}), 405
