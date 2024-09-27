import random as rd
from flask import request
from project import app
import project.models.prediction as pr
from project.models.log_error import method_error
import gc


def check_methods(methods=None):
    if request.method not in methods:
        return method_error()


@app.route('/ai/toxic_comments', methods=['GET', 'POST'], endpoint=str(rd.getrandbits(128)))
def toxic_comments():
    gc.collect()
    check_methods(['GET', 'POST'])
    input_text = str()
    match request.method:
        case "GET":
            input_text = request.args.get('text')
        case "POST":
            input_text = request.form.get('text')
    return pr.toxic_comments(input_text)


@app.route('/ai/chest_xray', methods=['POST'], endpoint=str(rd.getrandbits(128)))
def chest_xray():
    gc.collect()
    check_methods(['POST'])
    files = request.files.getlist('file')
    return pr.chest_xray(files)
