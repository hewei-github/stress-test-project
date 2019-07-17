import os
import json
import dotenv

'''
  测试用例数据生成
'''


class DataSeeder:
    max_len = 3000
    env_file = "/config/.env"
    data_save_file_key = 'TEST_CASES_FILE'
    data_file_env_key = "TEST_SOURCE_DATA_FILE"
    data_job_keys = ['gps_city', 'job_name']
    data_company_keys = ['gps_city', 'company_name']
    data_save_template = {"type": 0, "slot_list": []}

    def __init__(self):
        env_file = self.curr_dir() + self.env_file
        if not os.path.exists(env_file):
            return
        dotenv.load_dotenv(env_file)
        self.max_len = os.getenv('DATA_MAX_CASE_MAX_LEN', self.max_len)
        self.data_save_template['type'] = os.getenv('DATA_SEARCH_TYPE', 0)

    def get_data(self):
        data_file = self.curr_dir() + os.getenv(self.data_file_env_key)
        fs = open(data_file, mode='r', encoding='utf-8')
        obj = json.load(fp=fs, encoding='utf-8')
        return obj

    @staticmethod
    def curr_dir():
        curr_file = os.path.abspath(__file__)
        return os.path.dirname(curr_file)

    def load(self):
        row = self.get_data()
        if not isinstance(row, dict):
            return None
        data_list = row.get('data', False)
        if not data_list:
            return None
        return data_list

    def save(self, row_list: list):
        if len(row_list) == 0:
            return False
        txt = '[' + os.getenv('DATA_CASE_VAR', '#data') + ":json]\n"
        for i, val in enumerate(row_list):
            if not isinstance(val, dict):
                continue
            slot_list = []
            item = self.data_save_template
            for k, v in val.items():
                value = {"key": k, "value": v}
                slot_list.append(value)
            if len(slot_list) == 0:
                continue
            item['slot_list'] = slot_list
            tmp = json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n"
            txt = txt + tmp
        if len(txt) == 0:
            return False
        # 保存文件
        save_file = self.curr_dir() + os.getenv(self.data_save_file_key, '/config/test.case')
        print(save_file)
        fs = open(file=save_file, encoding='utf-8', mode='w+')
        ret = fs.write(txt)
        fs.close()
        return ret

    # 生成测试种子
    def seeder(self):
        lists = self.load()
        if not isinstance(lists, list):
            return []
        jobs = self.seeder_search_by_job(lists)
        companies = self.seeder_search_by_company(lists)
        return jobs + companies

    def seeder_search_by_company(self, row_data: list):
        if 0 == len(row_data):
            return []
        ret = self.seeder_handler(row_data, self.data_company_keys)
        return ret

    def seeder_search_by_job(self, row_data: list):
        if 0 == len(row_data):
            return []
        ret = self.seeder_handler(row_data, self.data_job_keys)
        return ret

    @staticmethod
    def seeder_handler(data_list: list, keys: list):
        ret = []
        for i, val in enumerate(data_list):
            if not isinstance(val, dict):
                continue
            item = {}
            for j, key in enumerate(keys):
                if not val.get(key, False):
                    continue
                item[key] = val.get(key)
            ret.append(item)
        return ret


if __name__ == '__main__':
    loader = DataSeeder()
    data = loader.seeder()
    loader.save(data)
