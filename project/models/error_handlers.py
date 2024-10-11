from project import app
import json


@app.errorhandler(400)
def constraint_error(message):
    return json.dumps({
        'code': 400,
        'message': message
    }, ensure_ascii=False), 400


@app.errorhandler(405)
def method_error():
    return json.dumps({
        'code': 405,
        'message': 'Phương thức không được phép !'
    }, ensure_ascii=False), 405
    
@app.errorhandler(500)
def system_error():
    return json.dumps({
        'code': 500,
        'message': 'Lỗi hệ thống. Thử lại !'
    }, ensure_ascii=False), 500
