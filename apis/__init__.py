from flask_restx import Api
from .todo import api as ns1
from .user import api as ns2


api = Api(
    version="1.0",
    title="TodoMVC API",
    description="A simple TodoMVC API",
)

api.add_namespace(ns1)
api.add_namespace(ns2)
