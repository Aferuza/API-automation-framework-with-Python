def mask_token(token: str, visible_chars: int = 4) -> str:

    if len(token) <= visible_chars * 2:
        return "*" * len(token)

    masked_middle_part = "*" * (len(token) - visible_chars * 2)
    return token[:visible_chars] + masked_middle_part + token[-visible_chars:]


def build_auth_token(token: str) -> str:

    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:]
    return f"Bearer {token}"