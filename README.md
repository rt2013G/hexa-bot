# hexa-bot <a id="title"></a>

Core bot of the Telegram groups @yugiohitatcgocg, @yugiohmarketingita and affiliates.

## Description

hexa-bot was created out of the need to manage thousands of users in a Telegram community I own, where we previously handled all requests by hand. \
The main topic of the community, as you may have guessed by the name, is the trading card game known as "Yu-Gi-Oh", which I have been interested in since 2010. \
The name of the bot comes from the card "Hexa Spirit of the Ice Barrier", a nice little fellow from the "Ice Barrier" archetype, which is the main theme across the groups. \
If you are interested in the game you are more than welcome to join, at the moment we are focused mostly on the Italian-speaking groups, but we also have an English-speaking one that you can find at @yugiohgroup

## Usage

hexa-bot is currently focused on admin-side utilities, but there are also some nice things you can do as a normal user:

- Gain access to the marketplace group via the `/seller` command
- Leave feedbacks to other users marking your feedback messages with `#feedback`
- Get all the feedbacks related to a user via the `/feedback @username` command
- Obtain the description of any card using the `/search` command

## Contributing

If you have experience with Python and the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library, you are free to clone the repo and submit a pull request. \
Please note that for linting and formatting I'm using _trunk_, you can find the configuration files in this repo.
Also please keep in mind that this bot works to serve a specific community on Telegram, if you are unsure of what needs to be done you can [join the group](#title) or read the [todo section](#todo).

## Todo <a id="todo"></a>

The bot is currently running on [an older version](https://github.com/rt2013G/YugiohHelper) that I've written almost a year ago. \
This version is not 100% working yet, here is a list of things that needs to be done before the first deployment:

- Implement the _guess the card_ minigame and possibly track games and scores in the database
- Set up CI/CD
- Fix the announce command to send announces in batches, the same way as the logging works
- Create an API to retrieve community analytics (and display them on this repo)
- Add support for auctions, claims and other important group features
- A plethora of other minor tweaks and fixes that I've written down in my personal todo list
