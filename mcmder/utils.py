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
    elif x is None:
        return None
    else:
        return str(x)


def clean_dic(local_dic):
    del local_dic['self']
    del local_dic['options']
    if '_from' in local_dic:
        local_dic['from'] = local_dic['_from']
        del local_dic['_from']
    cleaned_dic = {}
    for key, value in local_dic.items():
        cleaned_dic[key] = to_cstr(value)
    return cleaned_dic
