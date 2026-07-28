import os
import subprocess

eval("print('bad')")
subprocess.run("cat .env", shell=True)
print(os.environ.get("API_KEY"))
