import os


join_path = lambda *args: os.path.join(*args)
path_exists = lambda abs_path: os.path.exists(abs_path)
