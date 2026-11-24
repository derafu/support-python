"""Avatar de Gravatar a partir de un correo electrónico."""

import hashlib


def email_md5(email: str) -> str:
    """
    Entrega el hash MD5 de un correo, como lo usa Gravatar.

    El MD5 no se usa como protección: es el identificador que pide Gravatar.

    :param email: Correo electrónico.
    :return: Hash MD5 en hexadecimal.
    :rtype: str
    """
    return hashlib.md5(
        email.encode('utf-8'), usedforsecurity=False
    ).hexdigest()


def gravatar_url(email: str) -> str:
    """
    Entrega la URL de la imagen de Gravatar de un correo.

    :param email: Correo electrónico.
    :return: URL de la imagen.
    :rtype: str
    """
    return 'https://gravatar.com/avatar/' + email_md5(email)
