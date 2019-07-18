import os
import re
from RedisHelp import RedisTool as Redis

'''
  测试用例加载器
'''


class DataCaseFile:
    start_flag = '['
    end_flag = ']'
    div_flag = ':'
    line_flag = r'\n|\r\n'
    cache_time = 3600

    def __init__(self):
        self.cache = Redis.instance()
        self.cache_time = int(os.getenv('DATA_CACHE_TIME', self.cache_time))

    def __del__(self):
        del self.cache

    '''
        加入数据
    '''

    def load(self, file=""):
        if 0 == len(file) or not os.path.exists(file):
            return None
        if os.path.exists(file + ".lock"):
            return None
        key = 'file_' + Redis.md5(file)
        data = self.cache.get(key)
        if data is not None:
            data = str(data.decode('utf-8'))
            lines = re.split(pattern=self.line_flag, string=data)
            del data
            return self.scope(lines)
        lock_key = key + "_lock"
        if self.cache.get(lock_key) is not None:
            return None
        self.cache.setex(name=lock_key, value=1, time=60)
        fs = open(file=file, encoding='utf-8', mode='r')
        lines = []
        while True:
            line = fs.readline()
            if not line:
                fs.close()
                break
            lines.append(line)
        if 0 == len(lines):
            return None
        self.cache.setex(name=key, value="\n".join(lines), time=self.cache_time)
        self.cache.delete(lock_key)
        return self.scope(lines)

    '''
        作用域处理
    '''

    def scope(self, lines: list):
        if len(lines) == 0:
            return lines
        ret = {}
        current_scope = "all"
        for index, value in enumerate(lines):
            if len(value) == 0:
                continue
            match = self.is_scope(value)
            # 添加 case
            if not match:
                ret = self.add_case(ret, current_scope, value)
                continue
            scope_var = match.group(1)
            scope_obj = self.scope_name(scope_var)
            # 解析 scope
            if isinstance(scope_obj, dict):
                next_scope = scope_obj.get('scope', current_scope)
                if next_scope == current_scope:
                    continue
                current_scope = next_scope
                self.init_scope(obj=ret, key=next_scope, parse=scope_obj.get('parse', 'txt'))
        return ret

    def is_scope(self, line):
        if line is None or not isinstance(line, str) or 0 == len(line):
            return False
        pattern = '^' + '\\' + self.start_flag + '(.+)' + '\\' + self.end_flag + '$'
        match = re.match(pattern=pattern, string=str(line))
        if match is None:
            return False
        return match

    def scope_name(self, scope_str: str):
        if len(scope_str) > 0:
            li = scope_str.split(self.div_flag)
            size = len(li)
            if 1 == size:
                return {"scope": scope_str}
            if 2 == size:
                return {"scope": li[0], "parser": li[1]}
            if size > 2:
                return {"scope": li[0], "parser": li[1], "matches": li}
        return None

    def add_case(self, obj: dict, key: str, case: str):
        if not obj.get(key, False):
            obj = self.init_scope(obj, key)
        obj[key]['cases'].append(case)
        return obj

    @staticmethod
    def init_scope(obj: dict, key: str, parse="txt"):
        obj[key] = {"cases": [], "parse": parse}
        return obj

    @staticmethod
    def list_case_scope(cases: dict, key: str):
        if not cases.get(key, False):
            return None
        data_obj = cases.get(key)
        if not isinstance(data_obj, dict) or not data_obj.get('cases', False):
            return None
        return data_obj.get('cases')
