from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from nltk.corpus import stopwords
import re
import nltk
from nltk.stem.porter import PorterStemmer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor


def home(request):
    return render(request, 'news/home.html')

# Data Cleaning
port_stem=PorterStemmer()
def stemming(content):
    stemmed_content = re.sub('[^a-zA-Z]', ' ', str(content))
    stemmed_content = stemmed_content.lower()
    stemmed_content = stemmed_content.split()
    stemmed_content = [port_stem.stem(word) for word in stemmed_content if word not in stopwords.words('english')]
    stemmed_content = ' '.join(stemmed_content)
    return stemmed_content

def analyze_sentiment(article_text):
    blob = TextBlob(article_text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def get_article_sentiment(link):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'p')))
    article_soup = BeautifulSoup(driver.page_source, 'html.parser')
    paragraphs = article_soup.find_all('p')
    article_text = ' '.join([p.get_text() for p in paragraphs])
    driver.quit()
    
    stemmed_article = stemming(article_text)[:300]
    return analyze_sentiment(stemmed_article)


def extract_article_data(article):
    try:
        title_tag = article.find('a', {'class': 'JtKRv'})
        if title_tag:
            title = title_tag.get_text()
            link = 'https://news.google.com' + title_tag['href'][1:]
            published_time_tag = article.find('time')
            published_time = published_time_tag.text if published_time_tag else 'Unknown'
            sentiment = get_article_sentiment(link)

            return {
                'title': title,
                'link': link,
                'time': published_time,
                'sentiment': sentiment
            }
        else:
            print(f"Title tag not found")
    except Exception as e:
        return None


def get_google_news(query, num_articles=15):
    url = f"https://news.google.com/search?q={query}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve news articles: Status code {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    
    articles = soup.find_all('article', limit=num_articles)

    with ThreadPoolExecutor(max_workers=20) as executor:
        news_metadata = list(executor.map(extract_article_data, articles))

    return [article for article in news_metadata if article]


def result(request):
    if request.method == 'POST':
        key = request.POST.get('Keywords')
        if key:
            news_data = get_google_news(key)

            news_info = []
            
            for idx, news in enumerate(news_data, 1):
                news_info.append((news['time'], news['title'], news['link'], news['sentiment']))
                

            context={'Headline':news_info}

            return render(request, 'news/result.html', context)
        
        else:
            return render(request, 'news/result.html', {'result': 'Key is not provided correctly'})
        
    else:
        return HttpResponse("Invalid request method", status=405)


    


    
    


    
    
