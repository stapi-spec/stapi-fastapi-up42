import http.client
import json

from fastapi import Request
from pydantic import (
    BaseModel,
    ConfigDict,
)
from stat_fastapi.exceptions import NotFoundException
from stat_fastapi.models.opportunity import (
    Opportunity,
    OpportunityRequest,
)
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product, Provider, ProviderRole
from stat_fastapi_up42.settings import Settings


class Constraints(BaseModel):
    model_config = ConfigDict(extra="forbid")


PRODUCTS = [
    Product(
        id="some-product",
        description="Some product",
        license="propietary",
        providers=[
            Provider(
                name="ACME",
                roles=[
                    ProviderRole.licensor,
                    ProviderRole.producer,
                    ProviderRole.processor,
                    ProviderRole.host,
                ],
                url="http://acme.example.com",
            )
        ],
        parameters=Constraints,
        links=[],
    ),
]


class StatUp42Backend:

    def __init__(self):
        self.settings = Settings.load()

    def products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return PRODUCTS

    def product(self, product_id: str, request: Request) -> Product | None:
        """
        Return the product identified by `product_id` or `None` if it isn't
        supported.
        """
        try:
            return next((product for product in PRODUCTS if product.id == product_id))
        except StopIteration as exc:
            raise NotFoundException() from exc

    async def search_opportunities(
        self, search: OpportunityRequest, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the given search parameters.
        """
        # Specify the server and port number

        breakpoint()

        conn = http.client.HTTPConnection(self.settings.BASE_URL, 443)
        conn.request(
            "POST",
            "/v2/tasking/opportunities",
            body=json.dumps({"key": "value"}),
            headers={"Content-type": "application/json", "Accept": "application/json"},
        )
        response = conn.getresponse()
        data = response.read().decode()

        print("Status:", response.status)
        print("Response:", data)

        conn.close()

        return [
            f
            for f in data["features"]
            if f["properties"]["collectionName"] == search.product_id
        ]

    async def create_order(self, search: OpportunityRequest, request: Request) -> Order:
        """
        Create a new order.
        """
        raise NotImplementedError()

    async def get_order(self, order_id: str, request: Request):
        """
        Show details for order with `order_id`.
        """
        raise NotImplementedError()
