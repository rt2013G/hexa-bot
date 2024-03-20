from datetime import datetime


class Roles:
    ADMIN = "admin"
    SELLER = "seller"
    SCAMMER = "scammer"
    JUDGE = "judge"
    MODERATOR = "moderator"


class Dates:
    MARKET_EPOCH = datetime(year=2015, month=1, day=15)


class CacheLimits:
    MAX_USER_SIZE = 9999
    MAX_USERNAME_SIZE = 9999
    MAX_ROLE_SIZE = 9999
    MAX_CARD_DATA_SIZE = 499
    MAX_GUESS_GAME_RANKINGS_SIZE = 999
    MAX_SEARCH_WORD_SIZE = 9999
