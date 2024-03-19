
既定のConfig

{   
    'use_case': 'preview',
    'transform': <libcamera.Transform 'identity'>, 
    'colour_space': <libcamera.ColorSpace 'sYCC'>, 
    'buffer_count': 4, 
    'queue': True, 
    'main': {
        'format': 'XBGR8888', 
        'size': (640, 480)
        }, 
    'lores': None, 
    'raw': {
        'format': 'SBGGR10_CSI2P', 
        'size': (640, 480)
    }, 
    'controls': {
        'NoiseReductionMode': <NoiseReductionModeEnum.Minimal: 3>, 'FrameDurationLimits': (100, 83333)
    }, 
    'display': 'main', 
    'encode': 'main'
}


{
    'use_case': 'still', 
    'transform': <libcamera.Transform 'identity'>, 
    'colour_space': <libcamera.ColorSpace 'sYCC'>, 
    'buffer_count': 1, 
    'queue': True, 
    'main': {
        'format': 'BGR888', 
        'size': (4608, 2592)
    }, 
    'lores': None, 
    'raw': {
        'format': 'SBGGR10_CSI2P', 
        'size': (4608, 2592)
    }, 
    'controls': {
        'NoiseReductionMode': <NoiseReductionModeEnum.HighQuality: 2>,
        'FrameDurationLimits': (100, 1000000000)
    }, 
    'display': None, 
    'encode': None
}

{
    'use_case': 'video', 
    'transform': <libcamera.Transform 'identity'>, 
    'colour_space': <libcamera.ColorSpace 'Rec709'>, 
    'buffer_count': 6, 
    'queue': True, 
    'main': {
        'format': 'XBGR8888', 
        'size': (1280, 720)
    }, 
    'lores': None, 
    'raw': {
        'format': 'SBGGR10_CSI2P', 
        'size': (1280, 720)
    }, 
    'controls': {
        'NoiseReductionMode': <NoiseReductionModeEnum.Fast: 1>,
        'FrameDurationLimits': (33333, 33333)
    }, 
    'display': 'main', 
    'encode': 'main'
}

## IMX708 camera metadata

{
    'SensorTimestamp'       : 1816022642000, 
    'ScalerCrop'            : (576, 0, 3456, 2592), 
    'ColourCorrectionMatrix': (1.153103232383728, 0.2702089250087738, -0.4233209788799286, -0.4905202090740204, 1.6031261682510376, -0.11261484771966934, -0.09961201250553131, -1.078633427619934, 2.1782443523406982), 
    'FocusFoM'              : 717, 
    'ExposureTime'          : 1977, 
    'SensorTemperature'     : -20.0, 
    'AfPauseState'          : 0, 
    'LensPosition'          : 1.0, 
    'FrameDuration'         : 17849, 
    'AeLocked'              : True, 
    'AfState'               : 0, 
    'DigitalGain'           : 1.0114408731460571, 
    'AnalogueGain'          : 16.0, 
    'ColourGains'           : (1.2329082489013672, 4.292367458343506), 
    'ColourTemperature'     : 2534, 
    'Lux'                   : 11.615120887756348, 
    'SensorBlackLevels'     : (4096, 4096, 4096, 4096)
}
