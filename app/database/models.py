from datetime import datetime
from typing import Literal

type Role = Literal["admin", "seller", "scammer", "judge", "moderator"]

class User:
    def __init__(self, user_data: tuple) -> None:
        self.id: int = int(user_data[0])
        self.username: str | None = None
        if user_data[1]:
            try:
                self.username = user_data[1].decode("utf-8")
            except AttributeError:
                self.username = user_data[1]

        self.first_name: str | None = None
        if user_data[2]:
            try:
                self.first_name = user_data[2].decode("utf-8")
            except AttributeError:
                self.first_name = user_data[2]

        self.last_name: str | None = None
        if user_data[3]:
            try:
                self.last_name = user_data[3].decode("utf-8")
            except AttributeError:
                self.last_name = user_data[3]

        self.last_buy_post: datetime = user_data[4]
        self.last_sell_post: datetime = user_data[5]

    def __eq__(self, __value: object) -> bool:
        if __value is None:
            return False
        return bool(self.id == __value.id)


class Feedback:
    def __init__(self, feedback_data: tuple) -> None:
        self.id: int = feedback_data[0]
        self.seller_id: int = feedback_data[1]
        self.buyer_id: int = feedback_data[2]
        try:
            self.contents: str = feedback_data[3].decode("utf-8")
        except AttributeError:
            self.contents: str = feedback_data[3]
        self.date: datetime = feedback_data[4]


class MarketPlusPost:
    def __init__(self, post_data: tuple) -> None:
        self.message_id: int = int(post_data[0])
        self.end_date: datetime = post_data[1]
        self.last_posted_date: datetime = post_data[2]
        self.last_posted_market_id: int | None = (
            int(post_data[3]) if post_data[3] is not None else None
        )