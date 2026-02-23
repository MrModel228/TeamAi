# run.py
import sys
import os
from pathlib import Path
from agents import TeamAi

def main():
    print("🚀 Запуск TeamAi: Прямой доступ к ПК")
    
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("📝 Что нужно сделать? ")
    if not task: return

    # Собираем дерево файлов для контекста
    context = "СТРУКТУРА ПРОЕКТА:\n"
    project_root = Path(__file__).parent
    
    for f in project_root.glob("**/*"):
        if f.is_file() and not any(p in str(f) for p in [".git", "__pycache__", ".teamAi", ".env"]):
            try:
                # Читаем только небольшие куски для экономии контекста
                rel_path = f.relative_to(project_root)
                content = f.read_text(encoding='utf-8')[:1500] 
                context += f"\nFILE: {rel_path}\n{content}\n"
            except: pass

    team = TeamAi()
    print("👥 Конвейер запущен...")
    team.run_sequential(task, context[:40000]) # Ограничиваем контекст 40к токенов
    print("\n✅ Готово! Проверь файлы в папке проекта.")

if __name__ == "__main__":
    main()