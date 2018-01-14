import json
import time
import config
import itchats
import pydash

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

    def get_reply_msg(self, predefined_msg_array, msg_content, isKeyWordReplyActive=True):
        # TODO: unit test this
        # reserved keywords: default for default, new_friend for add friend
        if len(predefined_msg_array) == 0:
            return None
        elif not msg_content:
            return None
        else:
            print predefined_msg_array
            default_reply = pydash.find(predefined_msg_array, {'key': 'default'})
            reply_msg = default_reply['value']
            if msg_content=='new_friend':
                default_reply = pydash.find(predefined_msg_array, {'key': 'new_friend'})
                print default_reply['key'], default_reply['value']
                reply_msg = default_reply['value']
            if not isKeyWordReplyActive:
                return reply_msg
            elif reply_msg!=None:
                return reply_msg
            else:
                return None

    def process_msg_slowly(self, msg, loginInfo, isActivateAutoReply=True, isAutoAddFriend=True, responseMsg='test'):
        # TODO: handle group msg
        # handle text and friend request
        msgType = msg['MsgType']
        userName = loginInfo['User']['UserName']
        # decide the receiver of this msg:
        receiver = msg['FromUserName']
        if msg['FromUserName'] == userName:
            # I am the sender
            return 'OK'
        if '@@' in msg['FromUserName']:
            # from group
            return 'OK'
        if msgType:
            if msgType==1 and isActivateAutoReply: # plain text
                print 'trying'
                reply_msg = self.get_reply_msg(loginInfo['customReply'], msg['Content'], True)
                print reply_msg
                sent = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=reply_msg,toUserName=receiver)
                print 'Successfully reply to %s' % receiver
                return sent
            if msgType==37 and isAutoAddFriend: # friend request
                newFriendUserName = msg['RecommendInfo']['UserName']
                sent = itchats.add_friend(newFriendUserName, status=3, verifyContent=msg['Ticket'], loginInfo=loginInfo)
                print 'Successfully added a new friend'
                reply_msg = self.get_reply_msg(loginInfo['customReply'], 'new_friend', isKeyWordReplyActive=True)
                print reply_msg
                autoReply = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=reply_msg,toUserName=newFriendUserName)
                print 'Successfully replied to new friend %s' % newFriendUserName
                return autoReply
        return 'No compatible msg type, continue'
