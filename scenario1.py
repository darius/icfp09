import vm

def main():
    s1vm = S1VM(1001)
    s1vm.load('bin1.obf')
    s1vm.step()

# Sensor ports
s_score, s_fuel, s_sx, s_sy, s_tx, s_ty = range(6)

# Actuator ports
a_dvx, a_dvy, a_config = 2, 3, 0x3E80


class S1VM(vm.VM):

    def __init__(self, scenario):
        vm.VM.__init__(self)
        self.scenario = float(scenario)
        self.dv = (0.0, 0.0)

    def input(self, actuator):
        if actuator == a_config: return self.scenario
        if actuator == a_dvx:    return self.dv[0]
        if actuator == a_dvy:    return self.dv[1]
        assert False


if __name__ == '__main__':
    main()
