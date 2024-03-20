debug:
	@python hexa_bot.py polling debug
webhook:
	@python hexa_bot.py webhook
migrate:
	@python hexa_bot.py migrate
req:
	@pip freeze > requirements.txt
test:
	@python -m unittest discover -v -s tests/ -p "*test.py" || true
testdb:
	@python -m unittest discover -v -s tests/database -p "*test.py" || true