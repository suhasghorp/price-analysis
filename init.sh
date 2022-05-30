#!/bin/sh
set -e

echo "Starting SSH ..."
service ssh start

streamlit run app.py