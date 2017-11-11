'''
Created on Sep 20, 2015

@author: mehdi
'''
import pymongo
from pymongo import MongoClient
# from pymongo import collection
# from bson import ObjectId


class DataBase:
    
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['db_name']
        self.collection = self.db['subject_of_tweets']
        
    def get_collection(self):
        return self.collection
    
#     def control (self):
        
    def get_record(self):
        self.collection.find()
    
    def dbClose(self):
        self.collection.close()


