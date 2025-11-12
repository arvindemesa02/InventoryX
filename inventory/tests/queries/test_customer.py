from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Customer


class TestCustomerQueries(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        Customer.objects.create(email="a@example.com", full_name="Alice")
        Customer.objects.create(email="b@example.com", full_name="Bob")

    def test_customers_list(self):
        q = "{ customers { id email fullName } }"
        r = self.query(q)
        self.assertResponseNoErrors(r)
        emails = [c["email"] for c in r.json()["data"]["customers"]]
        assert {"a@example.com", "b@example.com"} <= set(emails)

    def test_customer_single(self):
        q = "query ($w: CustomerWhereInput!){ customer(where:$w){ id email fullName } }"
        r = self.query(q, variables={"w": {"email": {"exact": "a@example.com"}}})
        self.assertResponseNoErrors(r)
        assert r.json()["data"]["customer"]["email"] == "a@example.com"
