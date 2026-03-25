
import os

fs = {}

for root, dirs, files in os.walk('.'):
    for file in files:
        path = os.path.join(root, file)
        if os.path.abspath(path) == os.path.abspath(__file__):
            continue

        with open(path, 'rt') as f:
            data = f.read()
            fs[file] = data

print(repr(fs))
