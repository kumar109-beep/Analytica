activate_this = 'C:/ProgramData/Miniconda3/Scripts/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))
# exec(open(activate_this).read(),dict(__file__=activate_this))
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})
# activate_this = 'C:/Users/TATTVA/Miniconda3/Scripts/activate.sh'
# exec(open(activate_this).read(),dict(__file__=activate_this))
# exec(activate_this)


import os
import sys
import site
from django.core.wsgi import get_wsgi_application

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('C:/ProgramData/Miniconda3/Lib/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('C:/pyproject/analytica')
sys.path.append('C:/pyproject/analytica/analytica')

os.environ['DJANGO_SETTINGS_MODULE'] = 'analytica.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "analytica.settings")

application = get_wsgi_application()

