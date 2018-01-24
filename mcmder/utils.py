
def df2bytes(dataframe):
    """Convert pandas.DataFrame to bytes csv.

    :param pandas.DataFrame dataframe: dataframe to convert
    :return: bytes of csv
    :rtype: bytes
    """
    return '\n'.join(
        [','.join(dataframe), ] +
        [','.join(map(str, row)) for row in dataframe.values]
    ).encode()


def to_cstr(x):
    if isinstance(x, str):
        return x
    elif isinstance(x, list):
        return ','.join(x)
    elif isinstance(x, dict):
        return ','.join(k + ':' + v for k, v in x.items())
    else:
        return str(x)