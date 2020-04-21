from flask import Flask
from flask import request
from concurrent.futures import ThreadPoolExecutor
import requests
import time
import json
import re

# 搜索资源信息URL
XIAOXIAO_SEARCH_URL = 'http://fe2wzffedps4ejknbnnv.xiaoxiaoapps.com/search'
# 视频资源地址查询URL
XIAOXIAO_M3U8_QUERY = 'https://fe2wzffedps4ejknbnnv.xiaoxiaoapps.com/vod/reqplay/'

xxx_api_auth = '3037396564323935303466623161613564303436393964623735663338616163'

headers = {
        "Accept" : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "Upgrade-Insecure-Requests" : "1",
        "Accept-Language" : 'zh-cn',
        "Cookie" : ('xxx_api_auth=' + xxx_api_auth),
        "Host" : 'fe2wzffedps4ejknbnnv.xiaoxiaoapps.com',
        "User-Agent" : 'watemmeloncircle/2.1.5 (iPhone; iOS 13.3.1; Scale/2.00)',
}

# 创建线程池执行器
executor = ThreadPoolExecutor(2)

__all__ = ['app']
app = Flask(__name__)

@app.route('/')
def index():
    return 'XiaoXiao m3u8 Searcher. Please use /search?wd=名称'

@app.route('/search', methods=['GET', 'POST'])
def search():
    # 同步查询使用 GET
    if request.method == 'GET':
        searchword = request.args.get('wd', '')
        return requestXiaoXiaoSearchWithWd(searchword)
    # 异步查询使用 POST（接入微信个人号推送）
    else:
        data = request.form["json"]
        reSearch = re.search(r'\["(.*?)"\]', data).group(1)
        searchword = reSearch.encode('utf-8').decode('unicode_escape')
        searchword = searchword.replace('搜索', '')
        app.logger.warning("POST" + searchword)
        executor.submit(asyncRequestXiaoXiaoSearchWithWd, searchword)
        return "searching.."

# 异步查询视频资源信息
def asyncRequestXiaoXiaoSearchWithWd(wd):
    params = {
        '_t' : (int(time.time()) * 1000),
        'pid' : '',
        's_device_id' : '5C5E1143-A51A-4D9D-935A-00B663A01142',
        's_os_version' : '13.3.1',
        's_platform' : 'ios',
        'wd' : wd,
    }
    response = requests.get(XIAOXIAO_SEARCH_URL, headers=headers, params=params, verify=False)
    jsonDic = json.loads(response.text)
    resultArr = []
    for info in parseXiaoXiaoSearchWithResponse(jsonDic):
        m3u8url = requestM3U8WithInfo(info)
        resultArr.append({'名称' : info[1], '集数' : info[3], '播放地址' : m3u8url})
        app.logger.warning('名称: ' + info[1] + ' 集数: ' + info[3] + ' 播放地址: ' + m3u8url)
    if len(resultArr) > 0:
        data = {
            "text" : wd,
            'desp' : str(resultArr),
        }
        requests.post('https://sc.ftqq.com/SCU92977Ta943f796c0248f26c595e01585c6b30e5e8d16eeda6e0.send', data=data)
    else:
        data = {
            "text": wd,
            'desp': '无',
        }
        requests.post('https://sc.ftqq.com/SCU92977Ta943f796c0248f26c595e01585c6b30e5e8d16eeda6e0.send', data=data)

# 同步查询视频资源信息
def requestXiaoXiaoSearchWithWd(wd):
    params = {
        '_t' : (int(time.time()) * 1000),
        'pid' : '',
        's_device_id' : '5C5E1143-A51A-4D9D-935A-00B663A01142',
        's_os_version' : '13.3.1',
        's_platform' : 'ios',
        'wd' : wd,
    }
    response = requests.get(XIAOXIAO_SEARCH_URL, headers=headers, params=params, verify=False)
    jsonDic = json.loads(response.text)
    resultArr = []
    for info in parseXiaoXiaoSearchWithResponse(jsonDic):
        m3u8url = requestM3U8WithInfo(info)
        resultArr.append({'名称' : info[1], '集数' : info[3], '播放地址' : m3u8url})
        app.logger.warning('名称: ' + info[1] + ' 集数: ' + info[3] + ' 播放地址: ' + m3u8url)
    if len(resultArr) > 0:
        return str(resultArr)
    else:
        return "无搜索结果"

# 解析视频资源信息
def parseXiaoXiaoSearchWithResponse(jsonDic):
    try:
        data = jsonDic['data']
        vodrows = data['vodrows']
        for vodrow in vodrows:
            vodid = vodrow['vodid']
            title = vodrow['title']
            playlist = vodrow['playlist']
            for play in playlist:
                playindex = play['playindex']
                play_name = play['play_name']
                yield (vodid, title, str(playindex), play_name)
    except:
        return None
    return None

# 查询视频m3u8地址
def requestM3U8WithInfo(info):
    url = XIAOXIAO_M3U8_QUERY + info[0]
    params = {
        '_t': (int(time.time()) * 1000),
        'pid': '',
        'playindex' : info[2],
        's_device_id': '5C5E1143-A51A-4D9D-935A-00B663A01141',
        's_os_version': '13.3.1',
        's_platform': 'ios',
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    jsonDic = json.loads(response.text)
    return parseXiaoXiaoM3U8WithResponse(jsonDic)

# 解析获取视频m3u8地址
def parseXiaoXiaoM3U8WithResponse(jsonDic):
    try:
        data = jsonDic['data']
        retcode = jsonDic['retcode']
        httpurl = data['httpurl']
        return httpurl
    except:
        return str(retcode)
    return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0')