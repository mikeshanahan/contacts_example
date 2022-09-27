import boto3
from boto3.dynamodb.conditions import Attr, Key
from contexts.models import Contact
import os
import uuid
from fastapi import HTTPException


os.environ["CONTACTS_DATABASE"] = "contacts-db"

# Partition and sort key names
pk = "PK"
sk = "SK"


class QueryContacts:
    def __init__(self):
        self.dynamo_table = boto3.resource("dynamodb").Table(os.environ["CONTACTS_DATABASE"])
        self.pk_value = "contact"

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())

    def create_contact(
        self, 
        contact: Contact
    ):
        contact.id = self.generate_id()  # Assign it a unique ID
        create_obj = {
            pk: self.pk_value,
            sk: f"identifier#{contact.id}",  # identifier could be user id, organization id....
            "data": contact.get(),
            "has_home_number": contact.has_home_phone()
        }
        self.dynamo_table.put_item(Item=create_obj)
        return contact.id

    def update_contact(self, contact_id:str, contact: Contact):
        record = self.get_contact(contact_id)
        if not record:
            # Throw error that it doesn't exist
            raise HTTPException(status_code=400, detail="Contact not found")
        
        create_obj = {
            pk: self.pk_value,
            sk: f"identifier#{contact_id}",
            "data": contact.get(),
            "has_home_number": contact.has_home_phone()
        }
        self.dynamo_table.put_item(Item=create_obj)
        return True

    def get_contacts_page(
        self, 
        next_page=None
    ):
        if next_page is None:
            page = self.dynamo_table.query(
                KeyConditionExpression=Key(pk).eq(self.pk_value)
            )
        else:
            page = self.dynamo_table.query(
                KeyConditionExpression=Key(pk).eq(self.pk_value),
                ExclusiveStartKey=next_page
            )        
        items = [row["data"] for row in page["Items"]]
        return {"items": items, "next": page.get("LastEvaluatedKey")}

    def get_all_contacts(self):
        all_contacts = list()
        contact_page = self.get_contacts_page()
        all_contacts.extend(contact_page["items"])
        while contact_page["next"] is not None:
            contact_page = self.get_contacts_page(contact_page["next"])
            all_contacts.extend(contact_page["items"])
        return all_contacts

    def get_contact(self, contact_id:str):
        results = self.dynamo_table.query(
            KeyConditionExpression=Key(pk).eq(self.pk_value) & Key(sk).eq(f"identifier#{contact_id}")
        )
        if len(results["Items"]) == 0:
            return []
        return results["Items"][0]["data"]

    def delete_contact(self, contact_id: str):
        self.dynamo_table.delete_item(Key={
            pk: self.pk_value,
            sk: f"identifier#{contact_id}"
        })
        return True

    def get_call_page(
        self, 
        next_page=None
    ):
        if next_page is None:
            page = self.dynamo_table.query(
                KeyConditionExpression=Key(pk).eq(self.pk_value),
                FilterExpression=Attr("has_home_number").eq(True)
            )
        else:
            page = self.dynamo_table.query(
                KeyConditionExpression=Key(pk).eq(self.pk_value),
                FilterExpression=Attr("has_home_number").eq(True),
                ExclusiveStartKey=next_page
            )
        items = [row["data"] for row in page["Items"]]
        return {"items": items, "next": page.get("LastEvaluatedKey")}
        
    def get_call_list(self):
        # First get all contacts with home number
        all_contacts = list()
        contact_page = self.get_call_page()
        all_contacts.extend(contact_page["items"])
        while contact_page["next"] is not None:
            contact_page = self.get_call_page(contact_page["next"])
            all_contacts.extend(contact_page["items"])
        
        # Now reduce data to required fields
        reduced_call_list = [
            {
                "name": {
                    "first": contact["name"]["first"],
                    "middle": contact["name"]["middle"],
                    "last": contact["name"]["last"]
                },
                "phone": [
                    phone["number"] 
                    for phone in contact["phone"] 
                    if phone["type"] == "home"
                ][0],
                "id": contact.get("id")
            }
            for contact in all_contacts
        ]

        # Now sort based on last name then first name and send 'er
        return sorted(reduced_call_list, key=lambda d: (d["name"]["last"], d["name"]["first"]))
