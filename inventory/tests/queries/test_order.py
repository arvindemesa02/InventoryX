from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product, Customer, Order, OrderItem


class TestOrderQueries(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        self.prod = Product.objects.create(name="Mouse", sku="M-1", price_cents=800)
        self.cust = Customer.objects.create(email="c@example.com", full_name="C")
        self.order = Order.objects.create(customer=self.cust)
        OrderItem.objects.create(
            order=self.order, product=self.prod, quantity=2, unit_price_cents=800
        )

    def test_orders_list(self):
        q = """
        query ($o: [OrderOrderByInput!]) {
          orders(orderBy: $o) {
            id
            customer { email }
          }
        }
        """
        r = self.query(q, variables={"o": [{"createdAt": "DESC"}]})
        self.assertResponseNoErrors(r)
        data = r.json()["data"]["orders"]
        assert len(data) >= 1
        assert data[0]["customer"]["email"] == "c@example.com"

    def test_order_single_with_items(self):
        # get id via small query
        q_ids = "{ orders { id } }"
        rid = self.query(q_ids).json()["data"]["orders"][0]["id"]

        q = """
        query ($w: OrderWhereInput!) {
          order(where: $w) {
            id
            customer { email }
            items(orderBy: [{ createdAt: ASC }]) {
              edges {
                node {
                  quantity
                  unitPriceCents
                  product { sku }
                }
              }
            }
          }
        }
        """
        r = self.query(q, variables={"w": {"id": {"exact": rid}}})
        self.assertResponseNoErrors(r)
        data = r.json()["data"]["order"]
        assert data["customer"]["email"] == "c@example.com"
        nodes = [e["node"] for e in data["items"]["edges"]]
        assert any(n["product"]["sku"] == "M-1" and n["quantity"] >= 1 for n in nodes)
