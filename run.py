import sys
import game.game as g
from config import HOST, PORT
try:
    g.run(HOST, PORT)
except KeyboardInterrupt:
    sys.exit(0)
