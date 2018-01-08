from modules import db
import time
from modules import itchats
from modules import massager
import requests
class MassageConsumer():
    def __init__(self):
        self.db = db.DB()
    def test_consume_msg(self):
        print 'hi'
        massagers = massager.Massager(requests,self.db)
        # loginInfo1,userName1 = itchats.login()
        counter=0
        innerCounter=0
        while counter<100:
            loggedinUser = self.db.get_login_info_by_uuid('empty')
            if not loggedinUser:
                time.sleep(20)
            counter = counter.__add__(1)
            while innerCounter < 100:
                innerCounter += 1
                loginInfoId = loggedinUser['_id']
                loginInfo = loggedinUser
                userName = loginInfo['User']['UserName']
                print('excuting', counter)
                msg1,msg2 = massagers.get_msg(loginInfoId)
                if msg1 and len(msg1)>0:
                    for singleMsg in msg1:
                        processRes = massagers.process_msg_slowly(singleMsg, loginInfo, responseMsg='Hi, thanks talking to Miranda\'s chatbot. Will get back to you ASAP.')
                        print processRes
                time.sleep(10)
                

if __name__ == '__main__':
    mc = MassageConsumer() 
    h = mc.test_consume_msg()