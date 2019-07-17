import os
import re


def current_dir():
    current_file = os.path.abspath(__file__)
    _dir = os.path.dirname(current_file)
    return _dir


def load(file: str, distinct=True):
    if not os.path.exists(file):
        return []
    fs = open(file, encoding='utf-8', mode='r')
    row_lines = fs.read()
    fs.close()
    lines = re.split(r'\n|\r\n', row_lines)
    if distinct:
        return filter(lines)
    return lines


def filters(lines: list):
    if 0 == len(lines):
        return lines
    ret = []
    for i, line in enumerate(lines):
        match = re.match('.+(市|区)', line)
        if match is None:
            continue
        tmp = line.split('区', 2)
        if not isinstance(tmp, list):
            continue
        item = tmp[0] + '区'
        if item in ret:
            continue
        ret.append(item)
    return ret


def save(file: str, data: list):
    if 0 == len(data):
        return False
    fs = open(file=file, mode='w+', encoding='utf-8')
    txt = "\n".join(data)
    ret = fs.write(txt)
    fs.close()
    if ret > 0:
        return True
    return False


if __name__ == "__main__":
    curr_dir = current_dir()
    source_file = curr_dir + r"\source.txt"
    address_list = load(source_file)
    save(file=current_dir + r'\address.txt', data=address_list)
