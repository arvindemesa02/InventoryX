from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product, Customer, Order, OrderItem


class TestOrderItemQueries(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        p = Product.objects.create(name="Mouse", sku="M-1", price_cents=800)
        c = Customer.objects.create(email="c@example.com", full_name="C")
        o = Order.objects.create(customer=c)
        OrderItem.objects.create(order=o, product=p, quantity=2, unit_price_cents=800)

    def test_order_items_list_filtered(self):
        q = """
        query ($w: OrderItemWhereInput) {
          orderItems(where: $w) {
            quantity unitPriceCents product { sku } order { id }
          }
        }
        """
        r = self.query(q, variables={"w": {"product": {"sku": {"exact": "M-1"}}}})
        self.assertResponseNoErrors(r)
        rows = r.json()["data"]["orderItems"]
        assert len(rows) >= 1
        assert rows[0]["product"]["sku"] == "M-1"
