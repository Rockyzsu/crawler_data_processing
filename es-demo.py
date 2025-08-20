import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
import time
import random
import json
from urllib.parse import urlparse, parse_qs

# Initialize Elasticsearch connection
def init_elasticsearch(host='localhost', port=9200):
    """Initialize Elasticsearch connection"""
    es = Elasticsearch([f'http://{host}:{port}'])
    if es.ping():
        print("Successfully connected to Elasticsearch")
        return es
    else:
        print("Failed to connect to Elasticsearch, please check configuration")
        return None

# Create index and mapping
def create_ecommerce_index(es, index_name='amazon_products'):
    """Create Amazon product index and mapping"""
    if es.indices.exists(index=index_name):
        print(f"Index {index_name} already exists")
        return True
        
    # Define index mapping
    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "english_analyzer": {
                        "type": "standard",
                        "stopwords": "_english_"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "analyzer": "english_analyzer",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "price": {"type": "float"},
                "original_price": {"type": "float"},
                "currency": {"type": "keyword"},
                "category": {"type": "keyword"},
                "sub_category": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "rating": {"type": "float"},
                "review_count": {"type": "integer"},
                "description": {"type": "text", "analyzer": "english_analyzer"},
                "features": {"type": "text", "analyzer": "english_analyzer"},
                "specifications": {"type": "text", "analyzer": "english_analyzer"},
                "url": {"type": "keyword"},
                "image_url": {"type": "keyword"},
                "availability": {"type": "keyword"},
                "scraped_at": {"type": "date"}
            }
        }
    }
    
    try:
        es.indices.create(index=index_name, body=mapping)
        print(f"Successfully created index {index_name}")
        return True
    except RequestError as e:
        print(f"Failed to create index: {e}")
        return False

# Extract data from Amazon product page
def scrape_amazon_product(product_url):
    """Scrape product data from Amazon product page"""
    # Set request headers to simulate browser behavior
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    
    try:
        # Add random delay to avoid anti-scraping measures
        time.sleep(random.uniform(2, 5))
        
        # Send request
        response = requests.get(product_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTP errors
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract ASIN (Amazon product ID)
        parsed_url = urlparse(product_url)
        query_params = parse_qs(parsed_url.query)
        asin = query_params.get('asin', [None])[0]
        
        # If no ASIN in URL, try extracting from page
        if not asin:
            asin_meta = soup.find('meta', {'name': 'twitter:data1'})
            if asin_meta:
                asin = asin_meta.get('content', '').split(':')[-1].strip()
        
        # Extract product name
        product_name = soup.find('span', {'id': 'productTitle'})
        product_name = product_name.get_text(strip=True) if product_name else None
        
        # Extract price
        price = None
        original_price = None
        currency = '$'
        
        price_elem = soup.find('span', {'class': 'a-price-whole'})
        if price_elem:
            price_str = price_elem.get_text(strip=True).replace(',', '').replace('.', '')
            decimal_elem = soup.find('span', {'class': 'a-price-fraction'})
            if decimal_elem:
                price_str += '.' + decimal_elem.get_text(strip=True)
            price = float(price_str) if price_str else None
        
        # Extract original price (if discounted)
        original_price_elem = soup.find('span', {'class': 'a-price a-text-price'})
        if original_price_elem:
            original_price_str = original_price_elem.get_text(strip=True).replace(currency, '').replace(',', '')
            original_price = float(original_price_str) if original_price_str else None
        
        # Extract rating and review count
        rating = None
        review_count = None
        
        rating_elem = soup.find('span', {'class': 'a-icon-alt'})
        if rating_elem:
            rating_str = rating_elem.get_text(strip=True).split()[0]
            rating = float(rating_str) if rating_str else None
        
        review_count_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
        if review_count_elem:
            review_count_str = review_count_elem.get_text(strip=True).split()[0].replace(',', '')
            review_count = int(review_count_str) if review_count_str else None
        
        # Extract brand
        brand = None
        brand_elem = soup.find('a', {'id': 'bylineInfo'})
        if brand_elem:
            brand = brand_elem.get_text(strip=True).replace('Visit the ', '').replace(' Store', '')
        
        # Extract product description
        description = None
        description_elem = soup.find('div', {'id': 'productDescription'})
        if description_elem:
            description = description_elem.get_text(strip=True)
        
        # Extract product features
        features = []
        features_elems = soup.find_all('li', {'class': 'a-spacing-mini'})
        if features_elems:
            features = [f.get_text(strip=True) for f in features_elems[:5]]  # Get first 5 features
        features_text = ', '.join(features)
        
        # Extract category information
        category = None
        sub_category = None
        breadcrumbs = soup.find_all('li', {'class': 'a-spacing-none a-list-item'})
        if len(breadcrumbs) >= 2:
            category = breadcrumbs[-2].get_text(strip=True) if len(breadcrumbs) > 1 else None
            sub_category = breadcrumbs[-1].get_text(strip=True) if breadcrumbs else None
        
        # Extract image URL
        image_url = None
        image_elem = soup.find('img', {'id': 'landingImage'})
        if image_elem:
            image_url = image_elem.get('src')
        
        # Extract availability status
        availability = None
        availability_elem = soup.find('div', {'id': 'availability'})
        if availability_elem:
            availability = availability_elem.get_text(strip=True)
        
        # Build product data dictionary
        product_data = {
            "product_id": asin,
            "name": product_name,
            "price": price,
            "original_price": original_price,
            "currency": currency,
            "category": category,
            "sub_category": sub_category,
            "brand": brand,
            "rating": rating,
            "review_count": review_count,
            "description": description,
            "features": features_text,
            "url": product_url,
            "image_url": image_url,
            "availability": availability,
            "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
        
        return product_data
        
    except Exception as e:
        print(f"Error scraping product: {e}")
        return None

# Import data to Elasticsearch
def import_to_es(es, product_data, index_name='amazon_products'):
    """Import single product data to Elasticsearch"""
    if not product_data or not product_data.get('product_id'):
        print("Invalid product data, skipping import")
        return False
    
    try:
        # Use product ID as document ID
        response = es.index(
            index=index_name,
            id=product_data['product_id'],
            body=product_data
        )
        
        if response['result'] in ['created', 'updated']:
            print(f"Successfully imported product: {product_data.get('name')}")
            return True
        else:
            print(f"Failed to import product: {product_data.get('name')}")
            return False
            
    except Exception as e:
        print(f"Error importing to Elasticsearch: {e}")
        return False

# Main function
def main():
    # Initialize Elasticsearch connection
    es = init_elasticsearch()
    if not es:
        return
    
    # Create index
    index_name = 'amazon_products'
    create_ecommerce_index(es, index_name)
    
    # List of Amazon product URLs to scrape
    product_urls = [
        # Example product URLs - replace with any Amazon product pages
        "https://www.amazon.com/dp/B07VGRJDFY",
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.amazon.com/dp/B09V3KXJPB"
    ]
    
    # Scrape and import each product
    for url in product_urls:
        print(f"\nScraping product from: {url}")
        product_data = scrape_amazon_product(url)
        
        if product_data:
            print(f"Successfully scraped product: {product_data.get('name')}")
            import_to_es(es, product_data, index_name)
        else:
            print(f"Failed to scrape product from: {url}")
        
        # Scrape interval
        if url != product_urls[-1]:
            sleep_time = random.uniform(3, 7)
            print(f"Waiting {sleep_time:.2f} seconds before next scrape...")
            time.sleep(sleep_time)
    
    print("\nAll operations completed")

if __name__ == "__main__":
    main()
