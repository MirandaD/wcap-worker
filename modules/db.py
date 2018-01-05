from pymongo import MongoClient
from bson.objectid import ObjectId

class DB():
    def get_login_info_by_uuid(self, id):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['wacp-dev']
        loginInfo = db.loginInfo.find_one({'_id': ObjectId(id)})
        return loginInfo
