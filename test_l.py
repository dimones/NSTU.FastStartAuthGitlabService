from flask import *
from API import *
import json,pymysql
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/admin')
def admin():
    if 'token' not in request.cookies:
        redirect(init_user)
    g = Gitlab()
    return render_template('admin_index.html', labs=g.list_lab(), logs = g.get_last_logs())

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

@app.route('/api/admin/get_labs', methods=['GET'])
def get_users():
    d = """{% for d in labs %}
                <tr>
                  <th scope="row">{{ d.id }}</th>
                  <td>{{ d.name }}</td>
                  <td>{{ d.description }}</td>
                </tr>
                {% endfor %}"""
    return render_template_string(d, labs=Gitlab().list_lab())

@app.route('/api/admin/get_logs', methods=['GET'])
def get_logs():
    d = """{% for d in logs %}
                <tr>
                  <th scope="row">{{ d.id }}</th>
                  <td>{{ d.message }}</td>
                </tr>
                {% endfor %}"""
    return render_template_string(d, logs=Gitlab().get_last_logs())

@app.route('/api/admin/add_lab', methods=['POST'])
def add_lab():
    return json.dumps(Gitlab().create_lab(request.form['lab_name'],request.form['lab_description']))
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
