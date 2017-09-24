import requests
def auth_gitlab(username,password):
    #curl --request POST "http://10.211.55.4/api/v4/session?login=root&password=jmXQF97J"
    r = requests.post("http://10.211.55.4/api/v4/session?login=%s&password=%s"% (username,password))
    if r.status_code == 201:
        return r.json()['private_token']
    else:
        return None

def auth_nstu(username, password):
    headers = {'Content-Type': 'application/json',
               'X-OpenAM-Username': username,
               'X-OpenAM-Password': password}
    r = requests.post('https://login.nstu.ru/ssoservice/json/authenticate', headers=headers)
    if r.status_code == 200:
        out_data = {'username' : username, 'password' : password}
        nstu_token = r.json()["tokenId"]
        r_fd = requests.get('https://api.ciu.nstu.ru/v1.0/data/simple/student',
                     cookies={'NstuSsoToken': nstu_token })
        if r_fd.status_code == 200:
            r_fd_json = None
            for d in r_fd.json():
                if d['STATUS'] == 1:
                    r_fd_json = d
                    break
            if r_fd_json == None:
                print('Error finding student info')
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

def get_users(token):
    r = requests.get('http://10.211.55.4/api/v4/users',headers = {"PRIVATE-TOKEN": token})
    return r.json()
def create_user(auth_data, vk_link, token):
    r = requests.post('http://10.211.55.4/api/v4/users',
                      data= {"email": auth_data['username'], "password": auth_data['password'],
                             "username": auth_data['username'].split('@')[0], "name": auth_data['name'], "website_url": vk_link},
                      headers = {"PRIVATE-TOKEN": token})
    return r.json()

def get_user_projects(user_id,token):
    r = requests.get('http://10.211.55.4/api/v4/users/%s/projects' % user_id, headers={"PRIVATE-TOKEN": token})
    return r.json()

def create_user_project(user_id, name, description, token):
    for p in get_user_projects(user_id,token):
        if p['name'] == name:
            return None
    r = requests.post('http://10.211.55.4/api/v4/projects/user/%s' % user_id,
                      data={"name": name, 'description': description },
                      headers={"PRIVATE-TOKEN": token})
    return r.json()

if __name__ == '__main__':
    root_gitlab_token = auth_gitlab('root','jmXQF97J')
    print(create_user_project(2,'Быстрый Старт.Лабораторная 2', 'В этой лабораторной необходимо выполнить ряд действий и тра та та' ,root_gitlab_token))