# coding=utf-8
# encoding:utf-8

import sys
import json
import base64
import time

from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode

timer = time.perf_counter

API_KEY = 'uRNQA5QtznDHGwQRTNWe6wVT'  # Rain的账号，后期请替换为自己的
SECRET_KEY = '0kPfGQ0dgPf7SoGMIVW8xGqwXAG9SDT0'

# 需要识别的文件
AUDIO_FILE = 'voice.wav'  # 只支持 pcm/wav/amr 格式
# 文件格式
FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式

CUID = '123456PYTHON'
# 采样率
RATE = 16000  # API规定的固定值

# 普通版

DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
ASR_URL = 'http://vop.baidu.com/server_api'
SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有
NLP_URL = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify'


class DemoError(Exception):
    pass


"""  TOKEN start """

TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'  # 获取token的链接


def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    result_str = result_str.decode()

    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        print(SCOPE)
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


"""  TOKEN end """

def voice_API():
    token = fetch_token()

    speech_data = []
    with open(AUDIO_FILE, 'rb') as speech_file:  # 读入语音文件
        speech_data = speech_file.read()

    length = len(speech_data)
    if length == 0:
        raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
    speech = base64.b64encode(speech_data)
    speech = str(speech, 'utf-8')
    params = {'dev_pid': DEV_PID,
              # "lm_id" : LM_ID,    #测试自训练平台开启此项
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
    post_data = json.dumps(params, sort_keys=False)
    # print post_data
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        begin = timer()
        f = urlopen(req)
        result_str = f.read()
        print("Request time cost %f" % (timer() - begin))
    except URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()
    result_str = str(result_str, 'utf-8')
    print(result_str)
    with open("result.txt", "w") as of:
        of.write(result_str)

    host = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token=' + token
    try:
        params = {
            'text': json.loads(result_str)["result"][0],
        }
    except:
        return '0', '0'

    post_data = json.dumps(params, sort_keys=False)
    # print post_data
    req = Request(host, post_data.encode('UTF-8'))
    req.add_header('Content-Type', 'application/json')
    begin = timer()
    # print(str(req.header_items()))
    f = urlopen(req)
    result_str2 = f.read()
    print(result_str2.decode('UTF-8'))
    dict = json.loads(result_str2.decode('UTF-8'))
    print("Request time cost %f" % (timer() - begin))
    return dict['text'], dict['items']

if __name__ == '__main__':  # 主函数
    voice_API()