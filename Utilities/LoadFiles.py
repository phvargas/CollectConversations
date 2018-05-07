def file_list(inputfile):
    """
    :param inputfile: filename that holds the values
    :return: an array of values loaded from input file
    """
    obj = []
    with open(inputfile, mode='r') as fhs:
        for term in fhs:
            if term.strip():
                obj.append(term.lower().strip())

    return obj
