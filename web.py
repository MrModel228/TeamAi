# web.py
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from agents import TeamAi

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/run', methods=['POST'])
def run_task():
    data = request.json
    task = data.get('task', '')
    if not task:
        return jsonify({'error': 'Задача пуста'}), 400
    
    try:
        # Сбор контекста (сканируем папку проекта)
        context = "ТЕКУЩИЕ ФАЙЛЫ:\n"
        root = Path(__file__).parent
        for f in root.glob('**/*'):
            if f.is_file() and f.suffix in ['.py', '.js', '.json', '.html', '.txt']:
                if not any(x in str(f) for x in ['__pycache__', '.git', '.env']):
                    context += f"\n--- {f.name} ---\n{f.read_text(errors='ignore')[:1000]}\n"

        team = TeamAi()
        history = team.run_sequential(task, context[:30000]) # Лимит контекста
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
