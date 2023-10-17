class User:
    """
    User details.
    """

    def __init__(self, name, email, organization, subscriptions):
        #: The name of the user, str
        self.name = name
        #: The email of the user, str
        self.email = email
        #: The organization of the user, see :py:class:`Organization`
        self.organization = organization
        #: The subscriptions of the user, see :py:class:`Subscription`
        self.subscriptions = subscriptions

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<User: name=\"{self.name}\", email=\"{self.email}\", organization={self.organization}, " \
               f"subscriptions={self.subscriptions}>"


class Organization:
    """
    Organization details.
    """

    def __init__(self, name, account_manager):
        #: The name of the organization
        self.name = name
        #: The account manager of the organization
        self.account_manager = account_manager

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<Organization: name=\"{self.name}\", account_manager={self.account_manager}>"


class AccountManager:
    """
    Account manager details.
    """

    def __init__(self, name, email):
        #: The name of the account manager
        self.name = name
        #: The email of the account manager
        self.email = email

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<AccountManager: name=\"{self.name}\", email=\"{self.email}\">"
