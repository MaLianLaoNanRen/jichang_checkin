import requests
import json
import os
import hashlib

url = os.environ.get('URL', 'https://t8.wj-kc.com').rstrip('/')
EMAIL = os.environ.get('EMAIL')
PASSWD = os.environ.get('PASSWD')
SCKEY = os.environ.get('SCKEY', '')

def md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def decode_response(res_text):
    """解析这个机场特殊的返回格式"""
    try:
        data = json.loads(res_text)
        if 'data' in data and isinstance(data['data'], str):
            import base64
            return json.loads(base64.b64decode(data['data']).decode())
        return data
    except Exception as e:
        print(f"解析响应失败: {e}")
        print(f"原始响应: {res_text}")
        return None

def sign():
    session = requests.Session()
    headers = {
        'Origin': url,
        'Referer': f'{url}/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
    }

    # 1. 登录
    print(f'=== 开始登录 ===')
    print(f'账号：{EMAIL}')
    login_data = {
        'email': EMAIL,
        'password': md5(PASSWD)
    }
    try:
        res = session.post(f'{url}/api/user/login', headers=headers, json=login_data, timeout=15)
        print(f'登录原始返回: {res.text}')
        result = decode_response(res.text)
        print(f'登录解析结果: {result}')

        if not result or result.get('code') != 0:
            msg = result.get('msg', '未知错误') if result else '解析失败'
            print(f'登录失败: {msg}')
            content = f'登录失败: {msg}'
        else:
            print('登录成功')
            # 2. 签到
            print('=== 开始签到 ===')
            res2 = session.post(f'{url}/api/user/sign_use', headers=headers, json={}, timeout=15)
            print(f'签到原始返回: {res2.text}')
            result2 = decode_response(res2.text)
            print(f'签到解析结果: {result2}')

            if result2 and result2.get('code') == 0:
                add_traffic = result2.get('data', {}).get('addTraffic', '未知')
                content = f'签到成功！获得流量: {add_traffic}'
                print(content)
            else:
                msg = result2.get('msg', '未知错误') if result2 else '解析失败'
                content = f'签到失败: {msg}'
                print(content)

    except Exception as ex:
        content = f'签到异常: {str(ex)}'
        print(content)

    # 推送
    if SCKEY:
        try:
            push_url = f'https://sctapi.ftqq.com/{SCKEY}.send'
            requests.post(push_url, data={'title': '机场签到', 'desp': content}, timeout=10)
            print('推送成功')
        except:
            print('推送失败')

    print('=== 签到结束 ===')

if __name__ == '__main__':
    if not EMAIL or not PASSWD:
        print('请配置 EMAIL 和 PASSWD')
        exit(1)
    sign()
