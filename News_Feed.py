import requests
from datetime import datetime
import pandas as pd
from typing import List, Dict


class TechCrunchNews:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
        self.source = "techcrunch"

    def get_articles(self, days: int = 7, keywords: str = None) -> List [Dict]:
        params = {
            'apiKey': self.api_key,
            'sources': self.source,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 100
        }

        if keywords:
            params ['q'] = keywords

        response = requests.get (self.base_url, params=params)
        articles = response.json ().get ('articles', [])

        df = pd.DataFrame (articles)
        df ['publishedAt'] = pd.to_datetime (df ['publishedAt'])
        df ['source'] = df ['source'].apply (lambda x: x ['name'])

        return df [['title', 'description', 'url', 'publishedAt', 'source']]

    def get_tech_company_news(self, companies=None) -> pd.DataFrame:
        if companies is None:
            companies = ['Apple', 'Google', 'Microsoft', 'Amazon',
                         'Meta']
        all_news = []
        for company in companies:
            news = self.get_articles (keywords=company)
            news ['company'] = company
            all_news.append (news)

        return pd.concat (all_news).sort_values ('publishedAt', ascending=False)
