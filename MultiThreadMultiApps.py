'''
Created on Oct 1, 2015

@author: mehdi
'''

import threading
import time
from twitter import *
from pymongo import *
from MyDB import DataBase

consumer_key = ['key1' , 'key2' , 'key3', 'key4' ]
consumer_secret = ['secret1' , 'secret2','secret3', 'secret4' ]
access_token_key = ['token_key1', 'token_key2', 'token_key3',  'token_key4']
access_token_secret = ['token_secret1', 'token_secret2',  'token_secret3', 'token_secret4']

FileAddress = 'list_of_words_for_query.txt'


numOfParts = 4 # Number of parts of threads and list of programming languages
apiStreamList = []
for i in range (numOfParts-1): # Add api streams in a list
    api_stream = TwitterStream(auth=OAuth(access_token_key[i], access_token_secret[i], consumer_key[i], consumer_secret[i]))
    apiStreamList.append(api_stream)

#api_stream = TwitterStream(auth=OAuth(access_token_key, access_token_secret, consumer_key, consumer_secret))
database = DataBase()
collection = database.get_collection()

class refineTweets:
    '''
    This class will refine the tweets 
    '''
    def __init__(self, strTorefine):
        self.strTocheck = strTorefine
        self.trackingFile = open("TrackingFile.txt", "w")
        self.totalDeleted=0
        self.tweetDB = collection.find()
    
    def refine(self):
        self.tweetDB = collection.find()
        count=0
        for mytweets in self.tweetDB:
            for words in self.strTocheck:
                if words in mytweets['text']:
                    count +=1
                if count>1 :
                    break
        
                if count<2:
                    collection.remove(mytweets)
                    print ('Tweet # ' , count, ' is deleted: ', mytweets['text'].encode("utf-8"))
                    self.trackingFile.write('Deleted: ')
                    self.trackingFile.write(str(mytweets['text'].encode("utf-8")))
                    self.trackingFile.write('\n')
                    self.totalDeleted +=1
                    
                else:
                    print ('Non-deleted ' , count,': ', mytweets['text'].encode("utf-8"))
                    self.trackingFile.write('Kept: ')
                    self.trackingFile.write(str(mytweets['text'].encode("utf-8")))
                    self.trackingFile.write('\n')
                
                print (self.totalDeleted)


class Listen2Tweets:
    '''
    A class that listens to tweets and save it
    '''
    
    def __init__(self, mylistofProg, api_stream_forObject):
#         self.data = collection
        self.myProgList = mylistofProg
        self.my_api_stream = api_stream_forObject
        
    def Run2Listen (self):
        myTries=-1
        while True:
            myTries +=1
            print ( myTries, ' I am trying for: ', self.myProgList )
            try:
                for tweet in self.my_api_stream.statuses.filter(track=self.myProgList, language='en'):    
                    if 'text' in tweet:
                        print(tweet['text'].encode("utf-8"))
                        collection.insert(tweet)
                        
        
            except TwitterError as e:
                if 'errors' in e.response_data:
                        if e.response_data['errors'][0]['code'] == 88:
                            print (e.response_data['errors'][0]['message'])
                            time.sleep(60)

########################################################


def readFile (fileAddress):
    '''
        Read proglist and split data
    '''
    with open (fileAddress, "r") as myfile:
        plList=myfile.read().replace('\n', ',')
    strPlList = ""
    strPlList = plList
    y = strPlList.split(',',len(strPlList))
    strList = ["" for k in range(len(y))]
    for index in range(0, len(strList)):
        strList[index] = y[index] 
    myComb = round(len(strList)*(len(strList)-1)/2) 
    checkArray = ["" for k in range(myComb)]
    count = 0
    for i in range(0, len(strList)-1):
        for j in range(i+1 , len(strList)):
            checkArray[count] = strList[i] + " " + strList[j]
            count = count +1
        
            
    combOfLang =""
    for i in range(0,len(checkArray)-1):
        combOfLang = combOfLang + checkArray[i]
        if i<len(checkArray)-2:
            combOfLang = combOfLang + "," #combination of programming languages in string separated by blank space and ","
    print (combOfLang)    
    return checkArray
############  readFile End     
########################################
def readFile2strArray (fileAddress):
    '''
        Read proglist and split data
    '''
    with open (fileAddress, "r") as myfile:
        plList=myfile.read().replace('\n', ',')
    strPlList = ""
    strPlList = plList
    y = strPlList.split(',',len(strPlList))
    strList = ["" for k in range(len(y))]
    for index in range(0, len(strList)):
        strList[index] = y[index]
    return strList 
#######################  raedFile2 string array END
# print('readFile2strArray(FileAddress): ',readFile2strArray(FileAddress))    
# readFile("ProgLangListVeryShort.txt")


allCombArray = readFile(FileAddress)
print ('Length of allCombArray', len(allCombArray))
partSize = round(len(allCombArray)/numOfParts)
strArrayOfCombs =["" for k in range(numOfParts-1)]
count=0
for part in range(0,numOfParts-1):
    for index in range(0,partSize-1):
        strArrayOfCombs[part]  += allCombArray [count]
        count += 1
        if (index<partSize-2):
            strArrayOfCombs[part]  += ',' 
    
    print ('strArrayOfCombs: ',  strArrayOfCombs[part])

######################   Define list of objects to listen
my_listeners = [Listen2Tweets for k in range(len(strArrayOfCombs))]

for i in range (len(strArrayOfCombs)):  # len(strArrayOfCombs) = numOfParts-1
    my_listeners[i] = Listen2Tweets(strArrayOfCombs[i], apiStreamList[i])
#     print ('strArrayOfCombs[', i, '] : ',strArrayOfCombs[i])  # printing the array of parts of programming lang. list
####################################


# refineOBJ = refineTweets(readFile2strArray(FileAddress))


############################
#
#
##################  Define list of threads from objects
my_listener_thread = [threading.Thread(target=obj.Run2Listen, args=()) for obj in my_listeners]
# my_listener_thread.append(threading.Thread(target=refineOBJ.refine(), args=()))

print("Size of each part: " , partSize)
print("Number of my_listener_thread: " , len(my_listener_thread))


## run the threads
for listener_thread in my_listener_thread:
    listener_thread.start()


