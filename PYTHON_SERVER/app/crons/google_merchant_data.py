import os
import sys
import dotenv

dotenv.load_dotenv('../../.env')
server_path = os.getenv('SERVER_PATH')

if os.path.exists(server_path):
    sys.path.append(server_path)
    print("Server environment detected, using server path")


from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.repositories.ImageRepository import ImageRepository
from app.repositories.ProductHistoryRepository import ProductHistoryRepository
from app.repositories.ProductRepository import ProductRepository
from app.services.ProductService import ProductService
from app.helper.standardize_price import standardize_price

SERVICE_ACCOUNT_FILE = 'service_account_key.json'

SCOPES = ['https://www.googleapis.com/auth/content']

MERCHANT_ID = 137831750

load_dotenv('.env')

DATABASE_URL = os.getenv('DATABASE_URL')

def authenticate_with_jwt():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    credentials.refresh(Request())
    return credentials

def get_product_data(merchant_id):
    creds = authenticate_with_jwt()
    service = build('content', 'v2.1', credentials=creds)

    all_products = []
    page_token = None

    while True:
        try:
            request = service.products().list(
                merchantId=merchant_id,
                pageToken=page_token
            )
            response = request.execute()

            products = response.get('resources', [])

            all_products.extend(products)

            page_token = response.get('nextPageToken')
            if not page_token:
                break

        except Exception as e:
            print(f"An error occurred while fetching products: {e}")
            break

    return all_products

def transform_product_data(products):
    transformed_products = {}
    for item in products:
        mpn = item.get('mpn')
        price = float(item.get('price', {}).get('value', 0))
        sale_price = float(item.get('salePrice', {}).get('value', 0)) if item.get('salePrice') else price
        transformed_products[mpn] = {
            'price': standardize_price(price),
            'sale_price': standardize_price(sale_price),
            'merchant_price': standardize_price(sale_price)
        }
    return transformed_products


if __name__ == "__main__":
    merchant_id = MERCHANT_ID

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    product_repository = ProductRepository(db_session)
    image_repository = ImageRepository(db_session)
    product_history_repository = ProductHistoryRepository(db_session)

    product_service = ProductService(product_repository, product_history_repository, image_repository)

    product_data = get_product_data(merchant_id)

    transformed_products = transform_product_data(product_data)

    updated_count = product_service.update_product_prices(transformed_products)

    updated_product_history_merchant_price = product_service.create_product_history_with_merchant_price(product_data)

    print(f"Updated merchant prices for {updated_count} products.")

    print(f"Total products of no sku_code in products_history table: {updated_product_history_merchant_price}")

    db_session.commit()
    db_session.close()
