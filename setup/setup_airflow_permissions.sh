#!/bin/sh

# Create .env file to ensure that files written by Airflow are owned by the host user
echo "AIRFLOW_UID=$(id -u)" > ../.env