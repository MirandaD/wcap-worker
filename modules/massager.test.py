import unittest
import massager
import responses
import requests
import itchats
import db
import time
from test_fixtures import returnedMsgList, loginInfo
from mock import MagicMock
from mock import Mock


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.requests = requests
        self.db = db.DB()

    # @responses.activate
    # def test_get_msg_positive(self):
    #     responses.add(
    #         responses.POST,
    #         'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=U9PwUC9LhjQYgbHd&skey=@crypt_54cf7964_ec6fff8082fdec63f1e48922bc1007de&pass_ticket=sKthmb4m1yvzw%2BO7STY4%2BSYu0d6WWzfm4DnevgKzdixZCAgXGoR1GIDMDQOmJF8Y',
    #         json=returnedMsgList.MSG_LIST,
    #         status=200)
    #     resp = requests.post(
    #         'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=U9PwUC9LhjQYgbHd&skey=@crypt_54cf7964_ec6fff8082fdec63f1e48922bc1007de&pass_ticket=sKthmb4m1yvzw%2BO7STY4%2BSYu0d6WWzfm4DnevgKzdixZCAgXGoR1GIDMDQOmJF8Y'
    #     )
    #     self.requests.post.return_value = resp
    #     self.db.get_login_info_by_uuid.return_value = loginInfo.LOGIN_INFO
    #     Masseger = massager.Massager(self.requests, self.db)
    #     (returnedMsgLists,
    #      returnedContacts) = Masseger.get_msg('5a4f92f65e25504e396faa13')
    #     print 'herh------'
    #     self.assertEqual(len(returnedMsgLists), 4)
    #     print returnedMsgLists[1]
    @unittest.skip("skipping")
    def test_inti_receive_msg(self):
        massagers = massager.Massager(requests,db)
        loginInfo,userName = itchats.login()
        itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1, content='12314', toUserName='filehelper')
        itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1, content='123555', toUserName='filehelper')
        print '------!!!!!'
        massagers.auto_reply_txt_msg(loginInfo=loginInfo, userName=userName, msgType=1, content='123556', toUserName='filehelper')
    # @unittest.skip("skipping")
    def test_keep_receive_msg(self):
        print 'hi'
        massagers = massager.Massager(requests,self.db)
        loginInfo1,userName1,cookieVal = itchats.login()
        loginInfo1['cookieJar'] = cookieVal
        loginInfoId = self.db.save_login_info(loginInfo1)
        loginInfo = self.db.get_login_info_by_uuid(loginInfoId)
        userName = loginInfo['User']['UserName']
        counter=0
        while counter<100:
            counter = counter.__add__(1)
            print('excuting')
            msg1,msg2 = massagers.get_msg(loginInfoId)
            if msg1 and len(msg1)>0:
                sent = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1, content='123145', toUserName='filehelper')
                print sent
            print msg1
            time.sleep(10)
    @unittest.skip("skipping")
    def test_consume_msg(self):
        counter = 0
        while counter<10:
            counter = counter.__add__(1)
            time.sleep(10)
            oneMsg = self.db.get_one_msg()
            print oneMsg['loginInfo']['_id']
            loginInfo = self.db.get_login_info_by_uuid(oneMsg['loginInfo']['_id'])
            userName = oneMsg['FromUserName']
            toUserName = oneMsg['ToUserName']
            sent = itchats.send_raw_msg(loginInfo=loginInfo, userName=userName, msgType=1, content='123145', toUserName='filehelper')
            print sent
            delRes = self.db.delete_one_msg(oneMsg['_id'])
            print delRes
if __name__ == '__main__':
    unittest.main()