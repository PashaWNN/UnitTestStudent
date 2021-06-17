import subprocess
import json
import sys


def run_tests():
    failed = False
    subprocess.run(['chmod', '+x', 'solution'])
    with open('tests.json') as f:
        tests = json.loads(f.read())

    for i, test in enumerate(tests):
        print(f'====================\nRunning test #{i + 1}: {test["name"]}...')
        expected = test['expected_result']
        mode = test['mode']
        assert mode in ('contains', 'equals', 'regex'), 'Mode should be contains, equals or regex'
        strip = test['strip']
        assert strip is True or strip is False, 'strip should be True or False'
        result = subprocess.run(['./solution'], stdout=subprocess.PIPE, input=test['stdin'].encode('utf8'))
        stdout = result.stdout.decode('utf8')
        print("STDOUT:", stdout)
        if strip:
            stdout = stdout.strip()
        if mode == 'contains':
            passed = expected in stdout
        elif mode == 'equals':
            passed = stdout == expected
        elif mode == 'regex':
            passed = bool(re.match(expected, stdout))
        else:
            assert False, 'Unknown test mode'
        if passed:
            print('Test passed')
        else:
            print('Test failed')
            failed = True

    sys.exit(failed)


if __name__ == '__main__':
    run_tests()
