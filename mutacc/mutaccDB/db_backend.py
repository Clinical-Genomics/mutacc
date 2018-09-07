import pymongo

#Module contains classes and functions intended to communicate with a mongodb instanced.

class DBclient(pymongo.MongoClient):

    def __init__(self, host = 'localhost', port = '27017', user = None, password= None):

        super(DBclient self).__init__(host, port)



        

