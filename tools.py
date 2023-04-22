from os import getenv
import logging
from requests import post

def request_bill(qrraw: str):
    data = {}
    for i in qrraw.split('&'):
        data[i.split('=')[0]] = i.split('=')[1]
    data['token'] = getenv('PROVERKA_CHEKA_API_TOKEN')
    data['qr'] = 0
    ans = post('https://proverkacheka.com/api/v1/check/get', post)
    logging.log(logging.INFO, ans)
    logging.log(logging.INFO, ans.text.encode())
    ans = ans.json()

    logging.log(logging.INFO, ans)
    return ans








