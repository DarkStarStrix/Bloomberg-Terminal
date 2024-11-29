from News_Feed import TechCrunchNews
from Config import NEWS_API_KEY

news = TechCrunchNews(NEWS_API_KEY)
tech_news = news.get_tech_company_news()
print(tech_news.head())
