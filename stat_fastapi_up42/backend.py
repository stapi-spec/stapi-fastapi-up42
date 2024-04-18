from fastapi import Request
from pydantic import (
    BaseModel,
    ConfigDict,
)
from stat_fastapi.exceptions import NotFoundException
from stat_fastapi.models.opportunity import (
    Opportunity,
    OpportunitySearch,
)
from stat_fastapi.models.order import Order
from stat_fastapi.models.product import Product, Provider, ProviderRole


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
        constraints=Constraints,
        links=[],
    ),
]


class StatUp42Backend:
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
        raise NotImplementedError()

    async def get_order(self, order_id: str, request: Request):
        """
        Show details for order with `order_id`.
        """
        raise NotImplementedError()
