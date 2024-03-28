from . import admin_commands, chats, conversations, user_commands

handlers = {
    0: chats.service_handlers(),
    1: admin_commands.role_handlers()
    + admin_commands.helpers_handlers()
    + admin_commands.market_handlers(),
    2: user_commands.info_handlers() + user_commands.market_handlers(),
    3: chats.market_handlers(),
    4: conversations.seller_auth_handlers(),
    5: admin_commands.market_plus_handlers(),
    6: conversations.guess_game_conv_handler(),
    7: conversations.emoji_game_conv_handler(),
}
