from flask import request
from project import app
import project.models.prediction as pr
from project.models.error_handlers import constraint_error, method_error
import gc


def check_methods(methods=None):
    if request.method not in methods:
        return method_error()


@app.route('/ai/toxic_comments', methods=['GET', 'POST'])
def toxic_comments():
    gc.collect()
    check_methods(['GET', 'POST'])
    input_text = None
    match request.method:
        case "GET":
            input_text = str(request.args.get('text')).lower()
        case "POST":
            input_text = str(request.form.get('text')).lower()
    if len(input_text) == 0:
        return constraint_error('Chuỗi đầu vào không được để trống !')
    if len(input_text) > 255:
        return constraint_error('Chuỗi đầu vào không được vượt quá 255 kí tự !')    
    return pr.toxic_comments(input_text)


@app.route('/ai/chest_xray', methods=['POST'])
def chest_xray():
    gc.collect()
    check_methods(['POST'])
    files = request.files.getlist('file')
    return pr.chest_xray(files)
