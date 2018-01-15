from pymongo import MongoClient
from bson.objectid import ObjectId
import os

class DB():
    def __init__(self):
        self.mongoConnectionStr = 'mongodb://localhost:27017/'
        if os.environ.get('APP_LOCATION') == 'heroku':
            self.mongoConnectionStr = 'mongodb://mirandaLi:lisirui1020@cluster0-shard-00-00-eluxi.mongodb.net:27017,cluster0-shard-00-01-eluxi.mongodb.net:27017,cluster0-shard-00-02-eluxi.mongodb.net:27017/admin?readPreference=primary&ssl=true'
        self.client = MongoClient(self.mongoConnectionStr)
        self.db = self.client['wacp-dev']
        self.LoginInfo = self.db.loginInfo
        self.Messages = self.db.Messages
    def get_login_info_by_uuid(self, id):
        loginInfo = self.LoginInfo.find_one()
        return loginInfo
    def get_login_info_cursor(self):
        loginInfoCursor = self.LoginInfo.find()
        return loginInfoCursor
    def update_login_info(self, loginInfo):
        updateRes = self.LoginInfo.update_one({'_id': ObjectId(loginInfo['_id'])}, {'$set': loginInfo})
        return updateRes
    def save_login_info(self, loginInfo):
        saveRes = self.LoginInfo.insert_one(loginInfo)
        return saveRes.inserted_id
    def delete_login_info(self, loginInfo):
        delRes = self.LoginInfo.find_one_and_delete(loginInfo)
        return delRes
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
    def test_save_chinese(self, toSave):
        saveRes = self.Messages.insert_one(toSave)
        return saveRes
    def test_get_chinese(self, toget):
        getRes = self.Messages.find_one(toget)
        return getRes