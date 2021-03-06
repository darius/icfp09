def make_problem(scenario, watching=False):
    if 1001 <= scenario <= 1004:
        from hohmann import HohmannProblem as class_
    elif 2001 <= scenario <= 2004:
        from meetandgreet import MeetAndGreetProblem as class_
    elif 3001 <= scenario <= 3004:
        from eccentricmeetandgreet import EccentricMeetAndGreetProblem as class_
    elif 4001 <= scenario <= 4004:
        from clearskies import ClearSkiesProblem as class_
    else:
        assert False
    return class_(scenario, watching=watching)
