from distutils.core import setup
import py2exe


setup(
      name = 'start_gui',
      windows = [
                 {
                    'script':'start_gui.py',
                  }
                 ],
                 
      options = {
                    'py2exe' : {
                                'packages':'encodings',
                                'includes':'cairo, pango, pangocairo, atk, gobject, gio',
                                
                    
                    }
                 }
      
)