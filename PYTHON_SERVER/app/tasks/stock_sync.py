import os
import sys
import requests
import json
import time
import logging
from requests.auth import HTTPBasicAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.celery_worker import celery

server_path = os.getenv('SERVER_PATH')
if server_path and os.path.exists(server_path) and server_path not in sys.path:
    sys.path.append(server_path)

from app.repositories.StockRepository import StockRepository
from app.services.StockService import StockService

logger = logging.getLogger(__name__)

def get_products_page(base_url: str, endpoint: str, consumer_key: str, consumer_secret: str,
                      page: int) -> requests.Response:
    params = {"per_page": 100, "page": page}
    return requests.get(
        base_url + endpoint,
        auth=HTTPBasicAuth(consumer_key, consumer_secret),
        params=params,
        timeout=30  # Timeout eklemek her zaman iyi bir fikirdir.
    )


def process_products(products):
    stock_products = {}
    for product in products:
        mpn = product.get('sku')
        if not mpn:
            continue  # SKU'su olmayan ürünleri atla

        name = product.get('name')
        stock_quantity = product.get('stock_quantity')

        stock_products[mpn] = {
            'name': name,
            'stock_quantity': stock_quantity,
        }
        logger.debug(f"Processed SKU: {mpn}, Name: {name}, Stock: {stock_quantity}")
    return stock_products


@celery.task(name='app.tasks.stock_sync.sync_woocommerce_products', queue='stock_sync', bind=True)
def sync_woocommerce_products(self):
    logger.info("Starting WooCommerce product sync task...")
    base_url = "https://pt.com.tr"
    consumer_key = "ck_b4517c7deb158874f1fcc33c5e0405b9820771b9"
    consumer_secret = "cs_efd72d2272eca768c75e2295f4c76cd9c4f47d99"
    database_url = os.getenv('DATABASE_URL')

    if not all([base_url, consumer_key, consumer_secret, database_url]):
        logger.error(
            "Missing required environment variables for WooCommerce sync task. Check WOO_BASE_URL, WOO_CONSUMER_KEY, WOO_CONSUMER_SECRET, DATABASE_URL.")
        return

    db_session = None
    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        db_session = Session()

        stock_repository = StockRepository(db_session)
        stock_service = StockService(stock_repository)

        endpoint = "/wp-json/wc/v3/products"
        current_page = 1
        total_retrieved = 0
        total_updated = 0

        while True:
            logger.info(f"Fetching page {current_page}...")
            response = get_products_page(base_url, endpoint, consumer_key, consumer_secret, current_page)

            if response.status_code == 200:
                total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                products = response.json()

                if not products:
                    logger.info("No more products found on subsequent pages. Sync finished.")
                    break

                stock_products = process_products(products)
                if stock_products:
                    updated_on_this_page = stock_service.create_stock_data(stock_products)
                    total_updated += updated_on_this_page

                total_retrieved += len(products)

                if current_page >= total_pages:
                    break

                current_page += 1
                time.sleep(1)
            else:
                logger.error(f"Failed to retrieve products. Status: {response.status_code}, Response: {response.text}")
                break

        logger.info(f"Sync task completed. Total products retrieved: {total_retrieved}")
        return total_updated

    except Exception as e:
        logger.error(f"An error occurred during product sync: {str(e)}", exc_info=True)
        raise
    finally:
        if db_session:
            db_session.close()
            logger.info("Database session closed.")