import pydash
import requests
import config
import time, re
class LoginInfoHandler():
    def loginInfoValidation(self, loginInfo):
        # login info should contain at least the following to make it work:
        username = pydash.get(loginInfo, 'User.UserName', default=False)
        url = pydash.get(loginInfo, 'url', default=False)
        cookieJar = pydash.get(loginInfo, 'cookieJar', default=False)
        if username and url and cookieJar:
            return True
        else:
            return False

    def check_login_only(self, uuid=None):
        uuid = uuid or self.uuid
        url = '%s/cgi-bin/mmwebwx-bin/login' % config.BASE_URL
        localTime = int(time.time())
        params = 'loginicon=true&uuid=%s&tip=1&r=%s&_=%s' % (
            uuid, int(-localTime / 1579), localTime)
        headers = { 'User-Agent' : config.USER_AGENT }
        r = requests.get(url, params=params, headers=headers)
        regx = r'window.code=(\d+)'
        data = re.search(regx, r.text)
        if data and data.group(1) == '200':
            return '200'
        elif data:
            return data.group(1)
        else:
            return '400'