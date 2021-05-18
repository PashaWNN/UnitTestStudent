# UnitTestStudent

Наконец-то он работает

## Как запустить

```shell script
docker compose up

# Создание администратора:
docker compose exec web python manage.py createsuperuser
# Следуйте инструкциям для создания администратора
```

Затем заходим на http://localhost:8080, логинимся под свежесозданным админом

Можем создать новую среду выполнения, написать произвольное название, описание и указать какой-то образ Docker. Например, `python:latest`
Образ **должен быть предварительно скачан** командой `docker run python:latest`

Также нужно указать команду для запуска и имена файлов. Для примера это могут быть `python -m unittest`, `main.py` & `tests.py` 

Затем уже можно создать задачу с использованием этой среды.

Например, задачей будет написать функцию `add`.
Тестовый файл может быть таким:
```python
import unittest
import main

class MainTestCase(unittest.TestCase):
    def adds_integers(self):
        result = main.add(2, 2)
        self.assertEqual(result, 4)

    def adds_negative(self):
        result = main.add(2, -2)
        self.assertEqual(result, 0)
```


После этого создаём нового пользователя в разделе "Пользователи" и обязательно отмечаем у него в профиле галочку "студент".

Логинимся под этим пользователем и можем загрузить решение, нажав на кнопку внизу страницы просмотра задачи.

Пример решения:
```python
def add(x, y):
  return x + y
```
