from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product

class QueryTests(GraphQLTestCase):
    GRAPHQL_URL = "/graphql"

    def setUp(self):
        Product.objects.create(name="Wireless Mouse", sku="WM-001", price_cents=800)
        Product.objects.create(name="Mechanical Keyboard", sku="KB-101", price_cents=2500)

    def test_products_query(self):
        query = "{ products { name sku priceCents } }"
        response = self.query(query)
        self.assertResponseNoErrors(response)
        data = response.json()["data"]["products"]
        assert any(p["sku"] == "WM-001" for p in data)
        assert any(p["sku"] == "KB-101" for p in data)
