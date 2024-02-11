from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from flask_mysqldb import MySQL
from flask import abort
from functools import wraps
from flask_bcrypt import Bcrypt


mysql = MySQL()
jwt = JWTManager()
flask_brcypt = Bcrypt()


def role_required(role):
    def outer_wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if role == "read":
                return f(*args, **kwargs)
            else:
                user_role = get_jwt()["role"]
                if role != user_role:
                    abort(401, "You do not have access to this!")
                return f(*args, **kwargs)

        return inner_wrapper

    return outer_wrapper
