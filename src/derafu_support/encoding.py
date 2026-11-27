"""Data encoding functions."""

import base64
import re


def base64_decode(data: bytes, altchars: bytes = b'+/') -> bytes:
    """
    Decode base64 data, with optional padding (``=``).

    Before decoding, characters that are not base64 (for example, line
    breaks) are removed and any missing padding is added.
    Based on https://stackoverflow.com/a/9807138.

    :param data: Base64 data (ASCII text as bytes).
    :param altchars: The two characters used instead of ``+`` and ``/``.
    :return: Decoded data.
    :rtype: bytes
    """
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'=' * (4 - missing_padding)
    return base64.b64decode(data, altchars)
