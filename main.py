import os
from urllib.parse import urljoin
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv




ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
auth = HTTPBasicAuth()



def setup():
    load_dotenv()
    app.secret_key = os.getenv('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/var/img')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH'))
    app.config['SESSION_TYPE'] = 'filesystem'
    if os.getenv('PASSWORD') is not None and os.getenv('USERNAME') is not None:
        app.config['USERS'] = {os.getenv('USERNAME'): generate_password_hash(os.getenv('PASSWORD'))}

@auth.verify_password
def verify_password(username, password):
    users = app.config['USERS']
    if username in users and check_password_hash(users.get(username), password):
        return username

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@auth.login_required
def index():
    # Get a list of all routes available in the app
    all_routes = []
    for url in app.url_map.iter_rules():
        if url.rule != '/':
            all_routes.append(url.rule)
    return jsonify(user=auth.current_user(), routes=all_routes)
    # return "Hello, {}!".format(auth.current_user())

@app.route('/upload', methods=['GET', 'POST'])
@auth.login_required
def upload_file():
    # You can test with CURL:
    # curl \
    #   -F "file=@/home/user/Desktop/test.jpg" \
    #   http://localhost:5000/upload
    
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify(success=True, filename=filename, path=urljoin(request.host_url, url_for('download_file', name=filename)))
            # return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/download/<name>')
@auth.login_required
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

setup()
app.debug = False

if __name__ == '__main__':
    setup()
    app.debug = True
    app.run(host='0.0.0.0', port=5001)