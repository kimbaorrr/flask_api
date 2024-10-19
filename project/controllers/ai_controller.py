from flask import request
from project import app
from project.models.ai import *

@app.route('/ai/toxic_comments', methods=['GET', 'POST'])
def ai_toxic_comments():
    match request.method:
        case "GET":
            input_text = request.args.get('text')
        case "POST":
            input_text = request.form.get('text')
    return ToxicComments(input_text).run()


@app.route('/ai/chest_xray', methods=['POST'])
def ai_chest_xray():
    files = request.files.getlist('file')
    return ChestXray(files).run()
