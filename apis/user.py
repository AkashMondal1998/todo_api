from flask_restx import Namespace, fields, Resource
from flask import abort, jsonify
from .extensions import mysql, flask_brcypt
from flask_jwt_extended import create_access_token


api = Namespace("user", description="User operations")


login = api.model(
    "Login",
    {
        "username": fields.String(required=True, description="Username of the user"),
        "password": fields.String(required=True, description="Password of the user"),
    },
)

register = api.model(
    "Register",
    {
        "username": fields.String(
            required=True, max_length=20, description="Username of the user"
        ),
        "password": fields.String(required=True, description="Password of the user"),
        "con_password": fields.String(required=True, description="Confirm Password"),
        "role": fields.String(
            required=True, enum=["write", "read"], description="Role of the user"
        ),
    },
)


@api.route("/register")
class Resgiter(Resource):
    @api.expect(register, validate=True)
    def post(self):
        """User registration"""
        username = api.payload["username"]
        if not username:
            abort(400, "Username is required!")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user:
            abort(400, "Username already exists")
        password = api.payload["password"]
        if not password:
            abort(400, "Password is required!")
        con_password = api.payload["con_password"]
        if not con_password:
            abort(400, "Confirm Password is required!")
        role = api.payload["role"]
        if password != con_password:
            abort(400, "Password and Confirm Password are not same!")
        pass_hash = flask_brcypt.generate_password_hash(password).decode("utf-8")
        cur.execute(
            "INSERT INTO users(username,password,role) VALUES(%s,%s,%s)",
            (username, pass_hash, role),
        )
        mysql.connection.commit()
        return jsonify(message="Successfully registered!")


@api.route("/login")
class Login(Resource):
    @api.expect(login, validate=True)
    def post(self):
        """User login"""
        username = api.payload["username"]
        password = api.payload["password"]
        if not username or not password:
            abort(400, "Username or password is missing!")
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id,password,role FROM users WHERE username = %s", (username,)
        )
        user = cur.fetchone()
        if not user:
            abort(400, "Wrong username")
        if not flask_brcypt.check_password_hash(user["password"], password):
            abort(400, "Wrong password")
        role = {"role": user["role"]}
        user_id = user["id"]
        access_token = create_access_token(identity=user_id, additional_claims=role)
        return jsonify(access_token=access_token)
