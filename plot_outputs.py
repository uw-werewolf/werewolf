import pandas as pd
import numpy as np
import gdxtools as gt


def plt_stuff():
    gdxin = gt.gdxrw.gdxReader('./output.gdx')

    f = gdxin.rgdx(name='ave_f')
    lat = gdxin.rgdx(name='lat')
    lng = gdxin.rgdx(name='lng')
    ij = gdxin.rgdx(name='ij')
    nn = gdxin.rgdx(name='i')
    b = gdxin.rgdx(name='b')


if __name__ == '__main__':
