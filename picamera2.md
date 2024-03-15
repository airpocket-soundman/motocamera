
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