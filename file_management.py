import glob
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup(files, keep=500):
    removed_files = []
    for path in files[int(keep):]:
        try:
            os.remove(path)
            removed_files.append(path)
        except e:
            print(e)

    return removed_files

def get_list_of_img_path(path, reverse=False):
    files = []
        # Get a list of all files in the upload folder with allowed extension
    for types in ALLOWED_EXTENSIONS:
        paths = glob.glob(os.path.join(path, '*.{}'.format(types)))
        paths = [os.path.abspath(path) for path in paths]
        files.extend(paths)
    # Sort the files by their creation date
    files.sort(key=lambda x: os.path.getctime(x), reverse=reverse)
    return files