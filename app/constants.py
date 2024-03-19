from datetime import datetime


class Roles:
    ADMIN = "admin"
    SELLER = "seller"
    SCAMMER = "scammer"
    JUDGE = "judge"
    MODERATOR = "moderator"


class Dates:
    MARKET_EPOCH = datetime(year=2015, month=1, day=15)
