from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product


class QueryTests(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        Product.objects.create(name="Wireless Mouse", sku="WM-001", price_cents=800)
        Product.objects.create(name="Mechanical Keyboard", sku="KB-101", price_cents=2500)
        Product.objects.create(name="Budget Mouse", sku="BM-010", price_cents=500, is_active=False)

    def test_products_simple_list(self):
        query = """
        {
          products {
            name
            sku
            priceCents
          }
        }
        """
        response = self.query(query)
        self.assertResponseNoErrors(response)
        data = response.json()["data"]["products"]
        assert any(p["sku"] == "WM-001" for p in data)
        assert any(p["sku"] == "KB-101" for p in data)

    def test_products_with_filters_and_order(self):
        query = """
        query ListProducts($where: ProductWhereInput, $orderBy: [ProductOrderByInput!]) {
          products(where: $where, orderBy: $orderBy) {
            sku
            priceCents
            isActive
            createdAt
          }
        }
        """
        variables = {
            "where": {"priceCents": {"lte": 2000}, "isActive": {"exact": True}},
            "orderBy": [{"createdAt": "DESC"}],
        }
        response = self.query(query, variables=variables, operation_name="ListProducts")
        self.assertResponseNoErrors(response)
        rows = response.json()["data"]["products"]
        assert all(row["priceCents"] <= 2000 for row in rows)
        assert all(row["isActive"] is True for row in rows)

    def test_single_product_where(self):
        query = """
        query GetProduct($where: ProductWhereInput!) {
          product(where: $where) {
            id
            name
            sku
            priceCents
            isActive
          }
        }
        """
        variables = {"where": {"sku": {"exact": "WM-001"}}}
        response = self.query(query, variables=variables, operation_name="GetProduct")
        self.assertResponseNoErrors(response)
        node = response.json()["data"]["product"]
        assert node["sku"] == "WM-001"
