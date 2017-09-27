import requests,sys,uuid,pymysql

server_address = "http://192.168.0.79/api/v4/"
class DB:
    def get_mysql_connection(self):
        return pymysql.connect(host='192.168.0.79',
                        user='mynstu',
                        password='jmXQF97J%',
                        port=3306,
                        db='FastStart',
                        charset='utf8',
                        cursorclass=pymysql.cursors.DictCursor)

    def tokenExist(self, device_token):
        connection = self.get_mysql_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM tokens WHERE token = '%s'" % device_token)
                return len(cursor.fetchall()) > 0
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def getNewToken(self):
        temp = uuid.uuid4().hex
        while self.tokenExist(temp):
            temp = uuid.uuid4().hex
    def insertInDB(self,sql):
        connection = self.get_mysql_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()
    def selectInDB(self, sql):
        connection = self.get_mysql_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return list(cursor.fetchall())
        except Exception as e:
            print(e)
        finally:
            connection.close()

class Gitlab:
    root_gitlab_token = None
    DB = None
    def __init__(self):
        self.root_gitlab_token = 'R8FyHN5xkyy26zyQ-GR-'#self.auth_gitlab('root', 'jmXQF97J')
        self.DB = DB()

    def auth_gitlab(self,username, password):
        r = requests.post(server_address  + "session?login=%s&password=%s" % (username, password))
        print(r)
        if r.status_code == 201:
            print(r.content)
            self.root_gitlab_token = r.json()['private_token']
            print('AUTHED' + self.root_gitlab_token)
            return self.root_gitlab_token
        else:
            return None

    def auth_nstu(self,username, password):
        headers = {'Content-Type': 'application/json',
                   'X-OpenAM-Username': username,
                   'X-OpenAM-Password': password}
        r = requests.post('https://login.nstu.ru/ssoservice/json/authenticate', headers=headers)
        if r.status_code == 200:
            out_data = {'username': username, 'password': password}
            nstu_token = r.json()["tokenId"]
            r_fd = requests.get('https://api.ciu.nstu.ru/v1.0/data/simple/student',
                                cookies={'NstuSsoToken': nstu_token})
            if r_fd.status_code == 200:
                r_fd_json = None
                for d in r_fd.json():
                    if d['STATUS'] == 1:
                        r_fd_json = d
                        break
                if r_fd_json == None:
                    self.log_to_db('Error finding student info')
                    return None
                out_data.update({'name': "[%s] %s %s %s" %
                                         (r_fd_json['STUDY_GROUP'], r_fd_json['FAMILY_NAME'],
                                          r_fd_json['NAME'], r_fd_json['PATRONYMIC_NAME'])})
                out_data.update({"group": r_fd_json['STUDY_GROUP']})
                return out_data
            else:
                return None
        else:
            return None

    def get_users(self):
        while self.root_gitlab_token == None:
            self.root_gitlab_token = self.auth_gitlab('root','jmXQF97J')
            print('fucking repeat auth')

        print('get users')
        print('token ' + self.root_gitlab_token)
        r = requests.get(server_address  + 'users', headers={"PRIVATE-TOKEN": self.root_gitlab_token})
        return r.json()

    def create_user(self,auth_data, vk_link):
        r = requests.post(server_address  + 'users',
                          data={"email": auth_data['username'], "password": auth_data['password'],
                                "username": auth_data['username'].split('@')[0], "name": auth_data['name'],
                                "website_url": vk_link, 'skip_confirmation': True},
                          headers={"PRIVATE-TOKEN": self.root_gitlab_token})
        print(r.status_code)
        if r.status_code == 201:
            DB().insertInDB("INSERT INTO users(username,name) VALUES('%s','%s') " % (auth_data['username'], auth_data['name']))
            ll = self.list_lab()
            print(ll)
            if len(ll) > 0:
                for l in ll:
                    self.create_user_project(r.json()['id'], l['name'],l['description'])
        return r.json()

    def get_user_projects(self,user_id):
        r = requests.get(server_address  + 'users/%s/projects' % user_id, headers={"PRIVATE-TOKEN": self.root_gitlab_token})
        return r.json()
    def check_project_in_user(self,user_id, project_name):
        up = self.get_user_projects(user_id)
        for p in up:
            if p['name'] == project_name:
                return True
        return False
    def create_user_project(self,user_id, name, description):
        for p in self.get_user_projects(user_id):
            if p['name'] == name:
                return None
        print('create_user_project')
        r = requests.post(server_address  + 'projects/user/%s' % user_id,
                          data={"name": name, 'description': description},
                          headers={"PRIVATE-TOKEN": self.root_gitlab_token})
        return r.json()
    def create_lab(self, lab_name, lab_description):
        if len(DB().selectInDB("SELECT * FROM labs WHERE name = '%s'" % lab_name)) > 0:
            return {"succeed": False, "reason": "Уже есть такая лаба"}
        else:
            DB().insertInDB("INSERT INTO labs(name,description) VALUES('%s','%s') " % (lab_name,lab_description))
            gu = self.get_users()
            i = 0
            print(gu)
            for u in gu:
                print(u)
                if self.check_project_in_user(u['id'], lab_name) != True:
                    self.create_user_project(u['id'], lab_name, lab_description)
                self.log_to_db("%s/%s created lab" % (str(i),str(len(gu))))
                i += 1
            return {"succeed": True}
    def log_to_db(self,message):
        print(message)
        DB().insertInDB("INSERT INTO logs(message) VALUES('%s')" % message)
    def get_last_logs(self):
        return DB().selectInDB("SELECT * FROM logs ORDER BY ID DESC LIMIT 0,15")
    def list_lab(self):
        return DB().selectInDB("SELECT * FROM labs")
    def admin_auth(self,username,password):
        admin = DB().selectInDB("SELECT * FROM admins WHERE username = '%s' AND password = '%s'" % (username, password))

        if len(admin) > 0:
            DB().insertInDB("DELETE FROM tokens WHERE admin_id = %s" % admin[0]['id'])
            token = DB().getNewToken()
            DB().insertInDB("INSERT INTO tokens(token, admin_id) VALUES('%s',%s)" % (token, admin[0]['id']))
            return {"succeed" : True, 'token': token }
        else:
            return {"succeed": False, 'reason': 'Пользователь не прошел аутентификацию'}
    def admin_check_token(self,token):
        return DB().selectInDB("SELECT * FROM tokens WHERE token = '%s' " % token) > 0




if __name__ == '__main__':
    print(Gitlab().auth_gitlab('root','jmXQF97J'))
    pass
    # root_gitlab_token = auth_gitlab('root','jmXQF97J')
    # print(create_user_project(2,'Быстрый Старт.Лабораторная 2', 'В этой лабораторной необходимо выполнить ряд действий и тра та та' ,root_gitlab_token))