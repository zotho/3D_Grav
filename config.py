#!/usr/bin/env python3

import custom_update as upd

# Settings
CUSTOM_ACC = upd.custom_acc6

# Graphics
ROUND_SPACE = CUSTOM_ACC in (upd.custom_acc5, 
                             upd.custom_acc3_2,)
ACC_MARKERS = True
N_DIMENSION = 3

# Charge
REQIRE_CHARGE = (upd.custom_acc5,)
CHARGE = CUSTOM_ACC in REQIRE_CHARGE
