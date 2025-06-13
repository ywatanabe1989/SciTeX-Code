def is_ipython():
    try:
        __IPYTHON__
        ipython_mode = True
    except NameError:
        ipython_mode = False

    return ipython_mode


def is_script():
    return not is_ipython()
