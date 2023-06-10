from os import getenv
import logging
from requests import post


def request_bill(file_url: str) -> dict:
    data = {"token": getenv("PROVERKA_CHEKA_API_TOKEN"), "qrurl": file_url}
    ans = post("https://proverkacheka.com/api/v1/check/get", data=data)
    json = ans.json()
    if json.get("code") != 1:
        data["token"]=getenv("PROVERKA_CHEKA_API_TOKEN_RESERVE")
        ans = post("https://proverkacheka.com/api/v1/check/get", data=data)
        json = ans.json()
        if json.get("code") != 1:
            print(
                f"Unsuccessful API request, error_code={json.get('code')}\n"
                f"Data={json.get('data')},"
                f"request={ans.request.body}"
            )
            raise ValueError("Error while requesting bill")
    return json["data"]["json"]["items"]
