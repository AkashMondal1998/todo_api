from flask import Flask
from apis import api
from apis.extensions import jwt, mysql, flask_brcypt

app = Flask(__name__)

app.config["MYSQL_USER"] = "akash"
app.config["MYSQL_PASSWORD"] = "akash"
app.config["MYSQL_DB"] = "Todo"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["JWT_SECRET_KEY"] = "416fc5da3ec05694b2d2ebf8ea6a604f"


jwt.__init__(app)
api.init_app(app)
mysql.init_app(app)
flask_brcypt.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
