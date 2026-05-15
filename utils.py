import requests

def replay(raw):
    # 快速解析
    lines = raw.strip().split('\n')
    method, path = lines[0].split()[:2]
    headers = dict([l.split(': ', 1) for l in lines[1:] if ': ' in l])
    host = headers.get('Host')
    url = f"https://{host}{path}" if host else path
    
    # 清理并发送
    clean = {k:v for k,v in headers.items() if k not in ['Host', 'Content-Length', 'Connection']}
    return requests.request(method, url, headers=clean, verify=True)
