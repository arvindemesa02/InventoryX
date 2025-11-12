from graphene_django.utils.testing import GraphQLTestCase
from inventory.models import Product, InventoryEntry


class TestInventoryEntryMutations(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def setUp(self):
        self.prod = Product.objects.create(name="Widget A", sku="W-A", price_cents=500)

    def test_inventory_entry_create_update_delete(self):
        # create (connect product)
        create = """
        mutation ($input: InventoryEntryCreateInput!) {
          inventoryEntryCreate(input: $input) {
            ok
            errors { field messages }
            result { id delta note product { sku } }
          }
        }
        """
        v = {
            "input": {
                "delta": 50,
                "note": "Initial stock",
                "product": {"connect": {"sku": {"exact": "W-A"}}},
            }
        }
        r = self.query(create, variables=v)
        self.assertResponseNoErrors(r)
        payload = r.json()["data"]["inventoryEntryCreate"]
        assert payload["ok"] is True
        eid = payload["result"]["id"]

        # update
        update = """
        mutation ($where: InventoryEntryWhereInput!, $input: InventoryEntryUpdateInput!) {
          inventoryEntryUpdate(where: $where, input: $input) {
            ok
            errors { field messages }
            result { id delta note }
          }
        }
        """
        r = self.query(
            update, variables={"where": {"id": {"exact": eid}}, "input": {"note": "Adjusted"}}
        )
        self.assertResponseNoErrors(r)
        assert r.json()["data"]["inventoryEntryUpdate"]["result"]["note"] == "Adjusted"

        # delete (no result)
        delete = """
        mutation ($where: InventoryEntryWhereInput!) {
          inventoryEntryDelete(where: $where) { ok errors { field messages } }
        }
        """
        r = self.query(delete, variables={"where": {"id": {"exact": eid}}})
        self.assertResponseNoErrors(r)
        assert r.json()["data"]["inventoryEntryDelete"]["ok"] is True
        assert InventoryEntry.objects.filter(product=self.prod).count() == 0
