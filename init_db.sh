cat create_tables.sql | docker exec -i card_sorter_postgres psql -U rest_api --dbname=card_sorter

cat seed_database.sql | docker exec -i card_sorter_postgres psql -U rest_api --dbname=card_sorter