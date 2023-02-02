# coding=utf-8
#该代码示例适用于Python3
import urllib
import urllib.request
import hashlib

def md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()
def SMS_send(name, elder_name):
    statusStr = {
        '0': '短信发送成功',
        '-1': '参数不全',
        '-2': '服务器空间不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间',
        '30': '密码错误',
        '40': '账号不存在',
        '41': '余额不足',
        '42': '账户已过期',
        '43': 'IP地址限制',
        '50': '内容含有敏感词'
    }

    smsapi = "http://api.smsbao.com/"
    # 短信平台账号
    user = 'ray009'
    # 短信平台密码
    password = md5('7373494259a')
    # 要发送的短信内容
    content = '【电易物联】尊敬的' + name+ '先生/女士，'+ elder_name +'今日心情并不愉悦，家中老人需要及时关爱，希望能够及时与老人沟通'
    # 要发送短信的手机号码
    phone = '18146600669'

    data = urllib.parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
    send_url = smsapi + 'sms?' + data
    response = urllib.request.urlopen(send_url)
    the_page = response.read().decode('utf-8')
    print (statusStr[the_page])

# SMS_send('郝', '郝小子')