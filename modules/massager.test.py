import unittest
import requests
import massager

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.Masseger = massager.Massager(requests)
    def test_get_msg(self):
        returnedDic = self.Masseger.get_msg('5a4f92f65e25504e396faa13')
        print 'herh------'
        print(returnedDic)

if __name__ == '__main__':
    unittest.main()