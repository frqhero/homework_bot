class Not200StatusCodeResponse(Exception):
    """200."""

    def __init__(self, msg='Wrong status code response. Expected 200.'):
        """init."""
        super().__init__(msg)


class BadResponse(Exception):
    """Bad response."""

    pass


class BotNotSendingStuff(Exception):
    """Bot is not sending stuff."""

    def __init__(self, msg='Oops, the bot is down.'):
        """init."""
        super().__init__(msg)


class ApiUnreachable(Exception):
    """Api is out of reach."""

    def __init__(self, endpoint='The api'):
        """init."""
        super().__init__(f'{endpoint} is down.')
