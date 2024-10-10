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
from project.models.log_error import constraint_error, system_error
import logging
import gc
from PIL import Image as pil

logging.basicConfig(filename='flask_api.log',
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def text_preprocessing(text):
    """
    Tiền xử lý chuỗi đầu vào
    Args:
        text (str): Chuỗi đầu vào

    Returns:
        str: Chuỗi đã qua tiền xử lý
    """
    # Chuyển đổi chữ thường
    text = text.lower()
    # Xóa tất cả các số có chữ cái gắn liền với chúng
    text = re.sub(r'\w*\d\w*', ' ', text)
    # Loại bỏ các tags
    text = strip_tags(text)
    # Loại bỏ các số
    text = strip_numeric(text)
    # Loại bỏ dấu câu
    text = strip_punctuation(text)
    # Loại bỏ kí tự xuống dòng
    text = re.sub("\n", " ", text)
    # Xóa kí tự không phải ascii
    text = strip_non_alphanum(text)
    # Loại bỏ các khoảng trắng thừa
    text = strip_multiple_whitespaces(text)
    return text


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
        if not file.filename.endswith(('.jpg', '.png', '.jpeg')):
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


def toxic_comments(input_text):
    """
    Dự án Phân tích văn bản độc hại

    Args:
        input_text (str): Chuỗi đầu vào cần dự đoán

    Returns:
        JSON: Có lỗi: Thông báo lỗi | Không lỗi: Kết quả dự đoán
    """
    try:
        model_path = 'project/ai_models/toxic_comment/'
        models_list = ['toxic', 'severe_toxic', 'obscene',
                       'insult', 'threat', 'identity_hate']
        models_data = {}
        results_data = {}

        # Nạp mô hình đã Train vào bộ nhớ
        for model in models_list:
            with open(os.path.join(model_path, f'{model}_model.pkl'), 'rb') as f:
                models_data[model] = pickle.load(f)
        for idx, value in models_data.items():
            model_name, model, tfv = idx, value[0], value[1]
            text_preprocessed = text_preprocessing(input_text)
            text_vectorized = tfv.transform([text_preprocessed])
            result = np.round(model.predict_proba(text_vectorized)[:, 1], 3)[0]
            results_data[model_name] = result
        del models_data
        gc.collect()
        return json.dumps(results_data, indent=4)
    except Exception as e:
        logging.error(f"Error in toxic_comments: {str(e)}", exc_info=True)
        return system_error()


def chest_xray(files):
    """
    Dự án Phân đoạn kết hợp phân lớp dự đoán khả năng bệnh phổi

    Args:
        files (list, tuple): Các tệp ảnh đã được upload

    Returns:
        JSON: Có lỗi: Thông báo lỗi | Không lỗi: Kết quả dự đoán
    """
    try:
        valid_files = check_files(files)
        if valid_files is not None:
            return valid_files
        results_data = []
        img_size = (224, 224)
        classes = ('normal', 'abnormal')
        model_path = 'project/ai_models/chest_xray/'
        custom_objects = {"iou_score": iou_score, "f1_score": f1_score}
        with custom_object_scope(custom_objects):
            model = load_model(os.path.join(model_path, 'best_model.keras'))
        images = [pil.open(file) for file in files]
        images = images_preprocessing(images, img_size)
        mask_results, cls_results = model.predict(images)
        for mask, cls in zip(mask_results, cls_results):
            mask_to_show = np.zeros(shape=(*img_size, 3), dtype=np.uint8)
            mask_to_show[..., 0] = 0  # R
            mask_to_show[..., 1] = mask.squeeze() * 255  # G
            mask_to_show[..., 2] = 255  # B
            top_label = classes[(cls >= .5).astype(int)[0]]
            bad_label = classes[(cls < .5).astype(int)[0]]
            top_acc = round(float(cls[0]), 3)
            bad_acc = round(float(1 - cls[0]), 3)
            _, buffer = cv.imencode('.png', mask_to_show)  # RGB => BGR
            mask_base64 = b64encode(buffer).decode('utf-8')
            base64_to_show = f"data:image/png;base64,{mask_base64}"
            results_data.append({
                'mask_base64': base64_to_show,
                'top_label': top_label,
                'top_acc': top_acc,
                'prob_cls': {
                    top_label: top_acc,
                    bad_label: bad_acc
                }
            })
        del images, mask_results, cls_results, buffer, mask_base64, base64_to_show
        gc.collect()
        return json.dumps(results_data, indent=4)
    except Exception as e:
        logging.error(f"Error in chest_xray: {str(e)}", exc_info=True)
        return system_error()
