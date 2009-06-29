import vm

# Sensor ports
s_score, s_fuel, s_sx, s_sy, s_tx, s_ty = range(6)

# Actuator ports
a_dvx, a_dvy, a_config = 2, 3, 0x3E80

vm.load('bin1.obf')
vm.scenario = 1001.0
vm.step()
