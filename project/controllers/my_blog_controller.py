from flask import request
from project import app
from project.models.my_blog import *

# Dự án
@app.route('/my_blog/du_an/get', methods=['GET'])
def blog_get_du_an():
    return DuAn().get()


@app.route('/my_blog/du_an/update_viewer', methods=['POST'])
def blog_update_viewer():
    oid = request.form.get('id')
    return DuAn().update_viewer(oid)

# Tien Ich
@app.route('/my_blog/tien_ich/get', methods=['GET'])
def blog_get_tien_ich():
    return TienIch().get()

# Personal Info
@app.route('/my_blog/personal_info/get', methods=['GET'])
def blog_get_info():
    return PersonalInfo().get()

# Ask Question
@app.route('/my_blog/ask_question/send', methods=['POST'])
def blog_send_question():
    name = request.form.get('name')
    email = request.form.get('email')
    content = request.form.get('content')
    return AskQuestion().add(name, email, content)
