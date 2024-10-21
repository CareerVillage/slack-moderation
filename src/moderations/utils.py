def timedelta_to_str(td):
    result = ""
    td = str(td).split(",")  # Timedeltas >24hrs have commas
    if len(td) > 1:  # Timedelta > 1 day
        result += td[0] + " "
        td.pop(0)

    time = td[0].split(":")
    hours = time[0]
    minutes = time[1]
    seconds = time[2].split(".")[0]

    result += f"{hours} hrs "
    result += f"{minutes} min "
    result += f"{seconds} sec"

    return result
