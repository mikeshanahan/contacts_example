from fastapi import FastAPI, Request
from mangum import Mangum
from typing import List

from contexts.models import Contact
from contexts.dynamo import QueryContacts

contact_query = QueryContacts()
app = FastAPI()

# Used to forward request data through AWS lambda
handler = Mangum(app)


@app.get("/contacts", response_model=List[Contact])
async def get_all_contacts():
    return contact_query.get_all_contacts()


@app.post("/contacts", response_model=str)
async def create_contact(contact: Contact):
    return contact_query.create_contact(contact)


@app.put("/contacts/{contact_id}", response_model=bool)
async def update_contact(contact_id: str, contact: Contact):
    return contact_query.update_contact(contact_id, contact)


@app.get("/contacts/{contact_id}")
async def get_contact(contact_id: str):
    # Check if the contact ID is "call-list" and handle separately...
    if contact_id == "call-list":
        return contact_query.get_call_list()
    return contact_query.get_contact(contact_id)


@app.get("/call-list", response_model=List[dict])
async def get_call_list():
    return contact_query.get_call_list()


@app.delete("/contacts/{contact_id}", response_model=bool)
async def delete_contact(contact_id: str):
    return contact_query.delete_contact(contact_id)


"""
GET /contacts?fields=number,name...,sort=desc,by=name-last,name-first
"""
