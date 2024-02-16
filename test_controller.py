from controller import common_nandregs
from controller import bcm_nandregs
from controller import pxa3_nandregs
from controller import qcom_nandregs

if __name__ == "__main__":
    qcom_nandregs._moduletest()
    pxa3_nandregs._moduletest()
    bcm_nandregs._moduletest()
    common_nandregs._moduletest()