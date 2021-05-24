from flask import jsonify


def get_status():
    return jsonify(dict(
        status='ok'
    ))