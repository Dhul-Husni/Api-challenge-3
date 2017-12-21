# Api-challenge-3
[![Build Status](https://travis-ci.org/sir3n-sn/Api-challenge-3.svg?branch=master)](https://travis-ci.org/sir3n-sn/Api-challenge-3)
[![Coverage Status](https://coveralls.io/repos/github/sir3n-sn/Api-challenge-3/badge.svg?branch=development&service=github)](https://coveralls.io/github/sir3n-sn/Api-challenge-3?branch=development)

**Recipe Api:** version 1.0

**Powered by Flask!**

*Restful api that gives users power to:*
- Register, login and manage their account.
- Create, update, view and delete a category.
- Add, update, view or delete recipes.
- Enable logging of data manipulation timestamps.

## Example request with response
```
Curl
curl -X POST --header 'Content-Type: multipart/form-data' --header 'Accept: application/json' -F username=user1 -F password=useruser -F email=user%40mail.com  'http://127.0.0.1:5000/api/v1/auth/auth/register'
Request URL
http://127.0.0.1:5000/api-1.0/auth/register'
Response Body
{
  "message": "You have successfully registered"
}
Response Code
201
Response Headers
{
  "date": "Thu, 07 Dec 2017 12:53:49 GMT",
  "server": "Werkzeug/0.12.2 Python/2.7.12",
  "content-length": "87",
  "content-type": "application/json"
}
```
**Getting up and running**
#Prerequisites
- Python 3 or later
- Postgresql or any other sql database

##Dependencies
Dependencies are listed in the requirement.txt.
Ensure dependencies are up to date
*Commands*
inside a virtual environment run:
```
pip install -r requirements.txt
```
##Database
Ensure that postgresql is up and running on localhost
**command** *linux*:
```bash
service postgresql start
```
Create a postgresql database called ***api_challenge_3***
Navigate to instance/config.py 
configure the database variable in sqlalchemy_database_uri to your database user details
*example*
```
# local db
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:kali2018@localhost/challenge_3_api"
```
## Env
Create a virtual environment
**command**
```bash
pip install virtualenv
```
Navigate to api folder
```bash
DhulkifliHussein:Api-challenge-3 sir3nkali$ virtualenv -p python3 Kali
```
Activate virtual environment:

```bash
DhulkifliHussein:Api-challenge-3 sir3nkali$ source kali/bin/activate
```

## Testing
Untested code is broken code
To run the tests 

```
$ pip install nose
```

**To execute a test file**:
*Ensure you are in your virtualenvironment then run*:
```
$ nosetests
```

*Example test code*
```
def test_user_cannot_post_duplicate_entries(self):
    """When user creates two similar categories"""
    self.register_user()
    result = self.login_user()
    access_token = json.loads(result.data.decode())['Access token']
    res = self.client().post('/api-1.0/categories', data={
        "name": "Sweet pie",
        "detail": "Made by mama"
    },
                             headers=dict(Authorization=access_token)
                             )
    self.assertEqual(res.status_code, 201)
    self.assertIn('Sweet pie'.title(), str(res.data))
    # create duplicate entries
    res = self.client().post('/api-1.0/categories', data={
        "name": "Sweet pie",
        "detail": "Made by mama"
    },
                             headers=dict(Authorization=access_token)
                             )
    self.assertEqual(res.status_code, 409)
    self.assertIn('Category already exists', str(res.data))
```

**Populate and initialize the database**
*inside the virtualenv run:*
```
python3 manage.py db init

python3 manage.py db migrate

python3 manage.py db upgrade

```

##Running the Server
*Inside the virtualenv*
Start the server at localhost:5000 by running the following command:
```
python3 run.py
```

## Pagination
default page is : 1
default number of items returned per_page is : 20
The API enables pagination by passing in *page* and *per_page* as parameters

```
http://127.0.0.1:5000/api-1.0/category?page=1&per_page=10

```

## Searching

The API implements searching based on the name using a GET parameter *q* as shown below:

```
http://127.0.0.1:5000/categories?q=example
```


### Api endpoints

| url | Method|  Description| Authentication |
| --- | --- | --- | --- |
| /api-1.0/auth/login | POST | Handles POST request for /auth/login | TRUE
| /api-1.0/auth/logout | GET | Logs out a user | TRUE
| /api-1.0/auth/register | POST | Registers new user | FALSE
| /api-1.0/auth/reset-password | POST |reset user password| FALSE
| /api-1.0/auth/categories | GET | Get every category of logged in user|TRUE
| /api-1.0/auth/categories/{_id} | GET | Get category with {id} of logged in user|TRUE
| /api-1.0/auth/categories | POST | Create a new category|TRUE
| /api-1.0/auth/categories/{_id}  | PUT | Update a category with {id} of logged in user|TRUE
| /api-1.0/auth/categories/{_id} | DELETE | Delete category with {id} of logged in user|TRUE
| /api-1.0/auth/categories/{id}/recipes | POST | Creates a recipe|TRUE
| /api-1.0/auth/categories/{id}/recipes/{id} | GET | Gets a single recipe|TRUE
| /api-1.0/auth/categories/{id}/recipes/{id} | PUT | Updates a single recipe|TRUE
| /api-1.0/auth/categories/{id}/recipes/{id} | DELETE | Deletes a single recipe|TRUE


### Demo and API documentation

[https://api-recipe-challenge.herokuapp.com/](https://api-recipe-challenge.herokuapp.com/)