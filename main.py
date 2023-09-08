from flask import Flask
from flask import render_template, request
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    print (request.files)

    # upfileはcurlの場合
    # flutteもupfileにした
    # curl -X POST -F upfile=@/Users/shogohamada/github/genAI-image-backend/testenv/snowboard.png http://127.0.0.1:5000/upload

    # if 'upfile' not in request.files:
    #         return 'NO FILE'

    file = request.files['upfile']
    file.save(os.path.join('./static/image', 'test.png'))

    return 'OK'  
  else:
    return 'NG'

@app.route('/test', methods=['GET', 'POST'])
def upload_test():
  if request.method == 'POST':
    print (request.files))
    return 'OK'  
  else:
    return 'NG'

if __name__ == '__main__':
  app.run(debug=True)