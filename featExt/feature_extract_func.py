import numpy as np
import time, os
import scipy.stats as sts
from pywt import WaveletPacket


def rms_fea(a):
    return np.sqrt(np.mean(np.square(a)))


def var_fea(a):
    return np.var(a)


def max_fea(a):
    return np.max(a)


def pp_fea(a):
    return np.max(a) - np.min(a)


def skew_fea(a):
    return sts.skew(a)


def kurt_fea(a):
    return sts.kurtosis(a)


def wave_fea(a):
    wp = WaveletPacket(a, 'db1', maxlevel=8)
    nodes = wp.get_level(8, "freq")
    return np.linalg.norm(np.array([n.data for n in nodes]), 2)


def spectral_kurt(a):
    N = a.shape[0]
    mag = np.abs(np.fft.fft(a))
    mag = mag[1:N // 2+1] * 2.00 / N
    return sts.kurtosis(mag)


def spectral_skw(a):
    N = a.shape[0]
    mag = np.abs(np.fft.fft(a))
    mag = mag[1:N // 2+1] * 2.00 / N
    return sts.skew(mag)


def spectral_pow(a):
    N = a.shape[0]
    mag = np.abs(np.fft.fft(a))
    mag = mag[1:N // 2+1] * 2.00 / N
    return np.mean(np.power(mag, 2))


def extract_feature(data):
    # input: time_len, dim_fea  -> dim_fea*10
    data_fea = []
    dim_feature = data.shape[-1]
    for i in range(dim_feature): 
        data_slice = data[:, i]
        data_fea.append(rms_fea(data_slice))
        data_fea.append(var_fea(data_slice))
        data_fea.append(max_fea(data_slice))
        data_fea.append(pp_fea(data_slice))
        data_fea.append(skew_fea(data_slice))
        data_fea.append(kurt_fea(data_slice))
        data_fea.append(wave_fea(data_slice))
        data_fea.append(spectral_kurt(data_slice))
        data_fea.append(spectral_skw(data_slice))
        data_fea.append(spectral_pow(data_slice))
    data_fea = np.array(data_fea)  
    
    return data_fea



    