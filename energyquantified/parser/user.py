from .metadata import parse_subscription
from ..user import AccountManager, Organization, User


def parse_user(json):
    """
    Parse a JSON response from the server into a User object.
    """
    name = json.get("name")
    email = json.get("email")
    organization = json.get("organization")
    if organization:
        organization = parse_organization(organization)
    subscriptions = json.get("subscriptions")
    if subscriptions:
        subscriptions = parse_subscriptions(subscriptions)
    return User(name, email, organization, subscriptions)


def parse_organization(json):
    """
    Parse a JSON response from the server into an Organization object.
    """
    name = json.get("name")
    account_manager = json.get("account_manager")
    if account_manager:
        account_manager = parse_account_manager(account_manager)
    return Organization(name, account_manager)


def parse_account_manager(json):
    """
    Parse a JSON response from the server into an AccountManager object.
    """
    name = json.get("name")
    email = json.get("email")
    return AccountManager(name, email)


def parse_subscriptions(json):
    """
    Parse a JSON response from the server into a list of Subscription objects.
    """
    return [parse_subscription(subscription) for subscription in json]
