import tweepy
from pred import predict_1_hour
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()

def main():
    configure()
    predicted_price = predict_1_hour()
    client = tweepy.Client(
            consumer_key=os.getenv("CONSUMER_KEY"), consumer_secret=os.getenv("CONSUMER_KEY_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"), access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
        )
    if predicted_price != "RMSE":
        response = client.create_tweet(
            text=predicted_price
        )

main()