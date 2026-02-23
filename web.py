from flask import Flask, render_template, request, jsonify
from agents import TeamAi
from pathlib import Path
import os

app = Flask(__name__)
team = TeamAi()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run', methods=['POST'])
def run():
    task = request.json.get('task')
    # Собираем контекст из текущей папки
    context = "Файлы в проекте:\n"
    for f in Path('.').glob('*'):
        if f.is_file() and f.suffix in ['.py', '.js', '.json', '.html']:
            context += f"\n--- {f.name} ---\n{f.read_text()[:500]}\n"
            
    history = team.run_step_by_step(task, context)
    return jsonify({"history": history})

if __name__ == '__main__':
    app.run(debug=True, port=5000)