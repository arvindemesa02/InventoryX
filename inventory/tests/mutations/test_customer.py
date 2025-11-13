from graphene_django.utils.testing import GraphQLTestCase


class TestCustomerMutations(GraphQLTestCase):
    GRAPHQL_URL = "/graphql/"

    def test_customer_create_update_delete(self):
        # create
        create = """
        mutation ($input: CustomerCreateInput!) {
          customerCreate(input: $input) {
            ok
            errors { field messages }
            result { id email fullName }
          }
        }
        """
        r = self.query(
            create, variables={"input": {"email": "jane@example.com", "fullName": "Jane Roe"}}
        )
        self.assertResponseNoErrors(r)
        payload = r.json()["data"]["customerCreate"]
        assert payload["ok"] is True
        cid = payload["result"]["id"]

        # update
        update = """
        mutation ($where: CustomerWhereInput!, $input: CustomerUpdateInput!) {
          customerUpdate(where: $where, input: $input) {
            ok
            errors { field messages }
            result { id email fullName }
          }
        }
        """
        r = self.query(
            update, variables={"where": {"id": {"exact": cid}}, "input": {"fullName": "Jane R."}}
        )
        self.assertResponseNoErrors(r)
        assert r.json()["data"]["customerUpdate"]["result"]["fullName"] == "Jane R."

        # delete (no result)
        delete = """
        mutation ($where: CustomerWhereInput!) {
          customerDelete(where: $where) { ok errors { field messages } }
        }
        """
        r = self.query(delete, variables={"where": {"id": {"exact": cid}}})
        self.assertResponseNoErrors(r)
        assert r.json()["data"]["customerDelete"]["ok"] is True
