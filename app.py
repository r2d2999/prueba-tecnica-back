from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import jsonify


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Task {self.title}>'

tables_created = False

@app.before_request
def before_request():
    global tables_created
    if not tables_created:
        db.create_all()
        tables_created = True
        

@app.route('/')
def hello_world():
    return 'conexión exitosa!'


@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": f"Task {id} has been deleted"}), 200




@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task_data = request.get_json()
    task.completed = task_data.get('completed', task.completed)
    db.session.commit()

    return jsonify({'id': task.id, 'title': task.title, 'description': task.description, 'completed': task.completed})



@app.route('/tasks', methods=['POST'])
def add_task():
    task_data = request.get_json()
    
    new_task = Task(
        title=task_data.get('title'),
        description=task_data.get('description'),
        completed=task_data.get('completed', False)
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return f'Task "{new_task.title}" added!'



@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()  
    return jsonify([{'id': task.id, 'title': task.title, 'description': task.description,
        'completed': task.completed} for task in tasks])


if __name__ == '__main__':
    app.run(debug=True)
