def list2kwarg(args):
    par_dict = {}
    for value in args:
        parameter = value.split('=')
        if len(parameter) < 2:
            return 0

        par_dict[parameter[0]] = parameter[1]

    return par_dict
