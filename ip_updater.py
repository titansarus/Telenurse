import requests
import re
import time

cur_ip = None
domain = 'dynweb.duckdns.org'
token = 'ec7e753c-62c1-4a7f-aa28-dc5b032d80c3'
update_interval = 10 # in seconds

def send_dns_update_req():
    global cur_ip, domain, token
    httpr = None
    while True:
        params = {'domains': domain, 'token': token, 'ip': cur_ip, 'verbose': 'true'}
        httpr = requests.get('https://www.duckdns.org/update', params=params)
        res = httpr.text.split('\n')[0]
        if res == 'OK':
            break
        else:
            print('Resending update dns request')

def get_cur_ip():
    httpr = requests.get('https://ip4only.me/api/')
    new_ip = re.findall(r'((?:\d+\.){3}\d+)', httpr.text)[0]
    return new_ip

def main():
    global cur_ip, update_interval
    while True:
        new_ip = get_cur_ip()
        if cur_ip is None or cur_ip != new_ip:
            cur_ip = new_ip
            send_dns_update_req()
            print(f'CHANGED -> NEW-IP = {cur_ip}')
        else:
            print(f'NO CHANGE -> CUR-IP = {cur_ip}')
        time.sleep(update_interval)

if __name__ == '__main__':
    main()