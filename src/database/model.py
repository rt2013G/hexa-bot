class User():
    def __init__(self, user_data: tuple) -> None:
        self.id = user_data[0]
        self.username = user_data[1]
        self.first_name = user_data[2]
        self.last_name = user_data[3]
        self.is_seller = user_data[4]
        self.last_buy_post = user_data[5]
        self.last_sell_post = user_data[6]

    
