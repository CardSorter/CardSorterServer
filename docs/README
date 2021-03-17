## Register
#### Description
Registers a new user
#### Submission information
#####Method: `Post`  
#####Endpoint: `/user_endpoint?register=true`  
#####Body of the request: 
```json
{
    "username": string,
    "password": string,
    "email": string
}
```
#####Errors:  
Empty strings will result in an error message, e.g.:
```json
{'message': 'EMPTY field'}
```
Duplicate usernames and emails will result in an error message, e.g.:
```json
{'message': 'DUPLICATE field'}
```
######HTTP Status Code: `200`
#####Successful return:
```json
{
    "auth_token": string,
    "location": string
}
```
######HTTP Status Code: `200`



## Login
#### Description
Logins an existing user
#### Submission information
#####Method: `Post`  
#####Endpoint: `/user_endpoint`  
#####Body of the request: 
```json
{
    "username": string,
    "password": string
}
```
#####Errors:  
Empty strings will result in an error message, e.g.:
```json
{'message': 'EMPTY field'}
```
If the supplied username does not exist:
```json
{'message': 'USERNAME NOT FOUND'}
```
If the supplied password does not match the user's:
```json
{'message': 'INVALID PASSWORD'}
```
######HTTP Status Code: `200`
#####Successful return:
```json
{
    "auth_token": string,
    "location": string
}
```
######HTTP Status Code: `200`



## Study Creation
#### Description
Creates a study
#### Submission information
#####Method: `Post`  
#####Endpoint: `/studies_endpoint`  
#####Body of the request: 
```json
{
    "title": string,
    "description": string,
    "cards": {string:{"name": string,
                      "description": string,
                      "id": int}},
    "message": string
}
```
#####Errors:  
If the body of the request is malformed:
```json
{"error": "Cards is not an array"}
```
######HTTP Status Code: `200`
If the authorization token is wrong:
```json
{"location": string}
```
######HTTP Status Code: `401`
#####Successful return:
```json
{
    "study": {
        "abandonedNo": int,
        "completedNo": int,
        "editDate": string,
        "id": string,
        "isLive": boolean,
        "launchedDate": string,
        "share_url": string,
        "title": string,
        "url_to_study": string
    }
}
```
######HTTP Status Code: `200`



## Get user's name
#### Description
Returns the user's name that corresponds to the authorization token
provided
#### Submission information
#####Method: `Get`  
#####Endpoint: `/studies_endpoint?username=true`  
#####Errors:  
If the authorization token is wrong:
```json
{"location": string}
```
######HTTP Status Code: `401`
#####Successful return:
```json
{"username": string}
```
######HTTP Status Code: `200`



## Get study's clusters
#### Description
Returns the clusters of the study with the specified id, by taking
into account the user's id through the authorization token
#### Submission information
#####Method: `Get`  
#####Endpoint: `/studies_endpoint?id={study's id number}&clusters=true`  
#####Errors:  
If the authorization token is wrong:
```json
{"location": string}
```
######HTTP Status Code: `401`
If the user hasn't made the study that he requested:
```json
{'message': 'INVALID STUDY'}
```
######HTTP Status Code: `200`
If the clusters of the study cannot be calculated because of data 
scarcity:
```json
{'message': 'not enough data'}
```
######HTTP Status Code: `200`
If the clusters are being calculated:
```json
{'message': 'calculating'}
```
######HTTP Status Code: `200`
#####Successful return:
```json
{
    "clusters": {
        "children": [
            {
                "children": array,
                "distance": float,
                "hierarchy": int
            },
        ],
        "distance": float,
        "hierarchy": int
    }
}
```
######HTTP Status Code: `200`



## Get study
#### Description
Returns the study with the specified id, by taking
into account the user's id through the authorization token
#### Submission information
#####Method: `Get`  
#####Endpoint: `/studies_endpoint?id={study's id number}`  
#####Errors:  
If the authorization token is wrong:
```json
{"location": string}
```
######HTTP Status Code: `401`
If the user hasn't made the study that he requested:
```json
{'message': 'INVALID STUDY'}
```
######HTTP Status Code: `200`
If there are no participants:
```json
{
    "study": {
        "isLive": boolean,
        "launchedDate": string,
        "participants": int,
        "shareUrl": string,
        "title": string
    }
}
```
######HTTP Status Code: `200`
#####Successful return:
```json
{
    "study": {
        "abandoned_no": int,
        "cards": {
            "average": string,
            "data": [[string, int, [string, string], [float, float]]],
            "sorted": int,
            "total": int
        },
        "categories": {
            "data": [[string, int, [string, string], int, [float, float]]],
            "merged": int,
            "similar": int,
            "similarity": string,
            "total": int
        },
        "completed_no": string,
        "edit_date": int,
        "end_date": string,
        "id": int,
        "is_live": boolean,
        "launched_date": string,
        "message_text": boolean,
        "participants": {
            "completed": int,
            "completion": float,
            "data": [[string, int, string, int]],
            "total": int
        },
        "shareUrl": string,
        "similarityMatrix": [[string], [int, string]],
        "title": string
    }
}
```
######HTTP Status Code: `200`



## Get all studies
#### Description
Returns all studies of a user by taking into account the
user's id through the authorization token
#### Submission information
#####Method: `Get`  
#####Endpoint: `/studies_endpoint`  
#####Errors:  
If the authorization token is wrong:
```json
{"location": string}
```
######HTTP Status Code: `401`
#####Successful return:
```json
{
    "studies": [
        [
            int,
            string,
            int,
            int,
            string,
            boolean,
            string,
            boolean
        ]
    ]
}
```
######HTTP Status Code: `200`



## Get all cards of a study
#### Description
Returns the cards of a study
#### Submission information
#####Method: `Get`  
#####Endpoint: `/sort_endpoint?study_id={study's id}&cards=true`  
#####Errors:  
If the study_id parameter of the request is malformed
or the study does not exist:
```json
{"error": {"message": "STUDY NOT FOUND"}}
```
######HTTP Status Code: `404`
#####Successful return:
```json
{
    "cards": [
        {
            "description": string,
            "id": int,
            "name": string
        }
    ]
}
```
######HTTP Status Code: `200`



## Create a sorting of a study
#### Description
Creates a sorting of the study with the id specified
#### Submission information
#####Method: `Post`  
#####Endpoint: `/sort_endpoint`  
#####Body of the request: 
```json
{
    "studyID": string,
    "categories": {
        string: {
            "title": string,
            "cards": [int]
        }
    },
    "notSorted": [int],
    "time": int,
    "comment": string
}
```
#####Errors:  
If the studyID does not correspond to an existing study:
```json
{"error": {"message": "STUDY NOT FOUND"}}
```
######HTTP Status Code: `200`
#####Successful return:
```json
[string]
```
######HTTP Status Code: `200`
