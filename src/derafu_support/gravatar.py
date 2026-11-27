"""Gravatar avatar from an email address."""

import hashlib


def email_md5(email: str) -> str:
    """
    Return the MD5 hash of an email address, as used by Gravatar.

    MD5 is not used for security: it is the identifier Gravatar requires.

    :param email: Email address.
    :return: MD5 hash in hexadecimal.
    :rtype: str
    """
    return hashlib.md5(
        email.encode('utf-8'), usedforsecurity=False
    ).hexdigest()


def gravatar_url(email: str) -> str:
    """
    Return the URL of the Gravatar image of an email address.

    :param email: Email address.
    :return: Image URL.
    :rtype: str
    """
    return 'https://gravatar.com/avatar/' + email_md5(email)
