def printSchedule(schedule):
    """ Print the schedule in a more readable way (transform proc name)

    :param schedule: Schedule to print
    :type schedule: dict[int, (int, float, float)]
    :rtype: None
    """
    schedulebis = {}
    for s in schedule:
        schedulebis[s] = [schedule[s][0] + 1, schedule[s][1], schedule[s][2]]
    print(schedulebis)
