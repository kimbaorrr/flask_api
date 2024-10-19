import json
import logging
from hashlib import sha3_512
from uuid import uuid4
from datetime import datetime
from project import app
from project.models.db import connect
from bson import ObjectId

logging.basicConfig(filename='flask_api.log',
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

@app.errorhandler(500)
def exception_error(message, data={}):
    return json.dumps({
        'code': 500,
        'message': message,
        'data': data
    }, ensure_ascii=False), 500


@app.errorhandler(403)
def unknown_error(message, data={}):
    return json.dumps({
        'code': 403,
        'message': message,
        'data': data
    }, ensure_ascii=False), 403


@app.errorhandler(405)
def user_is_not_valid(message, data={}):
    return json.dumps({
        'code': 405,
        'message': message,
        'data': data
    }, ensure_ascii=False), 405


def success_response(message, data={}):
    return json.dumps({
        'code': 200,
        'message': message,
        'data': data
    }, ensure_ascii=False, indent=4), 200


class Accounts():
    def __init__(self):
        self.accounts_collection = connect("zalo", "accounts")

    def hash_password(self, password):
        return sha3_512(password.encode('utf-8')).hexdigest()

    def get_one_by_token(self, token):
        return self.accounts_collection.find_one({'token': token})

    def get_accounts(self, token):
        if self.get_one_by_token(token):
            json_data = list(self.accounts_collection.find())
            return json.dumps(json_data, default=str, ensure_ascii=False, indent=4)

    def register(self, phone_number, password):
        try:
            if phone_number == password:
                return unknown_error('Số điện thoại và mật khẩu không được trùng nhau !')
            if len(phone_number) != 10 or not phone_number.startswith('0'):
                return unknown_error('Số điện thoại không hợp lệ !')
            if len(password) < 6:
                return unknown_error('Mật khẩu quá ngắn (tối thiểu 6 kí tự) !')

            password_hashed = self.hash_password(password)

            if self.accounts_collection.find_one({'phone_number': phone_number}):
                return unknown_error("Số điện thoại đã được đăng kí !")

            doc = {
                'phone_number': phone_number,
                'password': password_hashed,
                'avatar_link': 'assets/images/person.jpg',
                'blocked_ids': [],
                'user_name': phone_number,
                'avatar': -1,
                'token': str(uuid4())
            }
            self.accounts_collection.insert_one(doc)
            return json.dumps({'code': 200, 'message': 'Đăng kí thành công !', 'data': {}}, ensure_ascii=False, indent=4), 200
        except Exception as e:
            logging.error(
                f"Error in accounts.register: {str(e)}", exc_info=True)
            return exception_error(e)

    def login(self, phone_number, password):
        try:
            password_hashed = self.hash_password(password)
            doc = {
                'phone_number': phone_number,
                'password': password_hashed
            }
            query_data = self.accounts_collection.find_one(doc)
            if not query_data:
                return unknown_error('Số điện thoại chưa đăng kí hoặc mật khẩu không đúng !')

            output_data = {
                'id': str(query_data['_id']),
                'username': query_data['user_name'],
                'token': query_data['token'],
                'avatar': query_data['avatar'],
            }
            return success_response('Đăng nhập thành công !', output_data)
        except Exception as e:
            logging.error(
                f"Error in accounts.register: {str(e)}", exc_info=True)
            return exception_error(e)

    def logout(self, token):
        try:
            if not self.get_one_by_token(token):
                return unknown_error('Token không chính xác !')
            return success_response('Đăng xuất thành công !')
        except Exception as e:
            logging.error(
                f"Error in accounts.register: {str(e)}", exc_info=True)
            return exception_error(e)

    def update_password(self, token, old_password, new_password):
        pass


class Posts(Accounts):
    def __init__(self):
        super().__init__()
        self.posts_collection = connect("zalo", "posts")

    def add_post(self, token, image, video, content):
        try:
            if type(image) not in (list, tuple):
                return unknown_error('Image phải là một array !')
            if len(content) > 255:
                return unknown_error('Nội dung bài viết không được vượt quá 255 kí tự !')
            query_data = self.get_one_by_token(token)
            if not query_data:
                return unknown_error('Token không chính xác!')
            doc = {
                'post_owner_id': str(query_data['_id']),
                'post_content': content,
                'image': image if len(image) > 0 and video == '' else [],
                'video': video if len(image) == 0 else '',
                'comment_ids': [],
                'liked_user_ids': [],
                'created_at': str(datetime.now()),
                'modified_at': str(datetime.now()),
                'can_comment': True
            }
            _id = self.posts_collection.insert_one(doc)
            return success_response('Thêm bài viết thành công !', {'id': str(_id.inserted_id)})
        except Exception as e:
            logging.error(
                f"Error in accounts.register: {str(e)}", exc_info=True)
            return exception_error(e)

    def get_post(self, token, post_owner_id):
        try:
            if not self.get_one_by_token(token):
                return unknown_error('Token không chính xác!')

            account_query_data = self.accounts_collection.find_one(
                {'_id': ObjectId(post_owner_id)})
            post_query_data = self.posts_collection.find_one(
                {'post_owner_id': post_owner_id})
            if not post_query_data:
                return unknown_error('Bài viết không tồn tại !')

            output_data = {
                'id': str(post_query_data['_id']),
                'described': post_query_data['post_content'],
                'created': str(post_query_data['created_at']),
                'modified': str(post_query_data['modified_at']),
                'liked_user_ids': len(post_query_data['liked_user_ids']),
                'comment': len(post_query_data['comment_ids']),
                'is_liked': len(post_query_data['liked_user_ids']) > 0,
                'image': post_query_data['image'],
                'video': post_query_data['video'],
                'author': {
                    'id': str(post_query_data['post_owner_id']),
                    'name': account_query_data['user_name'],
                    'avatar': account_query_data['avatar']
                },
                'state': '',
                'is_blocked': False,
                'can_edit': post_owner_id == post_query_data['post_owner_id'] and post_query_data['can_comment'],
                'can_comment': post_query_data['can_comment']
            }
            return success_response('Lấy bài viết thành công !', output_data)
        except Exception as e:
            logging.error(
                f"Error in accounts.register: {str(e)}", exc_info=True)
            return exception_error(e)

    def get_list_posts(self, token, last_id=0, index=0, count=20):
    
        try:
            index = int(index)
            count = int(count)
            if not self.get_one_by_token(token):
                return unknown_error('Token không chính xác!')
            account_query_data = self.accounts_collection.find_one(
                {'token': token})
            post_owner_id = str(account_query_data['_id'])
            post_query_data = self.posts_collection.find({
                'post_owner_id': post_owner_id,
                # '_id': {'$gt': ObjectId(last_id)}
            }).skip(index).limit(count)
            if not post_query_data:
                return unknown_error('Không tìm thấy bất kỳ bài viết nào !')
            output_data = []
            for post in post_query_data:
                output_data.append({
                    'id': str(post['_id']),
                    'name': [],
                    'created': str(post['created_at']),
                    'liked': len(post['liked_user_ids']),
                    'comment': 0,
                    'is_liked': post_owner_id in post['liked_user_ids'],
                    'is_blocked': False,
                    'can_comment': post['can_comment'],
                    'can_edit': True,
                    'banned': False,
                    'state': '',
                    'author': {
                        'id': str(post['post_owner_id']),
                        'user_name': account_query_data['user_name'],
                        'avatar': account_query_data['avatar'],
                    },
                    'new_items': 10,
                    'last_id': last_id
                })
            return success_response('Lấy danh sách bài viết thành công !', output_data)
        except Exception as e:
            logging.error(
                f"Error in accounts.register: {str(e)}", exc_info=True)
            return exception_error(e)
    def edit_post(self, token, post_id, content):
        try:
            if not self.get_one_by_token(token):
                return unknown_error('Token không chính xác!')
            self.posts_collection.find_one_and_update(
                {'_id': ObjectId(post_id)},
                {'$set': {'post_content': content,'modified_at': str(datetime.now())}},
            )
            return success_response('Sửa bài viết thành công !')    
        except Exception as e:
            logging.error(
                f"Error in accounts.register: {str(e)}", exc_info=True)
            return exception_error(e)
        
    def delete_post(self, token, post_id):
        try:
            if not self.get_one_by_token(token):
                return unknown_error('Token không chính xác!')
            self.posts_collection.delete_one({'_id': ObjectId(post_id)})
            return success_response('Xóa bài viết thành công !')
        
        except Exception as e:
            logging.error(
                f"Error in accounts.register: {str(e)}", exc_info=True)
            return exception_error(e)