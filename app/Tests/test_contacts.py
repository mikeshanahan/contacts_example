from contexts.models import Contact
from contexts.dynamo import QueryContacts
from copy import deepcopy


query = QueryContacts()

class TestQueryContacts:
    def test_update_create_delete(self):
        # Create the contact object from the example json payload
        example_contact = {
            "name": {
                "first": "Mike",
                "middle": "Me",
                "last": "Bob"
            },
            "address": {
                "street": "123 first",
                "city": "Rockstown",
                "state": "NY",
                "zip": "12345"
            },
            "phone": [
                {
                    "number": "123456",
                    "type": "home"
                }
            ],
            "email": "email@email.com"
        }
        new_contact = Contact(**example_contact)

        # Create it
        contact_id = query.create_contact(new_contact)

        # Check that it exists
        results = query.get_contact(contact_id)
        results.pop("id")  # Original did not have id so remove before comparison
        assert results
        assert results == example_contact

        # Define an updated contact payload
        updated_payload = {
            "name": {
                "first": "Different Name",
                "middle": "Me",
                "last": "Bob"
            },
            "address": {
                "street": "123 first",
                "city": "Rockstown",
                "state": "NY",
                "zip": "12345"
            },
            "phone": [
                {
                    "number": "123456",
                    "type": "home"
                }
            ],
            "email": "different@email.com"
        }
        
        # Create the new contact model
        updated_contact = Contact(**updated_payload)

        # Send the update
        res = query.update_contact(contact_id, updated_contact)
        assert res   # returns True when successful

        # Get the updated version and check
        result = query.get_contact(contact_id)
        result.pop("id")
        assert result == updated_payload

        # Delete it
        res = query.delete_contact(contact_id)
        assert res

        # Check that it is deleted
        res = query.get_contact(contact_id)
        assert not res

    def test_cant_update_non_existing_contact(self):
        example_contact = {
            "name": {
                "first": "Mike",
                "middle": "Me",
                "last": "Bob"
            },
            "address": {
                "street": "123 first",
                "city": "Rockstown",
                "state": "NY",
                "zip": "12345"
            },
            "phone": [
                {
                    "number": "123456",
                    "type": "home"
                }
            ],
            "email": "email@email.com"
        }
        contact = Contact(**example_contact)
        try:
            query.update_contact("thisdoesnotexist", contact)
            raise Exception("Able to update contact that did not exist")
        except:
            pass

    def test_get_all_contacts(self):
        # Make sure there is at least 1 contact that exists
        example_contact = {
            "name": {
                "first": "Mike",
                "middle": "Me",
                "last": "Bob"
            },
            "address": {
                "street": "123 first",
                "city": "Rockstown",
                "state": "NY",
                "zip": "12345"
            },
            "phone": [
                {
                    "number": "123456",
                    "type": "home"
                }
            ],
            "email": "email@email.com"
        }
        contact_id = query.create_contact(Contact(**example_contact))

        # Pull all contacts and check
        all_contacts = query.get_all_contacts()
        assert all_contacts
        assert any(contact.get("id") == contact_id for contact in all_contacts)

        # Delete the created contact
        query.delete_contact(contact_id)

    def test_sorted_calls_only_get_home_numbers(self):
        # Create a home number and mobile number contact
        example_contact = {
            "name": {
                "first": "Mike",
                "middle": "Me",
                "last": "Bob"
            },
            "address": {
                "street": "123 first",
                "city": "Rockstown",
                "state": "NY",
                "zip": "12345"
            },
            "phone": [
                {
                    "number": "123456",
                    "type": "home"
                }
            ],
            "email": "email@email.com"
        }
        example_contact_2 = deepcopy(example_contact)
        example_contact_2["phone"][0]["type"] = "mobile"

        id_1 = query.create_contact(Contact(**example_contact))
        id_2 = query.create_contact(Contact(**example_contact_2))

        # Expect to only see the home number, not the mobile number
        call_list = query.get_call_list()

        assert any(contact["id"] == id_1 for contact in call_list)
        assert not any(contact["id"] == id_2 for contact in call_list)

        # Cleanup
        query.delete_contact(id_1)
        query.delete_contact(id_2)

    def test_get_sorted_calls(self):
        example_contact = {
            "name": {
                "first": "Mike",
                "middle": "Me",
                "last": "Bob"
            },
            "address": {
                "street": "123 first",
                "city": "Rockstown",
                "state": "NY",
                "zip": "12345"
            },
            "phone": [
                {
                    "number": "123456",
                    "type": "home"
                }
            ],
            "email": "email@email.com"
        }
        # Create some contacts with different first and last names
        example_contact_2 = deepcopy(example_contact)
        example_contact_2["name"]["last"] = "Zob"

        example_contact_3 = deepcopy(example_contact)
        example_contact_3["name"]["last"] = "Zob"
        example_contact_3["name"]["first"] = "Roy"

        example_contact_4 = deepcopy(example_contact)
        example_contact_4["name"]["first"] = "Anthony"
        example_contact_4["name"]["last"] = "Middlename"
        
        # Actually Make them
        id_1 = query.create_contact(Contact(**example_contact))
        id_2 = query.create_contact(Contact(**example_contact_2))
        id_3 = query.create_contact(Contact(**example_contact_3))
        id_4 = query.create_contact(Contact(**example_contact_4))

        # Get the sorted calls
        call_list = query.get_call_list()

        # Subset the call list to only these 4 but maintain order
        sub_call_list = [contact for contact in call_list if contact["id"] in [id_1, id_2, id_3, id_4]]

        # Check that they match the expected order (order by last name then first name)
        # Mike Bob, Anthony Middlename, Mike Zob, Roy Zob

        assert sub_call_list[0]["name"]["last"] == "Bob"
        assert sub_call_list[0]["name"]["first"] == "Mike"

        assert sub_call_list[1]["name"]["last"] == "Middlename"
        assert sub_call_list[1]["name"]["first"] == "Anthony"

        assert sub_call_list[2]["name"]["last"] == "Zob"
        assert sub_call_list[2]["name"]["first"] == "Mike"

        assert sub_call_list[3]["name"]["last"] == "Zob"
        assert sub_call_list[3]["name"]["first"] == "Roy"

        # Cleanup
        query.delete_contact(id_1)
        query.delete_contact(id_2)
        query.delete_contact(id_3)
        query.delete_contact(id_4)
