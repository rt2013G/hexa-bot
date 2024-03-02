from datetime import datetime


class User:
    def __init__(self, user_data: tuple) -> None:
        self.id: int = int(user_data[0])
        self.username: str | None = (
            None if user_data[1] is None else user_data[1].decode("utf-8")
        )
        self.first_name: str | None = (
            None if user_data[2] is None else user_data[2].decode("utf-8")
        )
        self.last_name: str | None = (
            None if user_data[3] is None else user_data[3].decode("utf-8")
        )
        self.last_buy_post: datetime = user_data[4]
        self.last_sell_post: datetime = user_data[5]


class Feedback:
    def __init__(self, feedback_data: tuple) -> None:
        self.id: int = feedback_data[0]
        self.seller_id: int = feedback_data[1]
        self.buyer_id: int = feedback_data[2]
        self.contents: str = feedback_data[3].decode("utf-8")
        self.date: datetime = feedback_data[4]
