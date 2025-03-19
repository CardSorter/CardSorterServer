# CardSorterServer
Client side for the open card sorting tool. 

The full paper this tool was based on can be found on the [ACM's directory](https://dl.acm.org/doi/abs/10.1145/3437120.3437279)
Original authors: [Georgios Melissourgos](https://scholar.google.com/citations?user=ZcEnV9oAAAAJ&hl=en&oi=ao), [Christos Katsanos](https://scholar.google.com/citations?hl=en&user=_6k57BEAAAAJ)

## How to get started

### Prerequisites
1. Python 3 \w pip
2. Docker and docker-compose
3. (Optionally) a unix-based or bash enabled system 


### Running the development

1. Clone the repo locally (e.g. `$ git clone https://github.com/CardSorter/CardSorterServer`)
2. Cd into the root folder (e.g. `$ cd CardSorterServer`)
3. If running for the first time:
    - Create a new venv `$ python -m venv env`
    - Activate environment `$ source env/bin/activate`
    - install requirements from requirements.txt `pip install --no-cache-dir -r ./requirements.txt` (or leave it up to PyCharm)
4. Get up the database `$ docker-compose up`, database can be visually inspected from [localhost:8081](http://localhost:8081)
5. Get up the API `python app.py`

## Publications
- [Original paper](https://dl.acm.org/profile/99659688318) —[Georgios Melissourgos](https://scholar.google.com/citations?user=ZcEnV9oAAAAJ&hl=en&oi=ao), [Christos Katsanos](https://scholar.google.com/citations?hl=en&user=_6k57BEAAAAJ)
- [Functionality improvements](https://ikee.lib.auth.gr/record/354705/files/KYRIACOU.pdf) —Panagiotis Kyriacou