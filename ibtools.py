from .ibreal import IBReal as R
from os import environ

#number of expected roots given degree of real root
def num_roots(root):
    def isint(num):
        return int(num) == num 
    if not isinstance(root, R): 
        root = R(root)
    (num, sl) = root.ival
    denom = 10 ** sl
    index = sorted([num, denom])[0] + 1
    tn = num 
    for a in range(1, int(index)):
        if isint(num/a):
            if isint(denom/a):
                tn = num/a
    return tn

def set_global_prec(num):
    environ['IBR_DEF_PREC'] = str(num)

