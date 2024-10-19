from datetime import datetime
from flask import request
from project import app
from project.models.zalo import *
from pyisemail import is_email
from gensim.parsing.preprocessing import *

# Accounts
@app.route('/zalo/accounts/login', methods=['POST'])
def zalo_login():
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    return Accounts().login(phone_number, password)

@app.route('/zalo/accounts/register', methods=['POST'])
def zalo_register():
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    return Accounts().register(phone_number, password)


@app.route('/zalo/accounts/logout', methods=['POST'])
def zalo_logout():
    token = request.form.get('token')
    return Accounts().logout(token)

# Posts
@app.route('/zalo/posts/add_post', methods=['POST'])
def zalo_add_post():
    token = request.form.get('token')
    image = request.form.getlist('image')
    content = request.form.get('described')
    video = request.form.get('video')
    return Posts().add_post(token, image, video, content)

@app.route('/zalo/posts/get_post', methods=['POST'])
def zalo_get_post():
    token = request.form.get('token')
    post_owner_id = request.form.get('post_owner_id')
    return Posts().get_post(token, post_owner_id)

@app.route('/zalo/posts/get_list_posts', methods=['POST'])
def zalo_get_list_posts():
    token = request.form.get('token')
    last_id = request.form.get('last_id')
    index = request.form.get('index')
    count = request.form.get('count')
    return Posts().get_list_posts(token, last_id, index, count)

@app.route('/zalo/posts/edit_post', methods=['POST'])
def zalo_edit_post():
    token = request.form.get('token')
    post_id = request.form.get('id')
    content = request.form.get('described')
    return Posts().edit_post(token, post_id, content)

@app.route('/zalo/posts/delete_post', methods=['POST'])
def zalo_delete_post():
    token = request.form.get('token')
    post_id = request.form.get('post_id')
    return Posts().delete_post(token, post_id)

