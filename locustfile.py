import re
import os
import json
import time
import dotenv
import random
import urllib3
import xmltodict
from DataCaseParser import DataCaseFile
from urllib.parse import quote, unquote
from locust import HttpLocust, TaskSet, task

'''
    微信搜索压测试 
'''


class WeChatWidgetSearchTest(TaskSet):
    path = "/debug/cgi-bin/callbackagent"
    data = []
    isFine = 0
    file_cache = {}

    '''
        cookie 文件
    '''

    def cookie_params(self):
        cookies_file = self.current_dir() + os.getenv('TEST_COOKIES_FILE', "/config/cookies.json")
        jar = self.load_json_file(cookies_file)
        return jar

    '''
        头部参数
    '''

    def header_params(self):
        headers_file = self.current_dir() + os.getenv('TEST_HEADERS_FILE', "/config/header.json")
        headers = self.load_json_file(headers_file)
        return headers

    '''
          获取压测用例数据
    '''

    def get_data(self):
        if 0 != len(self.data):
            return self.data
        handler = DataCaseFile()
        file = self.current_dir() + os.getenv('TEST_CASES_FILE', "/config/data.case")
        param_file = self.current_dir() + os.getenv('TEST_PARAMS_FILE', "/config/params.json")
        params = self.load_json_file(param_file)
        data_list = handler.load(file)
        if data_list is None or not isinstance(params, dict):
            return []
        data = []
        var_case_key = os.getenv("DATA_CASE_VAR", '#data')
        cases = handler.list_case_scope(data_list, key=var_case_key)
        # print(cases)
        if 0 == len(cases):
            return []
        fill_case_param_key = os.getenv("FILL_CASE_PARAM_KEY", 'body')
        if not params.get(fill_case_param_key, False):
            return []
        template = str(params[fill_case_param_key])
        for i, val in enumerate(cases):
            item = params.copy()
            item[fill_case_param_key] = template.replace(var_case_key, val)
            data.append(item)
        self.data = data
        return data

    '''
      保存压测中的请求数据
    '''

    def save(self, data: str, index: int):
        storage_dir = '/' + os.getenv('TEST_STORAGE_DIR', 'storage') + '/'
        file = self.current_dir() + storage_dir + str(int(time.time())) + '_' + str(index) + '_'
        if len(data) == 0:
            print("error request test")
            return
        data_json = self.parse(data)
        if data_json is None:
            self.save_file(file + self.get_ext_html(), data)
            return
        obj = json.loads(data_json, encoding='utf-8')
        if obj is None:
            self.save_file(file + self.get_ext_json(), data_json)
            return
        xml_data = self.parse_xml(obj)
        if not xml_data:
            self.save_file(file + self.get_ext_json(), data_json)
            return
        xml_obj = xmltodict.parse(xml_data, encoding='utf-8')
        if isinstance(xml_obj, dict):
            if not xml_obj.get('xml', False):
                return
            el = xml_obj.get('xml')
            if not isinstance(el, dict) or not el.get('Content', False):
                return
            data = el['Content']
            self.save_file(file + "_query" + self.get_ext_json(), data)
        else:
            self.save_file(file + self.get_ext_xml(), xml_data)

    '''
           获取缓存数据
    '''

    def get_cache_file_content(self, file: str, expire=3600):
        cache = self.file_cache.get(file, False)
        if isinstance(cache, dict) and cache.get('content', False):
            now_time = int(time.time())
            cached_at = cache.get('cached_at', int(time.time()))
            if now_time - cached_at > expire:
                self.file_cache[file] = {}
                return None
            print('read in cache ' + file)
            return cache.get('content')
        else:
            return None

    '''
        通过json 文件加载 json 对象字典
    '''

    def load_json_file(self, file):
        cache = self.get_cache_file_content(file)
        if cache is not None:
            obj = json.loads(s=cache, encoding='utf-8')
            return obj
        if os.path.exists(file):
            fs = open(file=file, mode='r', encoding='utf-8')
            content = fs.read()
            fs.close()
            if 0 == len(content):
                return None
            self.file_cache[file] = {
                'content': content,
                'cached_at': int(time.time()),
            }
            obj = json.loads(s=content, encoding='utf-8')
            return obj
        else:
            return None

    def __del__(self):
        del self.file_cache, self.data

    @staticmethod
    def get_ext_html():
        return os.getenv('TEST_SAVE_HTML_EXT', '_res.html')

    @staticmethod
    def get_ext_json():
        return os.getenv('TEST_SAVE_JSON_EXT', '_res.json')

    @staticmethod
    def get_ext_xml():
        return os.getenv('TEST_SAVE_XML_EXT', '_res.xml')

    @staticmethod
    def save_file(file, data=None):
        if file is None or not isinstance(data, str) or 0 == len(data):
            return False
        fs = open(file, mode='w+', encoding='utf-8')
        fs.write(data)
        fs.close()
        return True

    '''
        解析结果xml数据
    '''

    @staticmethod
    def parse_xml(obj: dict):
        key = os.getenv("DATA_XML_KEY", "decrypt_xml")
        if not obj.get(key, False):
            return
        data = obj[key]
        xml_data = unquote(data)
        return xml_data

    @staticmethod
    def current_dir():
        cur = os.path.abspath(__file__)
        current_dir = os.path.dirname(cur)
        return current_dir

    '''
        解析html结果数据
    '''

    @staticmethod
    def parse(data):
        regexp = os.getenv("DATA_REGEXP", "resultData = (\{.+\})")
        match = re.search(regexp, data)
        if match:
            return match.group(1)
        return None

    '''
        压测接口[任务一]
    '''

    @task(1)
    def index(self):
        # env
        host = os.getenv('TEST_HOST_URL')
        host = quote(host)
        # case data
        data = self.get_data()
        count = len(data)
        # 随机抽取数据
        index = random.randint(0, count - 1)
        if 0 == count:
            print("error : empty data case")
            exit(-1)
        # fs = open(self.current_dir() + "/storage/data.json", mode='w+', encoding='utf-8')
        # json.dump(data, fs, ensure_ascii=False)
        # exit(1)
        data = data[index]
        # header
        header = self.header_params()
        # cookies load
        cookies = self.cookie_params()
        url = self.path + "?url=" + host
        # 请求
        req = self.client.post(url=url, data=data, json=False, headers=header, verify=False, cookies=cookies)
        if req.status_code == 200:
            print("ok")
            self.save(data=req.text, index=index)
        else:
            print("failed")


'''
 压测web server 启动类
'''


class WebsiteUser(HttpLocust):
    env_path = "/config/.env"
    task_set = WeChatWidgetSearchTest
    min_wait = 5000
    max_wait = 9000

    # 添加环境变量初始化
    def __init__(self):
        super().__init__()
        urllib3.disable_warnings()
        env_file = os.path.dirname(os.path.abspath(__file__)) + self.env_path
        dotenv.load_dotenv(env_file)
