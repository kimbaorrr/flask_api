import random as rd
from flask import request
from project import app
from project.models.log_error import method_error
from project.models.my_blog import DuAn, TienIch, PersonalInfo

def check_methods(methods=None):
    if request.method not in methods:
        return method_error()

# Du An
@app.route('/my_blog/du_an/get', methods=['GET'], endpoint=str(rd.getrandbits(128)))
def get_du_an():
    check_methods(['GET'])
    return DuAn().get()

@app.route('/my_blog/du_an/update_viewer', methods=['GET'], endpoint=str(rd.getrandbits(128)))
def update_viewer():
    check_methods(['GET'])
    oid = request.args.get('id').lower().strip()
    DuAn().update_viewer(oid)

# Tien Ich
@app.route('/my_blog/tien_ich/get', methods=['GET'], endpoint=str(rd.getrandbits(128)))
def get_tien_ich():
    check_methods(['GET'])
    return TienIch().get()

# Personal Info
@app.route('/my_blog/personal_info/get', methods=['GET'], endpoint=str(rd.getrandbits(128)))
def get_ttcn():
    check_methods(['GET'])
    return PersonalInfo().get()