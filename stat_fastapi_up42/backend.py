import json
from datetime import datetime
from typing import cast

import pytz
from fastapi import Request
from pydantic import BaseModel, Field, ValidationError, model_validator
from shapely.geometry import shape

from stat_fastapi.exceptions import ConstraintsException, NotFoundException
from stat_fastapi.models.opportunity import (
    Opportunity,
    OpportunityProperties,
    OpportunitySearch,
)
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product, Provider, ProviderRole
from stat_fastapi_up42.models import (
    ValidatedOpportunitySearch,
)
from stat_fastapi_up42.repository import Repository
from stat_fastapi_up42.settings import Settings


class Constraints(BaseModel):
    foo: str = Field(..., description="A foo string")



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
        constraints=Constraints,
        links=[],
    ),
]


class StatUp42Backend:
    repository: Repository

    def __init__(self):
        settings = Settings.load()
        self.repository = Repository(settings.database)

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
        self, search: OpportunitySearch, request: Request
    ) -> list[Opportunity]:
        """
        Search for ordering opportunities for the given search parameters.
        """
        opportunities = []
        return opportunities

    async def create_order(self, search: OpportunitySearch, request: Request) -> Order:
        """
        Create a new order.
        """
        try:
            validated = ValidatedOpportunitySearch(**search.model_dump(by_alias=True))
        except ValidationError as exc:
            error_dict = {str(index): error for index, error in enumerate(exc.errors())}
            raise ConstraintsException(error_dict) from exc

        return self.repository.add_order(validated)

    async def get_order(self, order_id: str, request: Request):
        """
        Show details for order with `order_id`.
        """
        feature = self.repository.get_order(order_id)
        if feature is None:
            raise NotFoundException()
        return feature
