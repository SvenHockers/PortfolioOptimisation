import logging
import requests
from requests.exceptions import HTTPError
from typing import Any, Dict, Optional, List

class Trading212:
    """Rest API client for Trading212"""

    def __init__(self, api_key: str, demo: bool = True):
        self._api_key = api_key
        self.host = (
            "https://demo.trading212.com" if demo else "https://live.trading212.com"
        )

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, api_version: str = "v0") -> Any:
        return self._process_response(
            requests.get(
                f"{self.host}/api/{api_version}/{endpoint}",
                headers={"Authorization": self._api_key},
                params=params,
            )
        )

    def _post(self, endpoint: str, data: Dict[str, Any], api_version: str = "v0") -> Any:
        return self._process_response(
            requests.post(
                f"{self.host}/api/{api_version}/{endpoint}",
                headers={"Authorization": self._api_key, "Content-Type": "application/json"},
                json=data,
            )
        )

    def _get_url(self, url: str) -> Any:
        return self._process_response(
            requests.get(
                f"{self.host}/{url}",
                headers={"Authorization": self._api_key},
            )
        )

    def _delete_url(self, url: str) -> Any:
        return self._process_response(
            requests.delete(
                f"{self.host}/{url}",
                headers={"Authorization": self._api_key},
            )
        )

    @staticmethod
    def _process_response(resp: requests.Response) -> Any:
        try:
            resp.raise_for_status()
        except HTTPError as http_err:
            logging.error(resp.text)
            raise http_err
        return resp.json()

    def _process_items(self, response: Dict[str, Any]) -> List[Any]:
        res: List[Any] = []
        res += response["items"]
        while next_page := response.get("nextPagePath"):
            response = self._get_url(next_page)
            res += response["items"]
        return res

    @staticmethod
    def _validate_time_validity(time_validity: str) -> None:
        if time_validity not in ["GTC", "DAY"]:
            raise ValueError("time_validity must be one of GTC or DAY")

    def orders(self, cursor: int = 0, ticker: Optional[str] = None, limit: int = 50) -> List[Any]:
        params: Dict[str, Any] = {"cursor": cursor, "limit": limit}
        if ticker:
            params["ticker"] = ticker
        return self._process_items(self._get("equity/history/orders", params=params))

    def dividends(self, cursor: int = 0, ticker: Optional[str] = None, limit: int = 50) -> List[Any]:
        params: Dict[str, Any] = {"cursor": cursor, "limit": limit}
        if ticker:
            params["ticker"] = ticker
        return self._process_items(self._get("history/dividends", params=params))

    def transactions(self, cursor: int = 0, limit: int = 50) -> List[Any]:
        params: Dict[str, Any] = {"cursor": cursor, "limit": limit}
        return self._process_items(self._get("history/transactions", params=params))

    def instruments(self) -> Any:
        return self._get("equity/metadata/instruments")

    def cash(self) -> Any:
        return self._get("equity/account/cash")

    def portfolio(self) -> Any:
        return self._get("equity/portfolio")

    def position(self, ticker: str) -> Any:
        return self._get(f"equity/portfolio/{ticker}")

    def exchanges(self) -> Any:
        return self._get("equity/metadata/exchanges")

    def account_info(self) -> Any:
        return self._get("equity/account/info")

    def equity_orders(self) -> Any:
        return self._get("equity/orders")

    def equity_order(self, id: int) -> Any:
        return self._get(f"equity/orders/{id}")

    def equity_order_cancel(self, id: int) -> Any:
        return self._delete_url(f"equity/orders/{id}")

    def equity_order_place_limit(self, ticker: str, quantity: int, limit_price: float, time_validity: str) -> Any:
        self._validate_time_validity(time_validity)
        return self._post(
            f"equity/orders/limit",
            data={
                "quantity": quantity,
                "limitPrice": limit_price,
                "ticker": ticker,
                "timeValidity": time_validity,
            },
        )

    def equity_order_place_market(self, ticker: str, quantity: int) -> Any:
        return self._post(
            f"equity/orders/market", data={"quantity": quantity, "ticker": ticker}
        )

    def equity_order_place_stop(self, ticker: str, quantity: int, stop_price: float, time_validity: str) -> Any:
        self._validate_time_validity(time_validity)
        return self._post(
            f"equity/orders/stop",
            data={
                "quantity": quantity,
                "stopPrice": stop_price,
                "ticker": ticker,
                "timeValidity": time_validity,
            },
        )

    def equity_order_place_stop_limit(self, ticker: str, quantity: int, stop_price: float, limit_price: float, time_validity: str) -> Any:
        self._validate_time_validity(time_validity)
        return self._post(
            f"equity/orders/stop_limit",
            data={
                "quantity": quantity,
                "stopPrice": stop_price,
                "limitPrice": limit_price,
                "ticker": ticker,
                "timeValidity": time_validity,
            },
        )

    def __repr__(self) -> str:
        return "Trading212(api_key=****{}, demo={})".format(
            self._api_key[-4:], self.host == "https://demo.trading212.com"
        ) 