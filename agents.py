# agents.py
from client import client
import json
import re
import os
from pathlib import Path

class Agent:
    def __init__(self, name, role, prompt, emoji):
        self.name = name
        self.role = role
        self.prompt = prompt
        self.emoji = emoji
    
    def think(self, task, context=""):
        system_instr = (
            f"{self.prompt}\n\nТвоя роль: {self.role}\n"
            f"ИНСТРУКЦИЯ ПО ФАЙЛАМ: Чтобы записать/создать файл, используй формат:\n"
            f"<write_file path=\"название_файла\">содержимое</write_file>\n"
            f"Пиши только по делу, без лишних извинений и вступлений."
        )
        messages = [
            {"role": "system", "content": system_instr},
            {"role": "user", "content": f"Контекст проекта:\n{context}\n\nЗАДАЧА:\n{task}"}
        ]
        print(f"\n{self.emoji} {self.name} работает...")
        return client.chat(messages, temperature=0.2)

class TeamAi:
    def __init__(self):
        self.agents = {
            "architect": Agent("Архитектор", "Lead Architect", "Проектируй структуру. Не пиши код, только план и список файлов.", "🏗️"),
            "coder": Agent("Кодер", "Senior Developer", "Пиши код. Используй <write_file>. Твой код должен быть готов к работе.", "💻"),
            "figura": Agent("Figura-Эксперт", "Compatibility Specialist", "Проверяй совместимость с Reign RP и figura-fix. Если есть ошибки — пиши BLOCK.", "🎩"),
            "reviewer": Agent("Критик", "Code Reviewer", "Ищи баги. НЕ ХВАЛИ КОД. Пиши BLOCK, если есть ошибки, или APPROVE.", "🔍"),
            "integrator": Agent("Интегратор", "Finalizer", "Проверяй целостность и делай финальный отчет.", "🧪")
        }

    def execute_file_ops(self, text):
        """Парсит теги и пишет файлы на диск"""
        write_pattern = re.compile(r'<write_file path="(.*?)">(.*?)</write_file>', re.DOTALL)
        ops = []
        for path_str, content in write_pattern.findall(text):
            try:
                path = Path(path_str.strip())
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content.strip())
                ops.append(f"✅ Файл обновлен: {path_str}")
            except Exception as e:
                ops.append(f"❌ Ошибка записи {path_str}: {e}")
        return ops

    def run_sequential(self, task, context=""):
        """Пошаговый запуск 5 агентов"""
        current_context = context
        history = []
        pipeline = ["architect", "coder", "figura", "reviewer", "integrator"]
        
        for name in pipeline:
            agent = self.agents[name]
            response = agent.think(task, current_context)
            ops = self.execute_file_ops(response)
            
            history.append({
                "agent": agent.name, "emoji": agent.emoji,
                "content": response, "ops": ops
            })
            current_context += f"\n\n--- {agent.name} ---\n{response}"
            
            if "BLOCK" in response and name in ["figura", "reviewer"]:
                print(f"🛑 Работа остановлена: {agent.name} нашел ошибку.")
                break
        return history
