Установка uv 

 pip install uv
  

Инициализация проекта

 uv init 
  

Создание виртуального окружения

 uv venv
  

Активировать виртуальное окружение

 source .venv/bin/activate # MacOS/Linux
 .venv\Scripts\activate.bat # Windows


Установить зависимости

  uv pip install -r <(uv pip compile pyproject.toml)


