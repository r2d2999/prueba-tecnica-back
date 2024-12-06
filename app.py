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
        

# Ruta principal
@app.route('/')
def hello_world():
    return 'conexión exitosa!'



# Ruta para eliminar una tarea
@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    # Buscar la tarea por su ID
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Eliminar la tarea de la base de datos
    db.session.delete(task)
    db.session.commit()

    # Devolver una respuesta de éxito
    return jsonify({"message": f"Task {id} has been deleted"}), 200




# Ruta para actualizar el estado de una tarea
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    # Obtener la tarea por ID
    task = Task.query.get(id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Obtener los datos del JSON enviados para actualizar la tarea
    task_data = request.get_json()

    # Actualizar los valores de la tarea
    task.completed = task_data.get('completed', task.completed)

    # Guardar los cambios en la base de datos
    db.session.commit()

    return jsonify({'id': task.id, 'title': task.title, 'description': task.description, 'completed': task.completed})



# Ruta para agregar una nueva tarea
@app.route('/tasks', methods=['POST'])
def add_task():
    # Obtener los datos del formulario
    task_data = request.get_json()
    
    # Crear una nueva tarea con los datos del JSON
    new_task = Task(
        title=task_data.get('title'),
        description=task_data.get('description'),
        completed=task_data.get('completed', False)
    )
    
    # Agregar la tarea a la base de datos
    db.session.add(new_task)
    db.session.commit()
    
    return f'Task "{new_task.title}" added!'



@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()  # Recupera todas las tareas de la base de datos
    # Devuelve las tareas como un arreglo de diccionarios en formato JSON
    return jsonify([{'id': task.id, 'title': task.title, 'description': task.description,
        'completed': task.completed} for task in tasks])


if __name__ == '__main__':
    app.run(debug=True)
