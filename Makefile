run:
	@python hexa_bot.py
webhook:
	@python hexa_bot.py webhook
req:
	@pip freeze > requirements.txt
test:
	@python -m unittest discover -v -s tests/ -p "*test.py" || true