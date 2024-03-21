from datetime import datetime

from app.config import get_market_group_link


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
    MAX_FEEDBACK_SIZE = 1999


class GuessGame:
    GAME_LENGTH = 10


class MessageLimits:
    MAX_USERNAME_LENGTH = 32


class Messages:
    USER_NOT_FOUND = "Utente non trovato!"
    USER_NOT_FOUND_WITH_MENTION = (
        "Utente non trovato! Assicurati di aver scritto correttamente lo @username."
    )
    USER_NOT_SELLER = "L'utente NON è un venditore!"
    START = f"""Benvenuto sul gruppo Yu-Gi-Oh ITA Main.
Per entrare nel gruppo market segui questo link: {get_market_group_link()}.\n
Ricorda di leggere le regole! Solo i venditori approvati possono vendere sul gruppo.
Se vuoi diventare venditore, usa il comando /seller.\n
Ricorda che in ogni caso, puoi effettuare solo 1 post di vendita e 1 post di acquisto al giorno."""
    GDPR = """Al fine di limitare il numero di truffatori, per autenticarsi come seller è necessario fornire un identificativo.
Se non si vuole vendere sul gruppo, NON è ovviamente obbligatorio autenticarsi.
Il video inviatoci è visibile soltanto agli amministratori del gruppo market, e non viene salvato dal bot. Non è condiviso con nessun altro.
Il video non viene utilizzato per nessuno scopo ECCETTO in caso di truffa da parte di un venditore, in quel caso potrebbe essere utilizzato al fine di risalire all'identità del truffatore.
"""
