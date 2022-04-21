import requests
import sys
import os
from urllib.parse import urljoin
from dotenv import load_dotenv

def call_cleanup(keep=500):
    load_dotenv()
    usernamme = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    server = os.getenv('SERVER')
    try:
        response = requests.post(urljoin(server, '/cleanup/'), json={'keep': keep}, auth=(usernamme, password))
    except Exception as e:
        return {'error': str(e)}
    
    return response.json()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if int(sys.argv[1]) >= 0:
            print(sys.argv[1])
            print(call_cleanup(keep=int(sys.argv[1])))
    else:
        print(call_cleanup())