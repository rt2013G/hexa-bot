run:
	@python hexa_bot.py deploy
debug:
	@python hexa_bot.py debug
req:
	@pip freeze > requirements.txt
test: