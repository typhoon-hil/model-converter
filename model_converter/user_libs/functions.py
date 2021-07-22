import numpy as np


def definition(x):
    return x

def print_input(input):
    print(input)
    return input

def si_prefix_remover(x):

    dictionary = {
                "T": "e12",
                "G": "e9",
                "M": "e6",
                "k": "e3",
                "K": "e3",
                "m": "e-3",
                "u": "e-6",
                "n": "e-9",
                "p": "e-12"
    }

    if x[-1] in dictionary:
        return x[:-1] + dictionary[x[-1]]
    else:
        return x


def int2string(int_value):
    return str(int(int_value))

def str2int(str_value):
    return int(str_value)

def period_frequency(freq_or_per):
    return float(1/freq_or_per)

def L12_to_k(L11, L22, L12):
    return float(L12) / np.sqrt(float(L11) * float(L22))


def return_negative(x):
    return -float(x)

def float2int(float_value):
    return int(float_value)

def primary_to_secondary(Np, Ns, Rs):
    return (float(Ns) ** 2) / (float(Np) ** 2) * float(Rs)


def Y_to_D(V):
    return float(V) / (3 ** 0.5)


def friction(J, tau):
    return float(J) / float(tau)


def flux():
    V = 98.67
    p = 4
    return V*60/(np.sqrt(3)*3.14169*p*1000)


def m_to_km(x):
    return float(x) / 1000


def return_cable_sequence(Rd, R0):
    return [[float(R0), 0, 0], [0, float(Rd), 0], [0, 0, float(Rd)]]


def return_cable_sequence_L(Xd, X0, f):
    Xd = float(Xd) / (2 * float(f) * np.pi)
    X0 = float(X0) / (2 * float(f) * np.pi)
    return [[X0, 0, 0], [0, Xd, 0], [0, 0, Xd]]

def divide(num, den):
    return num / den

def multiply(n1, n2):
    return n1 * n2

def divide_by_10(x):
    return x / 10

def divide_by_2(x):
    return x / 2


def return_constant1():
    return 0.5719631


def psi_pm(Vpk_krpm, poles):
    return float(Vpk_krpm)*60/(np.sqrt(3)*np.pi*float(poles)*1000)


def pole_pairs(poles):
    return float(poles)/2


def amplitude_to_rms(amplitude):
    return float(amplitude)/np.sqrt(2)


def line_to_phase_rms(line_rms):
    return float(line_rms)/np.sqrt(3)

def deg_to_rad(deg):
    return np.deg2rad(deg)

def rad_to_deg(rad):
    if type(rad) == str:
        rad = rad.replace("pi", "np.pi")
        return rad+"*180/np.pi"
    else:
        return np.rad2deg(rad)

def rad_per_sec_to_hz(rad):
    if type(rad) == str:
        rad = rad.replace("pi", "np.pi")
        return rad+"/(2*np.pi)"
    else:
        return rad/(2*np.pi)

def lowercase(input_str):
    return input_str.lower()

def on_off_to_bool_str(logic_str, capitalize=False):
    if logic_str not in ("on", "off"):
        raise ValueError(f"{logic_str} is not a valid value!")
    if capitalize:
        return "True" if logic_str == "on" else "False"
    return "true" if logic_str == "on" else "false"

def on_off_to_boolean(logic_str):
    if logic_str == 'on':
        return True
    if logic_str == 'off':
        return False

def simulink_switch_logic(logic_str):
    return str(logic_str).replace('-',' ').lower()

def simulink_contactor_init_state_st(initial_state):
    if initial_state == 'On / S1':
        return 'on'
    elif initial_state == 'Off / S2':
        return 'off'
    else:
        raise Exception('Invalid initial state value found in Simulink XML.')

def simulink_contactor_init_state_dt(initial_state):
    if initial_state == 'On / S1':
        return 'S1'
    elif initial_state == 'Off / S2':
        return 'S2'
    else:
        raise Exception('Invalid initial state value found in Simulink XML.')

def simulink_core_coupling_format(input, side):
    if input == "None":
        return 'none'
    elif input == "R":
        if side == '"is"':
            return 'R1'
        elif side == '"vs"':
            return 'R2'
    elif input == "R-C":
        return 'R1-C1'
    elif input == "R//L":
        return 'R2||L1'

def simulink_wye_delta_names(connection):
    if connection == "Wye":
        return "Y"
    elif connection == "Delta":
        return "D"
    else:
        raise Exception('Invalid connection type found in Simulink XML.')

def simulink_pmsm_theta_ab(angle):
    if angle == '-pi/2':
        return angle
    elif str(int(angle)) == '0':
        return str(int(angle))

def simulink_matrix_to_tse_format(mat):
    space_to_comma = ", ".join(mat.split())
    if ";" in space_to_comma:
        space_to_comma = "["+space_to_comma+"]"
        space_to_comma = space_to_comma.replace(";", "], [")
    return space_to_comma

def simulink_operator_conv(operator):

    if operator in ["isinf", "isNaN", "isFinite"]:
        return "=="
    if operator in ["sinh", "cosh", "tanh", "acosh", "asinh", "atanh", "sincos", "sin+jsin"]:
        return "sin"
    if operator == "~=":
        return "!="
    else:
        return operator


def snb_type_i_int_to_str(snb_type_int):
    if snb_type_int == 1:
        return 'R1'
    elif snb_type_int == 2:
        return 'R1-C1'
    else:
        return 'none'

def snb_type_u_int_to_str(snb_type_int):
    if snb_type_int == 1:
        return 'R2'
    elif snb_type_int == 2:
        return 'R2||L1'
    else:
        return 'none'

def fixed_snb_int_to_str(fixed_snb_int):
    if fixed_snb_int == 0:
        return 'false'
    else:
        return 'true'

def simulink_inputs(inputs):

    if type(inputs) == str:
        return inputs.replace("|", "")
    elif type(inputs) == float:
        return int(inputs)
    else:
        return inputs

def simulink_sample_to_f(sampletime, period):
    return 1/(period*sampletime)

def simulink_convert_data_types(input_data_type):
    if input_data_type in ['int8', 'int16', 'int32', 'int64']:
        return "int"
    elif input_data_type in ['uint8', 'uint16', 'uint32', 'uint64']:
        return "uint"
    elif input_data_type in ['double', 'single', 'half']:
        return "real"
    else:
        return ""

def simulink_switch_criteria(criterion):
    if "~=" in criterion:
        criterion = criterion.replace("~=", "!=")
        criterion = criterion.replace("0", "threshold")
    criterion = criterion.replace("u2 ", "ctrl ")
    return criterion.lower()

def simulink_sample_to_execution_rate(sample_rate):
    if sample_rate == "-1":
        sample_rate = "inherited"
    return sample_rate