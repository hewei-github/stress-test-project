import os
import json
from dotenv import load_dotenv
from DataCaseParser import DataCaseFile
from RedisHelp import RedisTool as Redis

'''
   好 案例 生成
'''


class GoodTestCase(object):
    is_good_key = 'test_finish'

    def __init__(self):
        super().__init__()
        self.cache = Redis.instance()
        self.is_good_key = os.getenv('TEST_GOOD_KEY', self.is_good_key)

    def get_good_cases(self):
        key = self.is_good_key
        val = self.cache.get(key)
        if val is None:
            return []
        lists = str(val.decode('utf-8')).split("\n")
        return lists

    @staticmethod
    def current_dir():
        return os.path.dirname(os.path.abspath(__file__))

    def get_all_cases(self):
        handler = DataCaseFile()
        file = self.current_dir() + os.getenv('TEST_CASES_FILE', "/config/data.case")
        data_list = handler.load(file)
        if data_list is None:
            return []
        var_case_key = os.getenv("DATA_CASE_VAR", '#data')
        cases = handler.list_case_scope(data_list, key=var_case_key)
        # print(cases)
        if 0 == len(cases):
            return []
        return cases

    '''
        过滤过多数据定位信息
    '''

    @staticmethod
    def good_case_filter(lists: list):
        ret = []
        for i, val in enumerate(lists):
            obj = json.loads(val, encoding='utf-8')
            item = obj.get('slot_list', [])
            print(item)
            if 0 == len(item):
                continue
            for j, it in enumerate(item):
                if not isinstance(it, dict) or not it.get('key', False):
                    continue
                if 'gps_city' != str(it.get('key')):
                    continue
                city = it.get('value', None)
                if city is None:
                    val = None
                    continue
                tmp = city.split('区', 2)
                if len(tmp) < 2:
                    continue
                city = tmp[0] + '区'
                tmp = city.split('省', 2)
                if len(tmp) >= 2:
                    city = tmp[1]
                tmp = city.split('市', 2)
                if len(tmp) >= 2:
                    city = tmp[1]
                print(city)
                it['value'] = city
                item[j] = it
            if val is None:
                continue
            obj['slot_list'] = item
            val = json.dumps(obj, ensure_ascii=False)
            ret.append(val)

        return ret

    def make_good_test_file(self, file: str):
        good = self.get_good_cases()
        cases = self.get_all_cases()
        ret = []
        count = len(cases)
        if len(good) == 0 and count >0:
            ret = cases
        for i, val in enumerate(good):
            val = int(val)
            if count > val >= 0:
                ret.append(cases[val])
        res = False
        ret = self.good_case_filter(ret)
        if len(ret) > 0:
            fs = open(file=file, mode='w+', encoding='utf-8')
            if fs is None:
                print("open file failed :" + file)
                return False
            txt = '[' + os.getenv('DATA_CASE_VAR', '#data') + ":json]\n"
            res = fs.write(txt + "\n".join(ret))
            fs.close()
        if res:
            return True
        return False


if __name__ == "__main__":
    cur_dir = GoodTestCase.current_dir()
    env_file = cur_dir + "/config/.env"
    load_dotenv(env_file)
    GoodTestCase().make_good_test_file(cur_dir + "/storage/data.good.case")
