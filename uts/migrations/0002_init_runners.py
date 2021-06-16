from django.db import migrations
from uts.models import Environment


def init_runners(apps, schema_editor):
    fixtures = [
        {
            "name": "Pure Python",
            "description": "Используется стандартный unittest. Импортировать решение из модуля main",
            "docker_image": "python:latest",
            "command": "python3 -m unittest tests",
            "tests_filename": "tests.py",
            "solution_filename": "main.py"
        },
        {
            "name": "C++ Google Test ZIPs",
            "description": "Среда выполнения для языка C++\r\n\r\nВходными файлами как для тестов, так и для решения должны быть ZIP-архивы с кодом.\r\nОсновной файл с кодом должен называться solution.cpp в корне архива, а основной файл тестов должен называться tests.cpp в корне архива.\r\nАрхивы распаковываются в /solution и /tests соответственно.\r\nАналогичная команда для компиляции локально: g++ tests/tests.cpp solution/solution.cpp -lgtest\r\n\r\nпример tests.cpp:\r\n\r\n#include \"gtest/gtest.h\"\r\n#include \"../solution/solution.h\"\r\n\r\nTEST(ExampleTests, MultiplyWorksOk)\r\n{\r\n    Calculator calc;\r\n\r\n    double result = calc.Multiply(4, 2);\r\n\r\n    ASSERT_EQ(8, result);\r\n}\r\n\r\nint main(int argc, char** argv)\r\n{\r\n    testing::InitGoogleTest(&argc, argv);\r\n\r\n    return RUN_ALL_TESTS();\r\n}",
            "docker_image": "coenvl/googletest",
            "command": "unzip solution.zip -oq && unzip tests.zip -oq && g++ tests/tests.cpp solution/solution.cpp -lgtest -o a.out && ./a.out",
            "tests_filename": "tests.zip",
            "solution_filename": "solution.zip"
        },
        {
            "name": "STD I/O",
            "description": "Среда выполнения, позволяющая тестировать любые бинарные и исполняемые файлы с помощью стандартного ввода/вывода\r\n\r\nФайл должен быть либо скомпилирован под Linux, либо быть валидным Unix-скриптом с \"магической строкой\", такой, как #!/usr/bin/python3 для скриптов на Python 3.\r\n\r\nФормат тестов — JSON-список, состоящий из объектов следующего вида:\r\n  {\r\n    \"expected_result\": \"False\",    #  Ожидаемый результат\r\n    \"mode\": \"contains\",  # contains, equals или regex\r\n    \"strip\": true,  # Обрезать ли из stdout пробелы и переносы строк по краям\r\n    \"name\": \"Basic test\",  # Название теста\r\n    \"stdin\": \"125\"  # Текст для стандартного ввода\r\n  }\r\n\r\nMode может принимать значения:\r\ncontains - проверка на то, что stdout содержит expected_result\r\nequals - проверка на то, что stdout идентичен expected_result\r\nregex - проверка на то, что stdout соответствует регулярному выражению",
            "docker_image": "prmn/plainrunner",
            "command": "python3 testrunner.py",
            "tests_filename": "tests.json",
            "solution_filename": "solution"
        }
    ]
    Environment.objects.bulk_create(Environment(**fixture) for fixture in fixtures)


class Migration(migrations.Migration):

    dependencies = [
        ('uts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_runners)
    ]
