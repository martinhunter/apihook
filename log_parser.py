import re
# pattern should return (func, md5_params, result)
_pattern = re.compile(r'.*:end:\d+ - ([^\s]+) ([^\s]+) (.*)')


def parse_log(file, pattern=_pattern):
    with open(file, encoding='utf-8') as f:
        while True:
            line = f.readline()
            if not line:
                break
            matched = pattern.match(line)
            if matched:
                yield matched.groups()


def reduce_log(values):
    temp = {}
    for func, md5_params, result in values:
        if func not in temp:
            temp[func] = {}
        if md5_params not in temp[func]:
            temp[func][md5_params] = {result: 0}
        temp[func][md5_params][result] += 1
    return temp


def reduce_max_result(reduced: dict):
    for pairs in reduced.values():
        for md5_params, results in pairs.items():
            max_result = max(results, key=results.get)
            pairs[md5_params] = None if max_result == 'None' else max_result
    return reduced


def get_log_data(file, pattern=_pattern):
    return reduce_max_result(reduce_log(parse_log(file, pattern)))
