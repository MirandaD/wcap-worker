from modules import db
import time
from modules import itchats
from modules import massager
from modules import login_info_handler
import requests
import pydash
class MassageConsumer():
    def __init__(self):
        self.db = db.DB()
        self.login_info_handler = login_info_handler.LoginInfoHandler()
        self.massagers = massager.Massager(requests,self.db)
    def test_consume_msg(self):
        print 'hi'
        # loginInfo1,userName1 = itchats.login()
        counter=0
        while True:
            loggedinUsers = self.db.get_login_info_cursor()
            print loggedinUsers.count()
            if loggedinUsers.count()==0:
                time.sleep(20)
            counter = counter.__add__(1)
            for loggedinUser in loggedinUsers:
                if not self.login_info_handler.loginInfoValidation(loggedinUser):
                    print 'Insufficient login details'
                    self.db.delete_login_info(loggedinUser)
                else:
                    # check login state first:
                    # loginStatus = self.login_info_handler.check_login_only(loggedinUser['uuid'])
                    # if loginStatus != '200':
                    #     print 'user drop out'
                    #     self.db.delete_login_info(loggedinUser)
                    # else:
                        loginInfoId = loggedinUser['_id']
                        loginInfo = loggedinUser
                        userName = pydash.get(loginInfo, 'User.UserName')
                        print('excuting', counter)
                        msg1,msg2 = self.massagers.get_msg(loginInfoId)
                        if msg1 and len(msg1)>0:
                            for singleMsg in msg1:
                                processRes = self.massagers.process_msg_slowly(singleMsg, loginInfo, responseMsg='Hi, thanks talking to Miranda\'s chatbot. Will get back to you ASAP.')
                                # all the steps should return the response from http request, I shall decide how to handle failure.
                                wechatCommunicateRet = pydash.get(processRes, 'BaseResponse.Ret', default=-1)
                                print processRes
                                if(wechatCommunicateRet != 0):
                                    print 'Disconnected with wechat account'
                                    self.db.delete_login_info(loginInfo)
                time.sleep(10)
                

if __name__ == '__main__':
    mc = MassageConsumer() 
    h = mc.test_consume_msg()