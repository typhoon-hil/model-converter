import numpy as np


def definition(x):
    return x


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


def L12_to_k(L11, L22, L12):
    return float(L12) / np.sqrt(float(L11) * float(L22))


def return_negative(x):
    return -float(x)


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