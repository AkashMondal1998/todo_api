from flask import request
from flask_restx import Resource, fields, Namespace, abort
from datetime import date
from .extensions import role_required, mysql


authorizations = {
    "jsonWebToken": {"type": "apiKey", "in": "header", "name": "Authorization"}
}

api = Namespace("todos", authorizations=authorizations, description="TODO operations")


todo = api.model(
    "Todo",
    {
        "id": fields.Integer(readonly=True, description="The task unique identifier"),
        "task": fields.String(required=True, description="The task details"),
        "due_date": fields.Date(required=True, description="The due date of the task"),
        "status": fields.String(readonly=True, description="The status of the task"),
    },
)


status = api.model(
    "Status",
    {
        "status": fields.String(
            required=True,
            enum=["Not started", "Finished", "In progress"],
            description="The updated status of the task",
        )
    },
)


@api.route("/")
class TodoList(Resource):
    """Shows a list of all todos, and lets you POST to add new tasks"""

    @api.doc(security="jsonWebToken")
    @api.marshal_list_with(todo)
    @role_required("read")
    def get(self):
        """List all tasks"""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        todos = cur.fetchall()
        return list(todos)

    @api.doc(security="jsonWebToken")
    @api.expect(todo, validate=True)
    @role_required("write")
    def post(self):
        """Create a new task"""
        task = api.payload["task"]
        if not todo:
            abort(400, "Task is required!")
        due_date = api.payload["due_date"]
        try:
            date.fromisoformat(due_date)
        except:
            abort(400, "Wrong date format!Accepted format YYYY-mm-dd")
        cur = cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO todos (task,due_date) VALUES(%s,%s)",
            (task, due_date),
        )
        mysql.connection.commit()
        return {"message": "Todo added successfully!"}, 201


@api.route("/<int:todo_id>")
class Todo(Resource):
    """Show a single todo item and lets you delete them and udpate the status"""

    @api.doc(security="jsonWebToken")
    @api.marshal_with(todo)
    @role_required("read")
    def get(self, todo_id):
        """Fetch a given task"""
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM todos WHERE id = %s",
            (todo_id,),
        )
        todo = cur.fetchone()
        if not todo:
            abort(404, "Todo not found")
        return todo

    @api.doc(security="jsonWebToken")
    @role_required("write")
    def delete(self, todo_id):
        """Delete a task given its identifier"""
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM todos WHERE id = %s",
            (todo_id,),
        )
        if cur.rowcount == 0:
            abort(400, "Todo Not found")
        mysql.connection.commit()
        return {"message": "Todo deleted"}, 200

    @api.doc(security="jsonWebToken")
    @api.expect(status, validate=True)
    @role_required("write")
    def put(self, todo_id):
        """Update a task given its identifier"""
        status = api.payload["status"]
        if not status:
            abort(400, "Status is required")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos WHERE id = %s", (todo_id,))
        todo = cur.fetchone()
        if not todo:
            abort(400, "Todo Not found!")
        cur.execute(
            "UPDATE todos SET status = %s WHERE id = %s",
            (status, todo_id),
        )
        if cur.rowcount == 0:
            abort(400, " You are setting the same status!")
        mysql.connection.commit()
        return {"message": "Todo updated"}, 200


@api.route("/finished")
class TodoFinished(Resource):
    @api.doc(security="jsonWebToken")
    @api.marshal_list_with(todo)
    @role_required("read")
    def get(self):
        """List of tasks that are finished"""
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos WHERE status = 'Finished'")
        todos = cur.fetchall()
        return list(todos)


@api.route("/overdue")
class TodoFinished(Resource):
    @api.doc(security="jsonWebToken")
    @api.marshal_list_with(todo)
    @role_required("read")
    def get(self):
        """List of tasks that are overdue"""
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM todos WHERE due_date < %s AND status != 'Finished'",
            (date.today().strftime("%Y-%m-%d"),),
        )
        todos = cur.fetchall()
        return list(todos)


@api.route("/due")
class TodoDue(Resource):
    @api.doc(security="jsonWebToken", params={"due_date": "date"})
    @api.marshal_list_with(todo)
    @role_required("read")
    def get(self):
        """List of tasks that are due on a particular date"""
        due_date = request.args.get("due_date")
        if not due_date:
            abort(400, "due_date required")
        try:
            date.fromisoformat(due_date)
        except:
            abort(400, "Wrong date format!Accepted format YYYY-dd-mm")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos WHERE due_date = %s", (due_date,))
        todos = cur.fetchall()
        return list(todos)
