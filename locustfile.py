import re
import os
import json
import time
import xmltodict
from urllib.parse import quote, unquote
from locust import HttpLocust, TaskSet, task

'''
    微信搜索压测试 
'''


class WeChatWidgetSearchTest(TaskSet):
    path = "/debug/cgi-bin/callbackagent"

    '''
      保存压测中的请求数据
    '''

    def save(self, data):
        file = self.current_dir() + '/storage/' + str(int(time.time()))
        if len(data) == 0:
            print("error request test")
            return
        self.save_file(file + "_res.html", data)
        data_json = self.parse(data)
        if data_json is None:
            return
        obj = json.loads(data_json, encoding='utf-8')
        self.save_file(file + "_res.json", data_json)
        if obj is None:
            return
        xml_data = self.parse_xml(obj)
        self.save_file(file + "_data.xml", xml_data)
        xml_obj = xmltodict.parse(xml_data, encoding='utf-8')
        print(xml_obj['xml']['Content'])

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
    def parse_xml(obj):
        if obj is None or not isinstance(obj, dict):
            return
        if obj['decrypt_xml'] is None or obj['decrypt_xml'] == "":
            return
        data = obj['decrypt_xml']
        xml_data = unquote(data)
        return xml_data

    @staticmethod
    def current_dir():
        cur = os.path.abspath(__file__)
        current_dir = os.path.dirname(cur)
        return current_dir

    '''
        cookie 文件
    '''

    def cookie_params(self):
        cookies_file = self.current_dir() + "/config/cookies.json"
        jar = self.load_json_file(cookies_file)
        return jar

    '''
        头部参数
    '''

    def header_params(self):
        headers_file = self.current_dir() + "/config/header.json"
        headers = self.load_json_file(headers_file)
        return headers

    '''
        通过json 文件加载 json 对象字典
    '''

    @staticmethod
    def load_json_file(file):
        if os.path.exists(file):
            fs = open(file=file, mode='r', encoding='utf-8')
            obj = json.load(fp=fs, encoding='utf-8')
            fs.close()
            return obj
        else:
            return None

    '''
        解析html结果数据
    '''

    @staticmethod
    def parse(data):
        regexp = 'resultData = (\{.+\})'
        match = re.search(regexp, data)
        if match:
            return match.group(1)
        return None

    '''
        获取压测用例数据
    '''

    def get_data(self):
        handler = DataCaseFile()
        file = self.current_dir() + "/config/data.case"
        param_file = self.current_dir() + "/config/params.json"
        params = self.load_json_file(param_file)
        data_list = handler.load(file)
        if data_list is None:
            return params
        data = []
        return data

    '''
        压测接口[任务一]
    '''

    @task(1)
    def index(self):
        # env
        host = quote("https://work-api.lieduoduo.com/wechat/mini/notify")
        # case data
        data = self.get_data()
        # header
        header = self.header_params()
        # cookies load
        cookies = self.cookie_params()
        url = self.path + "?url=" + host
        # 请求
        req = self.client.post(url=url, data=data, json=False, headers=header, verify=False, cookies=cookies)
        if req.status_code == 200:
            print("ok")
            self.save(data=req.text)
        else:
            print("failed")


'''
    测试数据加载类
'''


class DataCaseFile:
    start_flag = "["
    end_flag = "]"
    div_flag = ":"
    line_flag = r"\r\n"

    def load(self, file):
        if file is None or not isinstance(file, str) or 0 == len(file):
            return None
        fs = open(file=file, encoding='utf-8', mode='r')
        content = fs.read()
        if 0 == len(content):
            return
        lines = content.split(self.line_flag)
        return lines


'''
 压测web server 启动类
'''


class WebsiteUser(HttpLocust):
    task_set = WeChatWidgetSearchTest
    min_wait = 5000
    max_wait = 9000
