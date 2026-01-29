from flask import Flask, request, jsonify, abort
import subprocess
import os
import uuid

app = Flask(__name__)

tasks = []

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Todo API!",
        "endpoints": {
            "GET /tasks": "List all tasks",
            "POST /tasks": "Create a task",
            "GET /tasks/<task_id>": "Get a task",
           
        }
    })

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    if not request.json or 'title' not in request.json:
        abort(400, description="Missing 'title' in request body")
    task = {
        'id': str(uuid.uuid4()),
        'title': request.json['title'],
        'description': request.json.get('description', ''),
        'completed': False
    }
    tasks.append(task)
    return jsonify(task), 201

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        abort(404, description="Task not found")
    return jsonify(task)

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        abort(404, description="Task not found")
    if not request.json:
        abort(400, description="Invalid request body")
    task['title'] = request.json.get('title', task['title'])
    task['description'] = request.json.get('description', task['description'])
    task['completed'] = request.json.get('completed', task['completed'])
    return jsonify(task)

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({"message": "Task deleted"}), 200

@app.route('/ping')
def ping():
    target = request.args.get('target', '127.0.0.1')
    try:
        result = subprocess.run(
            ['ping', '-c', '1', target],
            capture_output=True, text=True, timeout=5, check=True
        )
        return jsonify({"result": result.stdout.strip()})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Ping timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "tasks_count": len(tasks)}), 200

@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(error):
    response = jsonify({"error": error.description})
    response.status_code = error.code
    return response

@app.route('/lookup')
def dns_lookup():
    hostname = request.args.get('hostname', '127.0.0.1')
    try:
        result = subprocess.run(
            ['nslookup', hostname],
            capture_output=True, text=True, timeout=5, check=True
        )
        return jsonify({"result": result.stdout.strip()})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "DNS lookup timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Permissions-Policy'] = 'interest-cohort=()'
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)