"""
Some constants necessary for proper communication between the modules.
"""


LOW = 0
HIGH = 1
MODE_OUT = 2
MODE_IN = 3
PUD_OFF = 4
PUD_DOWN = 5
PUD_UP = 6
BCM = 7
BOARD = 'BOARD'
MODE_PWM = 8

FALLING = 'FALLING'
RISING = 'RISING'
BOTH = 'BOTH'

GPIONames = [14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21, 2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26]

# map physical numbers to BCM numbers
PHYS_TO_BCM_MAP = {
    3: 2,
    5: 3,
    7: 4, 8: 14,
    10: 15,
    11: 17, 12: 18,
    13: 27,
    15: 22, 16: 23,
    18: 24,
    19: 10,
    21: 9, 22: 25,
    23: 11, 24: 8,
    26: 7,
    29: 5,
    31: 6, 32: 12,
    33: 13,
    35: 19, 36: 16,
    37: 26, 28: 20,
    40: 21
}
