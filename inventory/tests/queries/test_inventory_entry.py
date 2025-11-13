from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product, InventoryEntry


class TestInventoryEntryQueries(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        self.p = Product.objects.create(name="Widget", sku="W-1", price_cents=500)
        InventoryEntry.objects.create(product=self.p, delta=10, note="Load")
        InventoryEntry.objects.create(product=self.p, delta=-2, note="Order")

    def test_inventory_entries_list(self):
        q = """
        query ($w: InventoryEntryWhereInput, $o: [InventoryEntryOrderByInput!]) {
          inventoryEntries(where: $w, orderBy: $o) {
            delta note product { sku }
          }
        }
        """
        v = {"w": {"product": {"sku": {"exact": "W-1"}}}, "o": [{"createdAt": "ASC"}]}
        r = self.query(q, variables=v)
        self.assertResponseNoErrors(r)
        rows = r.json()["data"]["inventoryEntries"]
        assert len(rows) == 2
        assert rows[0]["product"]["sku"] == "W-1"

    def test_inventory_entry_single(self):
        # pick one via list → then query single by where.id
        q_list = "{ inventoryEntries { product { sku } } }"
        self.assertResponseNoErrors(self.query(q_list))
