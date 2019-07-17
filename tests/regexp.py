import re
import os
import json
import xmltodict
from urllib.parse import unquote


# from xml.dom import minidom


def test_regexp():
    pattern = r'.{1,}resultData = (\{.{1,}\})'
    file = "../storage/1563251793_res.html"
    fs = open(file=file, mode='r+', encoding='utf-8')
    data = fs.read()
    print("data:", data)
    match = re.match(pattern, data, re.M | re.I)
    print(match)
    fs.close()


def test_json():
    # obj.decrypt_xml
    cur = os.path.abspath(__file__)
    current_dir = os.path.dirname(cur)
    file = os.path.dirname(current_dir) + "/storage/1563257555_res.json"
    # print(file)
    fs = open(file, mode="r", encoding='utf-8')
    json_data = fs.read()
    obj = json.loads(s=json_data, encoding='utf-8')
    if obj['decrypt_xml'] is None or obj['decrypt_xml'] == "":
        return
    data = obj['decrypt_xml']
    # print(data)
    xml_data = unquote(data)
    xml_obj = xmltodict.parse(xml_data, encoding='utf-8')
    print(xml_obj['xml']['MsgType'])
    print(xml_obj['xml']['Content'])
    # print(xml_data)
    # xml_obj = minidom.parseString(xml_data)
    # if xml_obj.childNodes.length < 1:
    #     return
    # items = xml_obj.childNodes[0]
    # if isinstance(items, minidom.Element):
    #     for item in items.childNodes:
    #         if isinstance(item, minidom.Element):
    #             print(item.childNodes[0])
    # print('end')
    # obj = xml_obj
    # print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))
    # for key in xml_obj:
    #    print("key", xml_obj[key])


if __name__ == "__main__":
    test_json()
