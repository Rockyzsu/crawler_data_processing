# from newspaper import Article

# url = 'http://www.cnn.com/2013/11/27/justice/tucson-arizona-captive-girls/'
# article = Article(url)
# article.download()

# article.parse()

# print('Author -->',article.authors)
# print('Publish date -->',article.publish_date)
# print('Article --> ',article.text)
import pandas as pd
import newspaper
cnn_paper = newspaper.build('https://cnn.com')
article_list = []
for article in cnn_paper.articles:
    url = article.url
    article = newspaper.Article(url)
    article.download()
    article.parse()

    print('Author -->',article.authors)
    print('Publish date -->',article.publish_date)
    print('Article --> ',article.text)
    article_obj = {
        'url': url,
        'author': article.authors,
        'publish_date': article.publish_date,
        'text': article.text
    }

    article_list.append(article_obj)

df = pd.DataFrame(article_list)
df.to_excel('cnn_articles.xlsx', index=False)

