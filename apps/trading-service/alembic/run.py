import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alembic.config import main

if __name__ == "__main__":
    ini_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../alembic.ini"))
    args = sys.argv[1:] if len(sys.argv) > 1 else ["upgrade", "head"]
    main(argv=["-c", ini_path] + args)
