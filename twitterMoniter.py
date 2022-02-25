import twint
import pandas as pd

config = twint.Config()

class User():
    def __init__(self,name="Youtube",num_tweets=20):
        self.username = name
        self.num_tweets = num_tweets
        self.config = twint.Config()
        self.config.Username = self.username
        self.config.Search = f'from:@{self.username}'
        self.config.Pandas = True
        self.config.Limit = self.num_tweets
        self.config.Hide_output =False
        self.tweets = pd.DataFrame()
        self.get_tweets()


    def get_tweets(self):
        # until=""
        # dfs =[]
        # count=0
        # while count < self.num_tweets:
        #     self.config.until=until
        #     twint.run.Search(self.config)
        #     temp = twint.storage.panda.Tweets_df
        #     index = []
        #     for i,v in enumerate(temp["reply_to"]):
        #         if len(v) != 0:
        #             index.append(i)
        #     dates =  temp["date"]
        #     until =dates.pop(len(dates)-1)
        #     temp.drop(labels=index,axis=0,inplace=True)
        #     print(temp)
        #     dfs.append(temp)
        #     count+= temp.shape[0]
        #
        # self.tweets= pd.concat(dfs)

        self.config.since = "2021-07-19"
        twint.run.Search(self.config)
        temp = twint.storage.panda.Tweets_df
        pd.set_option('display.max_columns', None)
        print(temp.head())


    def display(self):
        print(self.tweets.head(5))


client = User("Youtube")
# pd.set_option('display.max_columns', None)
# client.display()

#
# print(client.tweets["reply_to"])
# x=client.tweets["date"]
# print(x.pop(len(x)-1))