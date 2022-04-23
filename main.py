import os
from urllib.parse import urljoin
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from file_management import get_list_of_img_path, allowed_file, cleanup


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

@app.route('/sitemap')
def index():
    # Get a list of all routes available in the app
    all_routes = []
    for url in app.url_map.iter_rules():
        if url.rule != '/':
            all_routes.append(url.rule)
    
    if len(all_routes) > 0:
        return jsonify(success=True, routes=all_routes)
    else:
        # Return an error with a 500 status code
        return jsonify(error='No routes found'), 500

    

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
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/cleanup/', methods = ['POST'])
@auth.login_required
def keep_last_images():
    ## You can test with curl
    # curl -v -d '{"keep": "20"}' -H "Content-Type: application/json" -u 'username:password' -X POST http://127.0.0.1:5001/cleanup/
    # Remove the last number of files sent in the POST request
    if request.method == 'POST':
        try:
            jsonrequest = request.get_json()
            files_to_keep = int(jsonrequest.get('keep', 500))
        except:
            files_to_keep = 500

        files = get_list_of_img_path(path=app.config['UPLOAD_FOLDER'], reverse=True)
        # Keep the last X files
        removed_files = cleanup(files, keep=int(files_to_keep))
        # Masquerade the server path to the user
        removed_files = [os.path.basename(path) for path in removed_files]
        return jsonify(removed_files=removed_files, files_available=len(files), success=True)
    return jsonify(success=False), 400


@app.route('/download/<name>')
@auth.login_required
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


# List endpoint, get an HTML page listing all the uploaded files link
@app.route('/')
@auth.login_required
def list_files():
    files = get_list_of_img_path(path=app.config['UPLOAD_FOLDER'], reverse=True)
    images_url = []
    for file in files:
        images_url.append(urljoin(request.host_url, url_for('download_file', name=os.path.basename(file))))

    return render_template('imglist.html', images_url=images_url)


setup()
app.debug = False

if __name__ == '__main__':
    setup()
    app.debug = True
    app.run(host='0.0.0.0', port=5001)