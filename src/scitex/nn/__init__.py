#!/usr/bin/env python3
"""Scitex nn module."""

from ._AxiswiseDropout import AxiswiseDropout
from ._BNet import BHead as BHead_v1, BNet as BNet_v1, BNet_config as BNet_config_v1
from ._BNet_Res import BHead as BHead_Res, BNet as BNet_Res, BNet_config as BNet_config_Res
from ._ChannelGainChanger import ChannelGainChanger
from ._DropoutChannels import DropoutChannels
from ._Filters import BandPassFilter, BandStopFilter, BaseFilter1D, DifferentiableBandPassFilter, GaussianFilter, HighPassFilter, LowPassFilter
from ._FreqGainChanger import FreqGainChanger
# Removed duplicate GaussianFilter import - already imported from _Filters
from ._Hilbert import Hilbert
from ._MNet_1000 import MNet1000, MNet_1000, MNet_config, ReshapeLayer, SwapLayer
from ._ModulationIndex import ModulationIndex
from ._PAC import PAC
from ._PSD import PSD
from ._ResNet1D import ResNet1D, ResNetBasicBlock
from ._SpatialAttention import SpatialAttention
from ._Spectrogram import Spectrogram, my_softmax, normalize, spectrograms, unbias
from ._SwapChannels import SwapChannels
from ._TransposeLayer import TransposeLayer
from ._Wavelet import Wavelet

__all__ = [
    "AxiswiseDropout",
    "BHead_v1",
    "BHead_Res", 
    "BNet_v1",
    "BNet_Res",
    "BNet_config_v1",
    "BNet_config_Res",
    "BandPassFilter",
    "BandStopFilter",
    "BaseFilter1D",
    "ChannelGainChanger",
    "DifferentiableBandPassFilter",
    "DropoutChannels",
    "FreqGainChanger",
    "GaussianFilter",
    "HighPassFilter",
    "Hilbert",
    "LowPassFilter",
    "MNet1000",
    "MNet_1000",
    "MNet_config",
    "ModulationIndex",
    "PAC",
    "PSD",
    "ResNet1D",
    "ResNetBasicBlock",
    "ReshapeLayer",
    "SpatialAttention",
    "Spectrogram",
    "SwapChannels",
    "SwapLayer",
    "TransposeLayer",
    "Wavelet",
    "my_softmax",
    "normalize",
    "spectrograms",
    "unbias",
]
