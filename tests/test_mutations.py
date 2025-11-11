import json
from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product, Customer

class MutationTests(GraphQLTestCase):
    GRAPHQL_URL = "/graphql"

    def setUp(self):
        self.prod = Product.objects.create(name="Widget", sku="W-1", price_cents=200)
        self.cust = Customer.objects.create(email="c@example.com", full_name="C")

    def test_create_order_mutation(self):
        mutation = '''
        mutation CreateOrder($cust: ID!, $items: [JSONString!]!){
          createOrder(customerId:$cust, items:$items){
            order { id totalCents }
          }
        }'''
        variables = {
             "cust": str(self.cust.id),
             "items": [json.dumps({"product_id": self.prod.id, "quantity": 3})]
         }
        response = self.query(mutation, operation_name="CreateOrder", variables=variables)
        self.assertResponseNoErrors(response)
        data = response.json()["data"]["createOrder"]["order"]
        assert data["totalCents"] == 600
