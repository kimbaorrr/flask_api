import pickle
from gensim.parsing.preprocessing import *
import os
import re
import numpy as np
import json
from base64 import b64encode
from project.models.custom_metrics import iou_score, f1_score
from keras.src.saving import load_model, custom_object_scope
import cv2 as cv
from project.models.common_handlers import constraint_error, system_error
import logging
import gc
from PIL import Image as pil

logging.basicConfig(filename='flask_api.log',
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def check_files(files):
    """
    Kiểm tra các tệp upload
    Args:
        files (list): Danh sách các tệp đã upload

    Returns:
        None: Không có lỗi
        JSON: Có lỗi. Trả về kèm thông báo lỗi
    """
    if not files or len(files) == 0:
        return constraint_error('Bạn chưa upload bất kì tệp nào !')
    for file in files:
        if not file.filename.endswith(('.jpg', '.png', '.jpeg', '.bmp', '.webp')):
            return constraint_error('Định dạng tệp không hỗ trợ !')
        if not file.content_type.startswith('image/'):
            return constraint_error('Nội dung tệp không phải là một ảnh !')
    return None


def images_preprocessing(images, img_size):
    """
    Tiền xử lý các ảnh đầu vào

    Args:
        images (list, tuple): Danh sách các ảnh đầu vào
        img_size (list, tuple): Kích thước ảnh đầu ra

    Returns:
        ndarray: Mảng numpy chứa các ảnh đã được tiền xử lý.
        Đầu ra là mảng numpy 4 chiều dạng (Batch_size, Width, Height, Channel)
    """
    new_images = []
    for image in images:
        image = image.resize((img_size))
        image = image.convert('RGB')
        image = np.array(image)
        new_images.append(image)
    new_images = np.asarray(new_images, dtype=np.uint8)
    new_images = new_images / 255.
    if new_images.ndim == 3:
        new_images = np.expand_dims(new_images, axis=0)
        return new_images
    elif new_images.ndim == 4:
        return new_images
    else:
        Exception('Mảng numpy không hợp lệ !')


class ToxicComments:
    def __init__(self, input_text):
        """
        Dự án Phân tích văn bản độc hại

        Args:
            input_text (str): Chuỗi đầu vào cần dự đoán

        Returns:
            JSON: Có lỗi: Thông báo lỗi | Không lỗi: Kết quả dự đoán
        """
        self.input_text = str(input_text)
        # Kiểm tra ràng buộc về chuỗi
        if len(self.input_text) == 0:
            return constraint_error('Chuỗi đầu vào không được để trống !')
        if len(self.input_text) > 255:
            return constraint_error('Chuỗi đầu vào không được vượt quá 255 kí tự !')
        # Bắt đầu tiền xử lý chuỗi trước khi dự đoán
        self.text_preprocessing()

    def run(self):
        # Thêm các biến cần thiết
        model_path = 'project/ai_models/toxic_comment/'
        models_list = ('toxic', 'severe_toxic', 'obscene',
                       'insult', 'threat', 'identity_hate')
        models_data = {}
        results_data = {}
        try:
            # Nạp các mô hình đã Train vào bộ nhớ
            for model in models_list:
                with open(os.path.join(model_path, f'{model}_model.pkl'), 'rb') as f:
                    models_data[model] = pickle.load(f)
            # Dự đoán chuỗi trên từng mô hình
            for idx, value in models_data.items():
                model_name, model, tfv = idx, value[0], value[1]
                # Chuyển đổi sang cấu trúc giống với ma trận tập Train
                input_text_vectorized = tfv.transform([self.input_text])
                # Lấy 3 chữ số thập phân từ giá trị dự đoán
                result = np.round(model.predict_proba(
                    input_text_vectorized)[:, 1], 3)[0]
                # Thêm kết quả dự đoán vào dict sao cho ứng với tên từng mô hình
                results_data[model_name] = result
            # Xóa các biến không còn sử dụng
            del models_data
            gc.collect()
            return json.dumps(results_data, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error in toxic_comments: {str(e)}", exc_info=True)
            return system_error()

    def text_preprocessing(self):
        """
        Tiền xử lý chuỗi đầu vào
        Args:
            text (str): Chuỗi đầu vào

        Returns:
            str: Chuỗi đã qua tiền xử lý
        """
        # Chuyển đổi chữ thường
        self.input_text = self.input_text.lower()
        # Xóa tất cả các số có chữ cái gắn liền với chúng
        self.input_text = re.sub(r'\w*\d\w*', ' ', self.input_text)
        # Loại bỏ các tags
        self.input_text = strip_tags(self.input_text)
        # Loại bỏ các số
        self.input_text = strip_numeric(self.input_text)
        # Loại bỏ dấu câu
        self.input_text = strip_punctuation(self.input_text)
        # Loại bỏ kí tự xuống dòng
        self.input_text = re.sub("\n", " ", self.input_text)
        # Xóa kí tự không phải ascii
        self.input_text = strip_non_alphanum(self.input_text)
        # Loại bỏ các khoảng trắng thừa
        self.input_text = strip_multiple_whitespaces(self.input_text)


class ChestXray:
    def __init__(self, files):
        self.files = files
        # Kiểm tra các ràng buộc dữ liệu
        is_valid_files = check_files(self.files)
        if is_valid_files is not None:
            return is_valid_files

    def run(self):
        """
        Dự án Phân đoạn kết hợp phân lớp dự đoán khả năng bệnh phổi

        Args:
            files (list, tuple): Các tệp ảnh đã được upload

        Returns:
            JSON: Có lỗi: Thông báo lỗi | Không lỗi: Kết quả dự đoán
        """
        try:

            # Thiết lập các biến cần thiết
            model_path = 'project/ai_models/chest_xray/'
            classes = ('normal', 'abnormal')
            img_size = (224, 224)
            custom_objects = {"iou_score": iou_score, "f1_score": f1_score}
            # Load mô hình và thêm các custom metrics
            with custom_object_scope(custom_objects):
                model = load_model(os.path.join(
                    model_path, 'best_model.keras'))
            # Đọc các tệp ảnh
            images = [pil.open(file) for file in self.files]
            # Tiền xử lý các ảnh
            images = images_preprocessing(images, img_size)
            # Dự đoán các dữ liệu ảnh & xuất kết quả là các mặt nạ RGB & xác xuất thuộc về 2 lớp bình thường|bất thường
            mask_results, cls_results = model.predict(images)
            for mask, cls in zip(mask_results, cls_results):
                # Tạo ma trận 3 chiều tương ứng 3 màu RGB & giới hạn giá trị ở 255
                mask_to_show = np.zeros(shape=(*img_size, 3), dtype=np.uint8)
                # Gán dữ liệu dự đoán được cho từng kênh R: không có màu, G: vị trí phổi, B: (background)
                mask_to_show[..., 0] = 0  # R
                mask_to_show[..., 1] = mask.squeeze() * 255  # G
                mask_to_show[..., 2] = 255  # B
                # Gán các nhãn tương ứng với xác xuất từng lớp
                top_label = classes[(cls >= .5).astype(int)[0]]
                bad_label = classes[(cls < .5).astype(int)[0]]
                top_acc = round(float(cls[0]), 3)
                bad_acc = round(float(1 - cls[0]), 3)
                # Encode mask dưới dạng một ảnh png (sau khi encode màu sẽ bị đổi vị trí RGB->BGR)
                _, buffer = cv.imencode('.png', mask_to_show)  # RGB => BGR
                # Chuyển đổi ảnh png thành chuỗi base64
                mask_base64 = b64encode(buffer).decode('utf-8')
                # Thêm trường data:... để trình duyệt có thể hiển thị
                base64_to_show = f"data:image/png;base64,{mask_base64}"
                results_data = {
                    'mask_base64': base64_to_show,
                    'top_label': top_label,
                    'top_acc': top_acc,
                    'prob_cls': {
                        top_label: top_acc,
                        bad_label: bad_acc
                    }
                }
            # Xóa các biến không còn sử dụng
            del images, mask_results, cls_results, buffer, mask_base64, base64_to_show
            gc.collect()
            return json.dumps(results_data, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error in chest_xray: {str(e)}", exc_info=True)
            return system_error()
