Author: Mike Shanahan
September 22, 2022

TECH STACK:

- Python3.9 using pipenv
- API: FastAPI with Pydantic
- Database: DynamoDB with Single Table Design
- Hosting: (would be) API Gateway with Lambda running with Mangum - Totally Serverless :)

TO RUN:
* There must be a dynamodb table with the name "contacts-db", partition key of "PK" and sort key of "SK" (both string type)

You can either link this to an existing deployment and just update the aws connection and table name
or deploy it using cloudformation using the template provided (only dynamo included).

More complicatedly... you could run dynamodb locally using a docker container and just change the boto3 reference to use
localhost instead of connecting to an account if you don't want to use an AWS account.

To configure the AWS connection you would need the AWS CLI, once you have that you can run
```sh
aws configure
-enter access key-
-enter secret key-
-enter region-
-enter return format-
```

Once the dynamodb table is accessible running the app only needs the following:

```sh
cd app/
pipenv install
pipenv shell
uvicorn main:app --reload
```

Testing the database layer can be done with pytest
```sh
cd app/
pytest Tests/test_contacts.py -v
```

Addt. Info:

Reviewing SQL is boring, exploring single table design is fun, but SQL would have worked too ->

contact table -> id, first_name, middle_name, last_name....
phone table -> contact_id, type, number

get all -> SELECT * FROM contacts LEFT JOIN phone ON phone.contact_id=contacts.id;
create -> INSERT INTO...
get -> SELECT... WHERE
update -> UPDATE... WHERE...
delete -> DELETE... WHERE...
call list -> SELECT... LEFT JOIN phone ON phone.... WHERE phone.type = 'home'

TODOS
Security and middleware
Depending on the actually application investigate access patterns (right now there is hot partition on "contact")
Finish deployment/CICD
Abstract the database communication further away from the contacts crudding
