import subprocess

def install(package):
    subprocess.check_call(["pip3", "install", package])

packages = ["instaloader", "tqdm", "colorama", "pillow"]

for package in packages:
    install(package)
