#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import config
import itchats
import pydash
import pprint

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
        try:
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
            # saveMsg = self.db.save_list_of_msg(dic['AddMsgList'], loginInfo)
            print 'succssfully pulled msg'
            return dic['AddMsgList'], dic['ModContactList']
        except:
            print 'too many requests, slowing down'
            time.sleep(3)
            return None, None

    def get_reply_msg(self, predefined_msg_array, msg_content, isKeyWordReplyActive=True):
        # TODO: unit test this
        # reserved keywords: default for default, new_friend for add friend
        if len(predefined_msg_array) == 0:
            return None
        elif not msg_content:
            return None
        else:
            print predefined_msg_array
            default_reply = pydash.find(predefined_msg_array, {'key': unicode('default')})
            reply_msg = default_reply['value']
            if msg_content=='new_friend':
                default_reply = pydash.find(predefined_msg_array, {'key': unicode('new_friend')})
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
        nickName = loginInfo['User']['NickName']
        # decide the receiver of this msg:
        receiver = msg['FromUserName']
        if msg['FromUserName'] == userName and nickName != 'Miranda':
            # I am the sender
            print 'sender ismyself'
            return 'OK'
        if '@@' in msg['FromUserName']:
            # from group
            return 'OK'
        if msgType:
            try:
                print msgType
                if msgType==1 and isActivateAutoReply: # plain text
                    reply_msg = self.get_reply_msg(loginInfo['customReply'], msg['Content'], True)
                    sent = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=reply_msg,toUserName=receiver)
                    print 'Successfully reply to %s' % receiver
                    return sent
                if msgType == 37 and isAutoAddFriend: # friend request
                    print 'new friend'
                    newFriendUserName = msg['RecommendInfo']['UserName']
                    sent = itchats.add_friend(newFriendUserName, status=3, verifyContent=msg['Ticket'], loginInfo=loginInfo)
                    print 'Successfully added a new friend'
                    reply_msg = self.get_reply_msg(loginInfo['customReply'], 'new_friend', isKeyWordReplyActive=True)
                    print reply_msg
                    autoReply = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=reply_msg,toUserName=newFriendUserName)
                    print 'Successfully replied to new friend %s' % newFriendUserName
                    return autoReply
                if msgType == 10000:
                    pprint.pprint(msg)
                    sent = itchats.add_friend(receiver, status=2, verifyContent=msg['Ticket'], loginInfo=loginInfo)
                    pprint.pprint(sent)
                    reply_msg = self.get_reply_msg(loginInfo['customReply'], 'new_friend', isKeyWordReplyActive=True)
                    print reply_msg
                    autoReply = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=reply_msg,toUserName=receiver)
                    print 'Successfully replied to new friend %s' % receiver
            except Exception as e:
                print'unexpected error happened', e.message, e.__doc__
                time.sleep(3)

        return 'No compatible msg type, continue'