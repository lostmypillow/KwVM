import os, sys
from vdiclient import main

sys.exit(main(os.path.abspath("vdiclient.ini").replace('\\', '/')))