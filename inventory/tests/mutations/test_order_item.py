from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product, Customer, Order, OrderItem


class TestOrderItemMutations(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        # Create backing records via ORM (simpler) and get the GraphQL ID via a query
        self.product = Product.objects.create(name="Mouse", sku="M-1", price_cents=800)
        self.customer = Customer.objects.create(email="c@example.com", full_name="C")
        self.order = Order.objects.create(customer=self.customer)

        # Grab the GraphQL global id for the order
        q = """
        query ($w: OrderWhereInput!) {
          orders(where: $w, orderBy: [{ createdAt: DESC }]) { id }
        }
        """
        r = self.query(q, variables={"w": {"customer": {"email": {"exact": "c@example.com"}}}})
        self.assertResponseNoErrors(r)
        self.order_id = r.json()["data"]["orders"][0]["id"]

    def test_order_item_create_update_delete(self):
        # create item
        create = """
        mutation ($input: OrderItemCreateInput!) {
          orderItemCreate(input: $input) {
            ok
            errors { field messages }
            result { id quantity unitPriceCents product { sku } order { id } }
          }
        }
        """
        v = {
            "input": {
                "quantity": 2,
                "unitPriceCents": 800,
                "product": {"connect": {"sku": {"exact": "M-1"}}},
                "order": {"connect": {"id": {"exact": self.order_id}}},
            }
        }
        r = self.query(create, variables=v)
        self.assertResponseNoErrors(r)
        payload = r.json()["data"]["orderItemCreate"]
        assert payload["ok"] is True, f"orderItemCreate failed: {payload['errors']}"
        iid = payload["result"]["id"]

        # update item
        update = """
        mutation ($where: OrderItemWhereInput!, $input: OrderItemUpdateInput!) {
          orderItemUpdate(where: $where, input: $input) {
            ok
            errors { field messages }
            result { id quantity unitPriceCents }
          }
        }
        """
        r = self.query(
            update, variables={"where": {"id": {"exact": iid}}, "input": {"quantity": 3}}
        )
        self.assertResponseNoErrors(r)
        assert r.json()["data"]["orderItemUpdate"]["result"]["quantity"] == 3

        # delete item
        delete = """
        mutation ($where: OrderItemWhereInput!) {
          orderItemDelete(where: $where) { ok errors { field messages } }
        }
        """
        r = self.query(delete, variables={"where": {"id": {"exact": iid}}})
        self.assertResponseNoErrors(r)
        assert r.json()["data"]["orderItemDelete"]["ok"] is True
        assert OrderItem.objects.count() == 0
