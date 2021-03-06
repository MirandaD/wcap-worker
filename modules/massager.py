#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import config
import itchats
import pydash
import pprint
import requests
import re

class Massager():
    def __init__(self, requests, db):
        # requires requests and costomized db
        self.db = db
        self.s = requests
    def sync_check(self, loginInfo):
        url = '%s/synccheck' % loginInfo['syncUrl']
        params = {
            'r'        : int(time.time() * 1000),
            'skey'     : loginInfo['skey'],
            'sid'      : loginInfo['wxsid'],
            'uin'      : loginInfo['wxuin'],
            'synckey'  : loginInfo['synckey'],
            '_'        : int(time.time() * 1000),}
        headers = { 'User-Agent' : config.USER_AGENT }
        try:
            r = self.s.get(url, params=params, headers=headers, timeout=config.TIMEOUT)
        except requests.exceptions.ConnectionError as e:
            try:
                if not isinstance(e.args[0].args[1], BadStatusLine):
                    raise
                # will return a package with status '0 -'
                # and value like:
                # 6f:00:8a:9c:09:74:e4:d8:e0:14:bf:96:3a:56:a0:64:1b:a4:25:5d:12:f4:31:a5:30:f1:c6:48:5f:c3:75:6a:99:93
                # seems like status of typing, but before I make further achievement code will remain like this
                return '2'
            except:
                raise
        r.raise_for_status()
        regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
        pm = re.search(regx, r.text)
        if pm is None or pm.group(1) != '0':
            print('Unexpected sync check result: %s' % r.text)
            return None
        return pm.group(2)

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
        print msg_content
        if len(predefined_msg_array) == 0:
            return None
        elif not msg_content:
            return None
        else:
            print predefined_msg_array
            default_reply = pydash.find(predefined_msg_array, {'key': unicode('default')})
            reply_msg = default_reply['value']
            if msg_content=='newfriend':
                default_reply = pydash.find(predefined_msg_array, {'key': 'newfriend'})
                reply_msg = default_reply['value']
            if not isKeyWordReplyActive:
                return reply_msg
            elif reply_msg!=None:
                return reply_msg
            else:
                return None

    def send_raw_msg(self, loginInfo, userName, msgType, content, toUserName):
        url = '%s/webwxsendmsg' % loginInfo['url']
        data = {
            'BaseRequest': loginInfo['BaseRequest'],
            'Msg': {
                'Type': msgType,
                'Content': content,
                'FromUserName': userName,
                'ToUserName': toUserName ,
                'LocalID': int(time.time() * 1e4),
                'ClientMsgId': int(time.time() * 1e4),
                }, 
            'Scene': 0, }
        headers = { 'ContentType': 'application/json; charset=UTF-8', 'User-Agent' : config.USER_AGENT }
        cookies = loginInfo['cookieJar']
        r = self.s.post(url, headers=headers, cookies=cookies,
            data=json.dumps(data, ensure_ascii=False).encode('utf8'))
        print r
        return r.content

    def process_msg_slowly(self, msg, loginId, isActivateAutoReply=True, isAutoAddFriend=True, responseMsg='test'):
        # TODO: handle group msg
        # handle text and friend request
        loginInfo = self.db.get_login_info_by_uuid(loginId)
        msgType = msg['MsgType']
        userName = loginInfo['User']['UserName']
        nickName = loginInfo['User']['NickName']
        # decide the receiver of this msg:
        receiver = msg['FromUserName']
        if msg['FromUserName'] == userName:
            # I am the sender
            print 'sender ismyself'
            return 'OK'
        if '@@' in msg['FromUserName']:
            # from group
            return 'OK'
        if msgType:
            try:
                # syncCheckRes = self.sync_check(loginInfo)
                print msgType
                if msgType==1 and isActivateAutoReply: # plain text
                    reply_msg = self.get_reply_msg(loginInfo['customReply'], msg['Content'], True)
                    sent = self.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1, content=reply_msg, toUserName=receiver)
                    pprint.pprint(sent)
                    print 'Successfully reply to %s' % receiver
                    return sent
                if msgType == 37 and isAutoAddFriend: # friend request
                    print 'new friend'
                    newFriendUserName = msg['RecommendInfo']['UserName']
                    sent = itchats.add_friend(newFriendUserName, status=3, verifyContent=msg['Ticket'], loginInfo=loginInfo)
                    print 'Successfully added a new friend'
                    reply_msg = self.get_reply_msg(loginInfo['customReply'], 'newfriend', isKeyWordReplyActive=True)
                    print reply_msg
                    autoReply = self.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1,content=reply_msg,toUserName=newFriendUserName)
                    print 'Successfully replied to new friend %s' % newFriendUserName
                    return autoReply
                if msgType == 10000 or msgType == 51:
                    print 10000
                    sent = itchats.add_friend(receiver, status=3, verifyContent=msg['Ticket'], loginInfo=loginInfo)
                    reply_msg = self.get_reply_msg(loginInfo['customReply'], 'newfriend', isKeyWordReplyActive=True)
                    pprint.pprint(sent)
                    autoReply = self.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1, content=reply_msg, toUserName=receiver)
                    pprint.pprint(autoReply)
                    print 'Successfully replied to new friend %s' % receiver
            except Exception as e:
                print'unexpected error happened', e.message, e.__doc__
                time.sleep(3)
        loginInfo = None
        return 'No compatible msg type, continue'