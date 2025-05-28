# Airflow Setup Notes

## Background

The default `airflow-init` service in `docker-compose.yaml` was originally set up to perform various setup steps, including file permission checks and directory initialization. However, in our current Docker environment (likely older or more limited), the complex bash script caused issues and was unreliable.

To keep the setup simple and robust, we opted to **remove unnecessary logic from `docker-compose.yaml`** and perform required initialization manually, only once.

## One-time Initialization Steps

Run these commands after cloning the repo and before starting the containers:

```bash
# Step 1: Initialize the database
docker-compose run --rm airflow-cli airflow db migrate

# Step 2: Create an admin user
docker-compose run --rm airflow-cli airflow users create \
  --username admin --firstname Admin --lastname User \
  --role Admin --email admin@example.com --password admin
```
After this, you can simply start the stack using:
```bash
docker-compose up -d
```
Notes  
These steps only need to be done once, unless the database is reset.
