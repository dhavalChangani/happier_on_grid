source venv/bin/activate

python ongrid/test/test_verification.py

python -m pytest ongrid/test/test_client_integration.py -v

python -m pytest ongrid/test/test_app.py -v