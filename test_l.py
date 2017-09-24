from flask import *
from API import *
import json
app = Flask(__name__)

root_gitlab_token = auth_gitlab('root', 'jmXQF97J')

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/api/init_user', methods=['POST'])
def init_user():
    r = create_user(auth_nstu(request.form['username'],request.form['password']),request.form['vk_link'], root_gitlab_token)
    if r['message'] != None:
        return json.dumps({"succeed": False})
    else:
        return json.dumps({"succeed": True})

@app.route('/api/auth_admin', methods=['POST'])
def auth_admin():
    pass

if __name__ == '__main__':
    app.run(debug=True)
