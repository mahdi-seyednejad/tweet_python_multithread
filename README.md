# tweet_python_multithread
Listening to Twitter stream using multiple tokens and multi-threaded process.
We assume that we have 4 tokens/access key to Twitter api and we create 4 threads. Then we want to read the list of enquery words from a file, devide it and feed it to 4 threads. Finally, we listen to Twitter stream and insert the tweets in a local Mongodb data base. 
