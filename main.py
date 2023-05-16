import requests
from twilio.rest import Client

STOCK_NAME = "TESLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = ""
STOCK_API_KEY = ""
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}
key = "4. close"
up_down = None
difference_percent = None
news_params = {
    "apiKey": NEWS_API_KEY,
    "qInTitle": COMPANY_NAME,
}
news_response = requests.get(NEWS_ENDPOINT, params=news_params)
articles = news_response.json()["articles"]
three_articles = articles[:3]
formatted_articles = [
    f"{STOCK_NAME}: {up_down}{difference_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for
    article in three_articles]

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
message = client.messages \
    .create(
    body="Join Earth's mightiest heroes. Like Kevin Bacon.",
    from_='+12056273393',
    to='+919999999999'
)
print(message.status)
data = requests.get(STOCK_ENDPOINT, params=stock_params)
data.raise_for_status()
data = data.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]
day_before_yesterday_closing_price = data_list[1]["4. close"]
data_list = [value for (key, value) in data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]
print(yesterday_closing_price)

# STEP 1: Use https://www.alphavantage.co/documentation/#daily
# When stock price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
# make a bloomberg terminal for yourself
# TODO 1. - Get yesterday's closing stock price. Hint: You can perform list comprehensions on Python dictionaries. e.g. [new_value for (key, value) in dictionary.items()]
connection = requests.get(STOCK_ENDPOINT, params=stock_params)
connection.raise_for_status()
data = connection.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]
print(yesterday_closing_price)
# TODO 2. - Get the day before yesterday's closing stock price
if yesterday_closing_price > day_before_yesterday_closing_price:
    up_down = "🔺"
else:
    up_down = "🔻"
difference = abs(yesterday_closing_price - day_before_yesterday_closing_price)
difference_percent = round((difference / yesterday_closing_price) * 100)
if difference_percent > 5:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]
    three_articles = articles[:3]
    formatted_articles = [
        f"{STOCK_NAME}: {up_down}{difference_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}"
        for
        article in three_articles]
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for article in formatted_articles:
        message = client.messages \
            .create(
            body=article,
            from_='+12056273393',
            to='+919999999999'
        )
    print(message.status)

print(formatted_articles)
# TODO 3. - Find the positive difference between 1 and 2. e.g. 40 - 20 = -20, but the positive difference is 20. Hint: https://www.w3schools.com/python/ref_func_abs.asp
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"
print(up_down)

# TODO 4. - Work out the percentage difference in price between closing price yesterday and closing price the day before yesterday.
if difference_percent > 5:
    print("Get News")
else:
    print("No news")

# STEP 2: https://newsapi.org/
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

# TODO 6. - Instead of printing ("Get News"), use the News API to get articles related to the COMPANY_NAME.
news_params = {
    "apiKey": NEWS_API_KEY,
    "qInTitle": COMPANY_NAME,
}
news_response = requests.get(NEWS_ENDPOINT, params=news_params)
articles = news_response.json()["articles"]
three_articles = articles[:3]
print(three_articles)

# TODO 7. - Use Python slice operator to create a list that contains the first 3 articles. Hint: https://stackoverflow.com/questions/509211/understanding-slice-notation
formatted_articles = [
    f"{STOCK_NAME}: {up_down}{difference_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for
    article in three_articles]
print(formatted_articles)

# STEP 3: Use twilio.com/docs/sms/quickstart/python
# to send a separate message with each article's title and description to your phone number.

# TODO 8. - Create a new list of the first 3 article's headline and description using list comprehension.
converted_articles = [
    f"{STOCK_NAME}: {up_down}{difference_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for
    article in three_articles]
print(converted_articles)

# TODO 9. - Send each article as a separate message via Twilio.
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
for article in formatted_articles:
    message = client.messages \
        .create(
        body=article,
        from_='+12056273393',
        to='+919999999999'
    )
    print(message.status)

# Optional TODO: Format the message like this:
"""
TESLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TESLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TESLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TESLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
