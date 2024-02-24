class User():
    def __init__(self, user_data: tuple) -> None:
        self.id = user_data[0]
        self.username = None if user_data[1] is None else user_data[1].decode("utf-8")
        self.first_name = None if user_data[2] is None else user_data[2].decode("utf-8")
        self.last_name = None if user_data[3] is None else user_data[3].decode("utf-8")
        self.last_buy_post = user_data[4]
        self.last_sell_post = user_data[5]

class Feedback():
    def __init__(self, feedback_data: tuple) -> None:
        self.id = feedback_data[0]
        self.seller_id = feedback_data[1]
        self.buyer_id = feedback_data[2]
        self.contents = feedback_data[3]
        self.date = feedback_data[4]
