import twitter_credential
import tweepy
import time
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk


nltk.download('vader_lexicon',quiet=True)


def authenticate():
    auth = OAuthHandler(twitter_credential.API_KEY, twitter_credential.API_SECRET_KEY)
    auth.set_access_token(twitter_credential.ACCESS_TOKEN, twitter_credential.ACCESS_TOKEN_SECRET)
    return auth


class TwitterClient():
    def __init__(self, username=None):
        self.auth = authenticate()
        self.twitterClient = API(self.auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
        self.username = username

    def get_tweets(self, numTweets):
        # tweets = []
        # for tweet in Cursor(self.twitterClient.user_timeline, id=self.username).items(numTweets):
        #     tweets.append(tweet)

        count = 0
        add = False
        tweets = Cursor(self.twitterClient.user_timeline,q="-filter:retweets", id=self.username).items()
        res=[]
        while count < numTweets:
            try:
                tweet = tweets.next()
                if hasattr(tweet, "in_reply_to_status_id_str"):
                    if tweet.in_reply_to_status_id_str is None:
                        add=True
                else:
                    add = True

                if add and (not tweet.retweeted) and ('RT @' not in tweet.text):
                    res.append(tweet)
                    count += 1
                add = False
            except tweepy.RateLimitError as e:
                print(f'API rate limit reached {e}')
                time.sleep(60)
                continue
            except tweepy.TweepError as e:
                print(f'tweepy error occured {e}')
                error = True
                break
            except StopIteration as e:
                print(f"Loop ended {e}")
                break
            except Exception as e:
                print(f'Error: {e}')
                error = True
                break

        return res

    def get_client(self):
        return self.twitterClient

    def get_username(self):
        return self.username


class DataLoader():
    def toDataFrame(self, tweets):
        df =None
        try:
            df = pd.DataFrame(
                data=[[tweet.id, tweet.text, tweet.favorite_count, tweet.retweet_count
                          , tweet.source, tweet.created_at] for tweet in tweets]
                , columns=["id", "text", "favorite_count", "retweet_count", "source", "created_at"])
        except AttributeError:
            df = pd.DataFrame(
                data=[[tweet.id, tweet.full_text, tweet.favorite_count, tweet.retweet_count
                          , tweet.source, tweet.created_at] for tweet in tweets]
                , columns=["id", "text", "favorite_count", "retweet_count", "source", "created_at"])

        return df


class Analyzer():
    # def strip_tweet(self, tweet):
    #     return ''.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet)).strip()

    def get_sentiment(self, tweet):
        return SentimentIntensityAnalyzer().polarity_scores(tweet)

    def add_sentiment(self,df):
        df["sentiment"] = np.array([self.get_sentiment(tweet)["compound"] for tweet in df["text"]])
        return df

    def graph(self,df):
        sns.set()
        sns.relplot(data=df, x="created_at", y="sentiment", hue="source", kind="line", ci=None)
        plt.show()


class Tweets():
    def __init__(self,username,num_tweets=5):
        self.client = TwitterClient(username)
        self.tweets = DataLoader().toDataFrame(self.client.get_tweets(num_tweets))
        self.analyzer = Analyzer()
        self.num_tweets = num_tweets
        # self.num_replies = num_replies
        # self.replies = {}
        # self.get_replies()
        self.analyzer.add_sentiment(self.tweets)

    def get_reply(self,id,num=5):
        api = self.client.get_client()
        print("\nSearching for tweets with")
        print(f'Id : {id}\nto:{self.client.get_username()}')
        print("\n")
        tweets = Cursor(api.search, q=f'to:@{self.client.get_username()}'
                        , since_id=id, tweet_mode='extended'
                        , result_type='recent'
                        ).items()
        count = 0
        replies=[]
        while count < num:
            try:
                tweet = tweets.next()
                # print(tweet)
                if hasattr(tweet, "in_reply_to_status_id_str"):
                    # print(tweet)
                    if tweet.in_reply_to_status_id_str == str(id):
                        # print(f'Reply:{tweet}')
                        replies.append(tweet)
                        count += 1
            except tweepy.RateLimitError as e:
                print(f'API rate limit reached {e}')
                time.sleep(60)
                continue
            except tweepy.TweepError as e:
                print(f'tweepy error occured {e}')
                break
            except StopIteration:
                print()
                print("Stop Iteration")
                print(f'Only {count} items present in the result')
                break
            except Exception as e:
                print(f'Error: {e}')
                break

        replies = DataLoader().toDataFrame(replies)
        self.analyzer.add_sentiment(replies)
        return replies
        # for id in self.tweets["id"]:
        #     replies=[]
        #     # try:
        #         # for tweet in Cursor(api.search,q=f'to:{self.client.get_username()}'
        #         #         ,since_id = id,tweet_mode='extended'
        #         #         ,result_type='recent').items(2):
        #         #     print(tweet)
        #         #     if hasattr(tweet,"in_reply_to_status_id_str") and tweet.in_reply_to_status_id_str==id:
        #         #         print(f'Reply:{tweet}')
        #         #         replies.append(tweet)
        #
        #     if error:
        #         break
        #     # except Exception as e:
        #     #     print(f'Error: {e}')
        #     #     break
        #
        #     self.replies[id] = DataLoader().toDataFrame(replies)
        #     self.analyzer.add_sentiment(self.replies[id])

    def display(self):
        print(f"\n First {self.num_tweets} tweets\n")
        pd.set_option('max_colwidth', 60)
        pd.options.display.show_dimensions = False
        print(self.tweets[['text','sentiment']])
        print("\n")
        # print()
        # print("Replies ")
        # for id in self.replies:
        #     print(f'For tweet {id} :')
        #     print(self.replies[id][['id','text','sentiment']])

username = input("Enter the username ")
user = Tweets(username)
user.display()
row=int(input("\nEnter the tweet number to analyse "))
id= user.tweets["id"].iloc[row]
nreplies=int(input("\nEnter the number of replies to analyse "))
user.analyzer.graph(user.get_reply(id,nreplies))




