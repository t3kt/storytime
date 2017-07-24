import sys
import os
import runpy

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)
runpy.run_module('tools.convert_ae_keyframes', run_name='__main__', alter_sys=True)
