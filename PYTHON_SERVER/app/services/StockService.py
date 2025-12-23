from app.repositories.StockRepository import StockRepository


class StockService:
    def __init__(
            self,
            stock_repository: StockRepository,
    ):
        self.stock_repository = stock_repository

    def create_stock_data(self, stocks) -> int:
        return self.stock_repository.create_stock_data(stocks)