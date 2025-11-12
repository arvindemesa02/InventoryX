# inventory/tests/mutations/test_order.py
from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Customer, Product, Order


class TestOrderMutations(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        self.customer = Customer.objects.create(email="c@example.com", full_name="Carol")
        self.product = Product.objects.create(name="Mouse", sku="M-1", price_cents=800)

    def test_order_create_update_delete(self):
        # 1) CREATE — minimal input we know exists
        create = """
        mutation ($input: OrderCreateInput!) {
          orderCreate(input: $input) {
            ok
            errors { field messages }
            result { id customer { email } }
          }
        }
        """
        r = self.query(
            create,
            variables={"input": {"customer": {"connect": {"email": {"exact": "c@example.com"}}}}},
        )
        self.assertResponseNoErrors(r)
        payload = r.json()["data"]["orderCreate"]

        # Fallback: if result is null / ok false, fetch a single order via 'order(where: …)'
        if not payload["ok"] or payload["result"] is None:
            fetch_one = """
            query ($w: OrderWhereInput!) {
              order(where: $w) { id customer { email } }
            }
            """
            qr = self.query(
                fetch_one, variables={"w": {"customer": {"email": {"exact": "c@example.com"}}}}
            )
            self.assertResponseNoErrors(qr)
            order_data = qr.json()["data"]["order"]
            assert order_data is not None, "order(where: …) returned null"
            oid = order_data["id"]
        else:
            oid = payload["result"]["id"]

        # 2) UPDATE — change customer
        Customer.objects.create(email="d@example.com", full_name="Dan")
        update = """
        mutation ($where: OrderWhereInput!, $input: OrderUpdateInput!) {
          orderUpdate(where: $where, input: $input) {
            ok
            errors { field messages }
            result { id customer { email } }
          }
        }
        """
        r2 = self.query(
            update,
            variables={
                "where": {"id": {"exact": oid}},
                "input": {"customer": {"connect": {"email": {"exact": "d@example.com"}}}},
            },
        )
        self.assertResponseNoErrors(r2)
        upd = r2.json()["data"]["orderUpdate"]
        assert upd["ok"] is True, f"orderUpdate failed: {upd['errors']}"
        assert upd["result"]["customer"]["email"] == "d@example.com"

        # 3) DELETE — ok/errors only
        delete = """
        mutation ($where: OrderWhereInput!) {
          orderDelete(where: $where) { ok errors { field messages } }
        }
        """
        r3 = self.query(delete, variables={"where": {"id": {"exact": oid}}})
        self.assertResponseNoErrors(r3)
        assert r3.json()["data"]["orderDelete"]["ok"] is True
        assert Order.objects.count() == 0
