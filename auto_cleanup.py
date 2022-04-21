from file_management import get_list_of_img_path, cleanup
from dotenv import load_dotenv
import sys
import os

def auto_cleanup(keep=500):
    load_dotenv()
    path = os.getenv('UPLOAD_FOLDER', '/var/img')
    files = get_list_of_img_path(path)
    removed_files = cleanup(files, keep)
    return removed_files


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if int(sys.argv[1]) >= 0:
            removed_files = auto_cleanup(keep=int(sys.argv[1]))
    else:
        removed_files = auto_cleanup()
    
    for file in removed_files:
        print('{} deleted'.format(file))

