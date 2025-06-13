from ._Pass import Pass


def switch(layer, is_used):
    if is_used:
        return layer
    else:
        return Pass()
