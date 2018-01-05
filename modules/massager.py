import db
import json
import time
import config

class Massager():
    def __init__(self,requests):
        self.db = db.DB()
        self.s = requests
    def get_msg(self, loginId):
        loginInfo = self.db.get_login_info_by_uuid(loginId)
        url = '%s/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (
        loginInfo['url'], loginInfo['wxsid'],
        loginInfo['skey'],loginInfo['pass_ticket'])
        data = {
            'BaseRequest' : loginInfo['BaseRequest'],
            'SyncKey'     : loginInfo['SyncKey'],
            'rr'          : ~int(time.time()), }
        headers = {
            'ContentType': 'application/json; charset=UTF-8',
            'User-Agent' : config.USER_AGENT }
        r = self.s.post(url, data=json.dumps(data), headers=headers, timeout=config.TIMEOUT)
        print r.content
        dic = json.loads(r.content.decode('utf-8', 'replace'))
        if dic['BaseResponse']['Ret'] != 0: return None, None
        loginInfo['SyncKey'] = dic['SyncCheckKey']
        loginInfo['synckey'] = '|'.join(['%s_%s' % (item['Key'], item['Val'])
            for item in dic['SyncCheckKey']['List']])
        return dic['AddMsgList'], dic['ModContactList']