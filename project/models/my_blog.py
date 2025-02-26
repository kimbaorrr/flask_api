import json
from project.models.db import connect
from bson.objectid import ObjectId
from project.models.common_handlers import *
import logging
from pyisemail import is_email
from datetime import datetime
from gensim.parsing.preprocessing import *

logging.basicConfig(filename='flask_api.log',
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class DuAn():
    def __init__(self):
        self.du_an_collection = connect('my_blog', "du_an")

    def get(self, current_page, limit):
        """Danh sách các dự án hiện có (có phân trang)

        Args:
            current_page (str): thứ tự trang hiện tại
            limit (str): giới hạn số đối tượng dữ liệu mỗi trang

        Returns:
            _type_: _description_
        """
        try:
            current_page = int(current_page)
            limit = int(limit)
            # Số đối tượng dữ liệu bị bỏ qua mỗi trang [page: 1, skip: 0, page: 2, skip:2-1 * limit]
            skip = int((current_page - 1) * limit)
            limited_projects = list(
                self.du_an_collection.find().skip(skip).limit(limit))
            # Đếm tổng dòng dữ liệu dự án hiện có trong DB
            total_projects = self.du_an_collection.count_documents({})
            # Tính số trang cần phân để phù hợp với tổng dòng dữ liệu hiện có
            total_pages = (total_projects // limit) + \
                (1 if total_projects % limit > 0 else 0)
            # Trả về dữ liệu danh sách dự án đã được phân theo trang
            output_data = {
                'limited_projects': limited_projects,
                'total_pages': total_pages,
                'current_page': current_page
            }
            return json.dumps(output_data, default=str, indent=4, ensure_ascii=False), 200

        except Exception as e:
            logging.error(
                f"Error in my_blog.DuAn: {str(e)}", exc_info=True)
            return system_error()

        return json_data

    def update_viewer(self, oid):
        """Cập nhật lượt click xem dự án

        Args:
            oid (str): id của dự án

        Returns:
            JSON: Trạng thái thực hiện
        """
        try:
            oid = str(oid).lower().replace(' ', '')
            # Kiểm tra ràng buộc dữ liệu
            if not ObjectId.is_valid(oid):
                return constraint_error('ID không tồn tại !')
            # Tăng lượt xem lên 1
            update_operation = {'$inc': {'viewer': 1}}
            # Cập nhật giá trị trong DB
            self.du_an_collection.update_one(
                {'_id': ObjectId(oid)}, update_operation)
            return success_response('Cập nhật lượt xem thành công !')
        except Exception as e:
            logging.error(
                f"Error in my_blog.DuAn: {str(e)}", exc_info=True)
            return system_error()


class TienIch():
    def __init__(self):
        self.tien_ich_collection = connect('my_blog', "tien_ich")

    def get(self):
        """Danh sách các tiện ích hiện có

        Returns:
            JSON: danh sách các tiện ích
        """
        tools = list(self.tien_ich_collection.find())
        return json.dumps(tools, default=str,
                          ensure_ascii=False, indent=4)


class PersonalInfo():
    def __init__(self):
        self.ttcn_collection = connect('my_blog', "personal_info")

    def get(self):
        json_data = [doc for doc in self.ttcn_collection.find()]
        json_data = json.dumps(json_data, default=str,
                               ensure_ascii=False, indent=4)
        return json_data


class AskQuestion():
    def __init__(self):
        self.ask_collection = connect('my_blog', "ask_question")

    def add(self, name, email, content):
        """Thêm mới một câu hỏi

        Args:
            name (str): Tên người dùng
            email (str): Địa chỉ email
            content (str): Nội dung cần hỏi

        Returns:
            JSON: Trạng thái gửi tới DB
        """
        try:
            name = strip_multiple_whitespaces(str(name).capitalize())
            email = str(email).lower().strip()
            content = strip_multiple_whitespaces(str(content))
            # Kiểm tra các ràng buộc dữ liệu
            if len(name) == 0 or len(name) > 50:
                return constraint_error('Tên không được để trống hoặc vượt quá 50 kí tự !')
            if len(email) == 0:
                return constraint_error('Email không được để trống !')
            if len(email) > 75 or not is_email(email, check_dns=True):
                return constraint_error('Email phải ít hơn 75 kí tự & phải là một tên miền hợp lệ !')
            if len(content) == 0 or len(content) > 255:
                return constraint_error('Nội dung không được để trống hoặc vượt quá 255 kí tự !')
            doc = {
                'name': name,
                'email': email,
                'content': content,
                'createdAt': datetime.now()
            }
            # Thêm một dòng mới trong DB
            self.ask_collection.insert_one(doc)
            return success_response('Thêm câu hỏi thành công !')
        except Exception as e:
            logging.error(
                f"Error in my_blog.AskQuestion: {str(e)}", exc_info=True)
            return system_error()
