from flask import *
from API import *
import json,pymysql
app = Flask(__name__)

root_gitlab_token = auth_gitlab('root', 'jmXQF97J')
def get_mysql_connection():
    return pymysql.connect(host="192.168.0.79",
                    user='mynstu',
                    password='jmXQF97J%',
                    db='mynstu',
                    charset='utf8',
                    cursorclass=pymysql.cursors.DictCursor)
@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/api/init_user', methods=['POST'])
def init_user():
    r = create_user(auth_nstu(request.form['username'],request.form['password']),request.form['vk_link'], root_gitlab_token)
    print(r)
    if 'message' in r:
        return json.dumps({"succeed": False, 'reason': 'exist'})
    else:
        return json.dumps({"succeed": True, 'username': r['username']})

@app.route('/api/auth_admin', methods=['POST'])
def auth_admin():
    pass

if __name__ == '__main__':
    print(get_mysql_connection())
    app.run(debug=True)
