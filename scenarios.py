def make_problem(scenario, watching=False):
    if 1001 <= scenario <= 1004:
        from hohmann import HohmannProblem as class_
    elif 2001 <= scenario <= 2004:
        from meetandgreet import MeetAndGreetProblem as class_
    else:
        assert False
    return class_(scenario, watching=watching)
