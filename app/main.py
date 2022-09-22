from fastapi import FastAPI, Request
from typing import List

from contexts.models import Contact
from contexts.dynamo import QueryContacts

contact_query = QueryContacts()
app = FastAPI()


@app.get("/contacts")
async def get_all_contacts():
    return contact_query.get_all_contacts()


@app.post("/contacts")
async def create_contact(contact: Contact):
    return contact_query.create_contact(contact)


@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: str, contact: Contact):
    return contact_query.update_contact(contact_id, contact)


@app.get("/contacts/{contact_id}")
async def get_contact(contact_id: str):
    # Check if the contact ID is "call-list" and handle separately...
    if contact_id == "call-list":
        return contact_query.get_call_list()
    return contact_query.get_contact(contact_id)


@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str):
    return contact_query.delete_contact(contact_id)
