from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product


class ProductMutationTests(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def test_product_create(self):
        mutation = """
        mutation CreateProduct($input: ProductCreateInput!) {
          productCreate(input: $input) {
            ok
            errors { field messages }
            result {
              id
              name
              sku
              priceCents
              isActive
              createdAt
            }
          }
        }
        """
        variables = {
            "input": {
                "name": "Acetaminophen 500 mg (100 ct)",
                "sku": "AP-500-100",
                "priceCents": 599,
                "isActive": True,
            }
        }
        resp = self.query(mutation, variables=variables, operation_name="CreateProduct")
        self.assertResponseNoErrors(resp)
        payload = resp.json()["data"]["productCreate"]
        assert payload["ok"] is True
        assert payload["errors"] in (None, []) or len(payload["errors"]) == 0
        assert payload["result"]["sku"] == "AP-500-100"
        assert Product.objects.filter(sku="AP-500-100").exists()

    def test_product_update_by_sku(self):
        # seed
        prod = Product.objects.create(name="Widget", sku="W-1", price_cents=200)

        mutation = """
        mutation UpdateProduct($where: ProductWhereInput!, $input: ProductUpdateInput!) {
          productUpdate(where: $where, input: $input) {
            ok
            errors { field messages }
            result {
              id
              name
              sku
              priceCents
              isActive
              updatedAt
            }
          }
        }
        """
        variables = {
            "where": {"sku": {"exact": "W-1"}},
            "input": {"priceCents": 349, "name": "Widget (new)"},
        }
        resp = self.query(mutation, variables=variables, operation_name="UpdateProduct")
        self.assertResponseNoErrors(resp)
        payload = resp.json()["data"]["productUpdate"]
        assert payload["ok"] is True
        assert payload["result"]["priceCents"] == 349
        prod.refresh_from_db()
        assert prod.price_cents == 349
        assert prod.name == "Widget (new)"

    def test_product_delete_by_sku(self):
        Product.objects.create(name="Temp", sku="TEMP-1", price_cents=100)
        mutation = """
        mutation DeleteProduct($where: ProductWhereInput!) {
          productDelete(where: $where) {
            ok
            errors { field messages }
          }
        }
        """
        variables = {"where": {"sku": {"exact": "TEMP-1"}}}
        resp = self.query(mutation, variables=variables, operation_name="DeleteProduct")
        self.assertResponseNoErrors(resp)
        payload = resp.json()["data"]["productDelete"]
        assert payload["ok"] is True
        assert not Product.objects.filter(sku="TEMP-1").exists()
