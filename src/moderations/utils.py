def timedelta_to_str(td):
    result = ""
    td = str(td).split(",")  # Timedeltas >24hrs have commas
    if len(td) > 1:  # Timedelta > 1 day
        result += td[0] + " "
        td.pop(0)
    time = td[0].split(":")

    result += "%s hrs " % time[0]
    result += "%s min " % time[1]
    result += "%s sec" % time[2].split(".")[0]

    return result
