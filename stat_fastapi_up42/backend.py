import json
from typing import cast

import requests
from fastapi import Request
from pydantic import (
    BaseModel,
    ConfigDict,
)
from stat_fastapi.exceptions import NotFoundException
from stat_fastapi.models.opportunity import (
    Opportunity,
    OpportunityProperties,
    OpportunityRequest,
)
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product, Provider, ProviderRole

from stat_fastapi_up42.settings import Settings


class Constraints(BaseModel):
    model_config = ConfigDict(extra="forbid")


PRODUCTS = [
    Product(
        id="PHR-tasking",
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

    async def get_products(self, request: Request) -> list[Product]:
        """
        Return a list of supported products.
        """
        return PRODUCTS

    async def get_product(self, product_id: str, request: Request) -> Product | None:
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

        opportunities = []

        start = cast(tuple, search.datetime)[0]
        end = cast(tuple, search.datetime)[1]

        response = requests.post(
            f"{self.settings.BASE_URL}/v2/tasking/opportunities",
            json={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": search.geometry.coordinates,
                        },
                        "properties": {
                            "acquisitionStart": start.isoformat().replace(
                                "+00:00", ".000Z"
                            ),
                            "acquisitionEnd": end.isoformat().replace(
                                "+00:00", ".000Z"
                            ),
                        },
                    }
                ],
            },
        )
        data = json.loads(response.text)

        for f in data["features"]:
            if f["properties"]["collectionName"] == search.product_id:
                opportunities.append(
                    Opportunity(
                        geometry=f["geometry"],
                        properties=OpportunityProperties(
                            datetime=(
                                f["properties"]["start_datetime"],
                                f["properties"]["end_datetime"],
                            ),
                            product_id=f["properties"]["collectionName"],
                            incidence_angle="view:incidence_angle",
                        ),
                    )
                )
        return opportunities

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
