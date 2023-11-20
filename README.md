# CardSorterServer
Client side for the open card sorting tool. 

The full paper that was based on this tool can be found on the ACM's directory.

## How to get started

### Prerequisites
1. Python 3 \w pip
2. Docker and docker-compose
3. (Optionally) a unix-based or bashed enabled system 


### Running the development

1. Clone the repo locally (e.g. `$ git clone https://github.com/CardSorter/CardSorterServer`)
2. Cd into the root folder (e.g. `$ cd CardSorterServer`)
3. If running for the first time:
    - Create a new venv `$ python -m venv env`
    - Activate environment `$ source env/bin/activate`
    - install requirements from requirements.txt `pip install --no-cache-dir -r ./requirements.txt` (or leave it up to PyCharm)
4. Get up the database `$ docker-compose up`, database can be visually inspected from [localhost:8081](http://localhost:8081)
5. Get up the API `python app.py`

