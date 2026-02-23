# agents.py
from client import client
import json
import re

class Agent:
    def __init__(self, name, role, prompt, emoji):
        self.name = name
        self.role = role
        self.prompt = prompt
        self.emoji = emoji
    
    def think(self, task, context=""):
        """Мыслительный процесс агента"""
        messages = [
            {"role": "system", "content": f"{self.prompt}\n\nРоль: {self.role}"},
            {"role": "user", "content": f"Контекст:\n{context}\n\nЗАДАЧА:\n{task}"}
        ]
        print(f"\n{self.emoji} {self.name} работает...")
        return client.chat(messages)


class TeamAi:
    def __init__(self):
        self.agents = {
            "orchestrator": Agent(
                "Оркестратор", "Team Lead / Координатор",
                """Ты руководитель AI-команды. Твоя задача:
                1. Проанализировать задачу пользователя
                2. ОПРЕДЕЛИТЬ каких агентов нужно подключить
                3. Распределить работу между ними
                4. Свести всё в единый ответ
                
                ВАЖНО: В начале ответа напиши JSON со списком агентов:
                {"agents": ["coder", "reviewer"]}
                
                Доступные агенты: coder, reviewer, tester, documenter
                Тебя (orchestrator) всегда подключать не нужно — ты уже работаешь.
                
                Примеры:
                - "Напиши функцию" → coder
                - "Проверь код" → reviewer
                - "Создай тесты" → tester
                - "Напиши документацию" → documenter
                - "Сделай полный цикл" → coder, reviewer, tester, documenter
                
                Будь экономным — подключай только необходимых агентов.""",
                "🎯"
            ),
            "coder": Agent(
                "Кодер", "Senior Developer",
                """Ты опытный разработчик. Твоя задача:
                1. Писать чистый, рабочий код
                2. Следовать best practices
                3. Добавлять комментарии
                4. Использовать современные подходы
                
                Пиши только код и минимальные пояснения.""",
                "💻"
            ),
            "reviewer": Agent(
                "Критик", "Senior Code Reviewer",
                "Ты — злой и дотошный ревьюер. НЕ ХВАЛИ КОД. Ищи баги, уязвимости и нарушения логики. "
                "Выдавай только два статуса: APPROVE или BLOCK с аргументами.", "🔍"
            ),
            "tester": Agent(
                "Тестировщик", "QA Engineer",
                """Ты тестировщик. Твоя задача:
                1. Писать unit-тесты
                2. Находить edge cases
                3. Проверять покрытие кода
                4. Создавать интеграционные тесты
                
                Думай как пользователь, который хочет сломать код.""",
                "🧪"
            ),
            "documenter": Agent(
                "Документатор", "Technical Writer",
                """Ты технический писатель. Твоя задача:
                1. Писать README и документацию
                2. Создавать комментарии в коде
                3. Делать инструкции по установке
                4. Описывать API endpoints
                
                Пиши понятно для новичков.""",
                "📝"
            )
        }
    
    def parse_agents_from_response(self, response):
        """Извлечь список агентов из ответа оркестратора"""
        json_match = re.search(r'\{[^}]*"agents"[^}]*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                agents_list = data.get("agents", [])
                clean_response = response.replace(json_match.group(), "").strip()
                return agents_list, clean_response
            except json.JSONDecodeError:
                pass
        
        # Если JSON не найден, пытаемся найти имена агентов в тексте
        agent_names = []
        response_lower = response.lower()
        if "coder" in response_lower:
            agent_names.append("coder")
        if "reviewer" in response_lower:
            agent_names.append("reviewer")
        if "tester" in response_lower:
            agent_names.append("tester")
        if "documenter" in response_lower:
            agent_names.append("documenter")
        
        return agent_names, response
    
    def run(self, task, agents_list=None, context=""):
        """Ручной выбор агентов (для run.py)"""
        if agents_list is None:
            agents_list = ["orchestrator", "coder", "reviewer"]
        
        results = {}
        current_context = context
        
        for agent_name in agents_list:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                result = agent.think(task, current_context)
                results[agent_name] = result
                current_context += f"\n\n{agent_name}: {result}"
        
        return results
    
    def execute_smart(self, task, context=""):
        """Умное выполнение — оркестратор сам выбирает агентов (для web.py)"""
        print("\n🎯 Оркестратор анализирует задачу...")
        orchestrator_response = self.agents["orchestrator"].think(task, context)
        
        selected_agents, clean_response = self.parse_agents_from_response(orchestrator_response)
        
        if not selected_agents:
            selected_agents = ["coder", "reviewer"]
            print("⚠️ Оркестратор не указал агентов, подключаем: coder, reviewer")
        else:
            print(f"✅ Оркестратор выбрал агентов: {', '.join(selected_agents)}")
        
        results = {
            "orchestrator": {
                "content": clean_response,
                "selected_agents": selected_agents
            }
        }
        
        current_context = context + f"\n\nПлан от оркестратора:\n{clean_response}"
        
        for agent_name in selected_agents:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                result = agent.think(task, current_context)
                results[agent_name] = {"content": result}
                current_context += f"\n\n{agent_name}: {result}"
        
        return results