from messaging.producer import JobProducer


def test_producer():
    """Producer'ı test et"""
    producer = JobProducer()

    # Test job'ı gönder
    result = producer.send_parsing_job(
        url='https://www.beymen.com/tr/p_apple-ipad-11-nesil-a16-11-wi-fi-128gb-pembe-tablet-md4e4tua_1729787',
        mpn='MD4E4TU/A',
        company_id=40,
        application_id=5,
        server_id=1,
        parser_type='scrapy'
    )

    print(f"📋 Sonuç: {result}")

    # Queue size kontrol et
    size = producer.get_queue_size('scrapy_jobs')
    print(f"📊 scrapy_jobs queue size: {size}")


if __name__ == "__main__":
    test_producer()