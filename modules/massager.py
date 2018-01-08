import json
import time
import config
import itchats


class Massager():
    def __init__(self, requests, db):
        # requires requests and costomized db
        self.db = db
        self.s = requests

    def get_msg(self, loginId):
        loginInfo = self.db.get_login_info_by_uuid(loginId)
        url = '%s/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (
            loginInfo['url'], loginInfo['wxsid'], loginInfo['skey'],
            loginInfo['pass_ticket'])
        data = {
            'BaseRequest': loginInfo['BaseRequest'],
            'SyncKey': loginInfo['SyncKey'],
            'rr': ~int(time.time()),
        }
        headers = {
            'ContentType': 'application/json; charset=UTF-8',
            'User-Agent': config.USER_AGENT
        }
        r = self.s.post(
            url,
            data=json.dumps(data),
            headers=headers,
            timeout=config.TIMEOUT)
        dic = json.loads(r.content.decode('utf-8', 'replace'))
        if dic['BaseResponse']['Ret'] != 0: return None, None
        loginInfo['SyncKey'] = dic['SyncCheckKey']
        loginInfo['synckey'] = '|'.join([
            '%s_%s' % (item['Key'], item['Val'])
            for item in dic['SyncCheckKey']['List']
        ])
        updateLoginInfo = self.db.update_login_info(loginInfo)
        saveMsg = self.db.save_list_of_msg(dic['AddMsgList'], loginInfo)
        return dic['AddMsgList'], dic['ModContactList']

    def process_msg_slowly(self, msg, loginInfo, isActivateAutoReply=True, isAutoAddFriend=True, responseMsg='test'):
        # handle text and friend request
        msgType = msg['MsgType']
        userName = loginInfo['User']['UserName']
        # decide the receiver of this msg:
        receiver = msg['FromUserName']
        sent = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=responseMsg,toUserName='filehelper')
        print sent
        if msg['FromUserName'] == userName:
            # I am the sender
            return 'OK'
        if msgType:
            if msgType==1 and isActivateAutoReply: # plain text
                sent = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=responseMsg,toUserName=receiver)
                print 'Successfully reply to %s' % receiver
                return sent
            if msgType==37 and isAutoAddFriend:
                print msg
                newFriendUserName = msg['RecommendInfo']['UserName']
                sent = itchats.add_friend(newFriendUserName, status=3, verifyContent=msg['Ticket'], loginInfo=loginInfo)
                print 'Successfully added a new friend'
                print sent
                autoReply = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=responseMsg,toUserName=newFriendUserName)
                print 'Successfully replied to new friend %s' % newFriendUserName
                return autoReply
        return 'No compatible msg type, continue'
