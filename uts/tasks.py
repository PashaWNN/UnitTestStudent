import traceback

import epicbox
from celery import shared_task

from uts.models import Solution


@shared_task()
def run_solution(solution_id: int):
    solution = Solution.objects.get(pk=solution_id)
    solution.state = Solution.RUNNING
    solution.save()

    try:
        files = [
            {'name': solution.task.environment.solution_filename, 'content': solution.solution_file.read()},
            {'name': solution.task.environment.tests_filename, 'content': solution.task.tests_file.read()},
        ]
        limits = {
            'cputime': solution.task.cpu_limit,
            'realtime': solution.task.cpu_limit * 5,
            'memory': solution.task.memory_limit,
            'processes': 15,
        }
        epicbox.configure(
            profiles=[
                epicbox.Profile('main', solution.task.environment.docker_image, read_only=False, network_disabled=True)
            ]
        )
    except Exception as e:
        solution.log = 'Произошла ошибка при конфигурации среды выполнения:\n' + traceback.format_exc() + '\n' + str(e)
        solution.state = Solution.FAILED
        solution.save()
        return
    try:
        with epicbox.working_directory() as workdir:
            raw_report = epicbox.run(
                'main',
                solution.task.environment.command,
                files=files,
                limits=limits,
                workdir=workdir
            )
    except Exception as e:
        solution.log = 'Произошла ошибка среды выполнения при выполнении:\n' + traceback.format_exc() + '\n' + str(e)
        solution.state = Solution.FAILED
        solution.save()
        return

    solution.log = f'''
Тесты завершены, код ошибки: {raw_report['exit_code']}
Выполнение заняло {raw_report['duration']:.2f} секунд
{'Выполнение прервано по таймауту' if raw_report['timeout'] else ''}
{'Выполнение прервано по превышению лимита ОЗУ' if raw_report['oom_killed'] else ''}

Стандартный вывод:
{raw_report['stdout'].decode('utf8')}

stderr:
{raw_report['stderr'].decode('utf8')}
'''

    if any((raw_report['exit_code'], raw_report['timeout'], raw_report['oom_killed'])):
        solution.state = Solution.FAILED
    else:
        solution.state = Solution.COMPLETED
    solution.save()
