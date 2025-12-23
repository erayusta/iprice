import sys
import requests
import os
import json
import time
import dotenv
import logging

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

dotenv.load_dotenv('../../.env')
server_path = os.getenv('SERVER_PATH')

if os.path.exists(server_path):
    sys.path.append(server_path)
    print("Server environment detected, using server path")

from requests.auth import HTTPBasicAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.repositories.StockRepository import StockRepository
from app.services.StockService import StockService


def get_products_page(base_url: str, endpoint: str, consumer_key: str, consumer_secret: str,
                      page: int) -> requests.Response:
    params = {
        "per_page": 100,
        "page": page
    }

    return requests.get(
        base_url + endpoint,
        auth=HTTPBasicAuth(consumer_key, consumer_secret),
        params=params
    )


def process_products(products):
    stock_products = {}

    for product in products:
        mpn = product.get('sku')
        name = product.get('name')
        stock_quantity = product.get('stock_quantity')
        #is_stock = product.get('is_stock', 'N/A')

        stock_products[mpn] = {
            'name': name,
            'stock_quantity': stock_quantity,
        }

        print(f"SKU: {mpn}")
        print(f"Name: {name}")
        print(f"Stock: {stock_quantity}")
        print("---")

    return stock_products


def sync_products(
        base_url: str,
        consumer_key: str,
        consumer_secret: str,
        stock_service: StockService
) -> None:

    endpoint = "/wp-json/wc/v3/products"
    current_page = 1
    all_products = []

    while True:
        try:
            response = get_products_page(base_url, endpoint, consumer_key, consumer_secret, current_page)

            if response.status_code == 200:
                if current_page == 1:
                    total_products = int(response.headers.get('X-WP-Total', 0))
                    total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                    print(f"Total number of products: {total_products}")
                    print(f"Total number of pages: {total_pages}")
                    print("---")

                products = json.loads(response.text)
                stock_products = process_products(products)


                stock_service.create_stock_data(stock_products)

                all_products.extend(products)

                total_products = int(response.headers.get('X-WP-Total', 0))
                if len(all_products) < total_products:
                    current_page += 1
                    print(f"Fetching page {current_page}...")
                    time.sleep(1)
                else:
                    break
            else:
                print(f"Failed to retrieve products. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                break

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            break

    print(f"Total products retrieved: {len(all_products)}")


def main():

    base_url = "https://pt.com.tr"
    consumer_key = "ck_b4517c7deb158874f1fcc33c5e0405b9820771b9"
    consumer_secret = "cs_efd72d2272eca768c75e2295f4c76cd9c4f47d99"
    database_url = os.getenv('DATABASE_URL')

    try:
        engine = create_engine(database_url)
        session = sessionmaker(bind=engine)
        db_session = session()

        stock_repository = StockRepository(db_session)
        stock_service = StockService(stock_repository)

        sync_products(base_url, consumer_key, consumer_secret, stock_service)

        return 0
    except Exception as e:
        print(f"Error in main: {str(e)}")
        return 1


if __name__ == "__main__":
    main()