import random as rd
from flask import request
from project import app
from project.models.log_error import constraint_error, method_error
from project.models.my_blog import *
from pyisemail import is_email

def check_methods(methods=None):
    if request.method not in methods:
        return method_error

# Du An
@app.route('/my_blog/du_an/get', methods=['GET'], endpoint=str(rd.getrandbits(128)))
def get_du_an():
    check_methods(['GET'])
    return DuAn().get()

@app.route('/my_blog/du_an/update_viewer', methods=['POST'], endpoint=str(rd.getrandbits(128)))
def update_viewer():
    check_methods(['POST'])
    oid = str(request.form.get('id')).lower().strip()
    return DuAn().update_viewer(oid)

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

# Ask Question
@app.route('/my_blog/ask_question/send', methods=['POST'], endpoint=str(rd.getrandbits(128)))
def send():
    check_methods(['POST'])
    name = str(request.form.get('name'))
    if len(name) > 50:
        return constraint_error('Tên không được vượt quá 50 kí tự !')
    email= str(request.form.get('email')).lower().strip()
    if len(email) > 75 or not is_email(email, check_dns=True):
        return constraint_error('Email phải ít hơn 75 kí tự & phải là một tên miền hợp lệ !')
    content = str(request.form.get('content'))
    if len(content) > 255:
        return constraint_error('Nội dung không được vượt quá 255 kí tự !')
    doc = {
        'name': name,
        'email': email,
        'content': content
    }
    return AskQuestion().add(doc)  
