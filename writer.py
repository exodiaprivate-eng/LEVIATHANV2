import base64, sys, pathlib
pathlib.Path(sys.argv[1]).write_text(base64.b64decode(sys.argv[2]).decode("utf-8"))
