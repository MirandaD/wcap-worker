from pymongo import MongoClient
from bson.objectid import ObjectId

class DB():
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['wacp-dev']
        self.LoginInfo = self.db.loginInfo
        self.Messages = self.db.Messages
    def get_login_info_by_uuid(self, id):
        if not id=='empty':
            loginInfo = self.LoginInfo.find_one({'_id': ObjectId(id)})
            return loginInfo
        else:
            loginInfo = self.LoginInfo.find_one()
            return loginInfo
    def update_login_info(self, loginInfo):
        updateRes = self.LoginInfo.update_one({'_id': ObjectId(loginInfo['_id'])}, {'$set': loginInfo})
        return updateRes
    def save_login_info(self, loginInfo):
        saveRes = self.LoginInfo.insert_one(loginInfo)
        return saveRes.inserted_id
    def save_list_of_msg(self, listOfMsg, loginInfo):
        for msg in listOfMsg:
            tempMsg = msg
            tempMsg['loginInfo'] = loginInfo
            self.Messages.insert_one(tempMsg)
    def get_one_msg(self):
        oneMsg = self.Messages.find_one()
        return oneMsg
    def delete_one_msg(self, id):
        delRes = self.Messages.find_one_and_delete({'_id': ObjectId(id)})
        return delRes