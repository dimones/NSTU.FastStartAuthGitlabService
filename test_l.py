from flask import *
from API import *
import json,pymysql
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/api/init_user', methods=['POST'])
def init_user():
    g = Gitlab()
    r = g.create_user(g.auth_nstu(request.form['username'],request.form['password']),request.form['vk_link'])
    print(r)
    if 'message' in r:
        return json.dumps({"succeed": False, 'reason': 'exist'})
    else:
        return json.dumps({"succeed": True, 'username': r['username']})

@app.route('/api/auth_admin', methods=['POST'])
def auth_admin():
    return json.dumps(Gitlab().admin_auth(request.form['username'],request.form['password']))

@app.route('/api/admin/get_labs', methods=['POST'])
def get_users():
    if 'token' not in 

if __name__ == '__main__':
    app.run(debug=True)
