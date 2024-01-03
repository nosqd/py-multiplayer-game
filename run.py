import sys
import game.game as g

try:
    g.run()
except KeyboardInterrupt:
    sys.exit(0)
