import pkg_resources
import sys

try:
    version = pkg_resources.get_distribution("PyGithub").version
    print(f"PyGithub version: {version}")
except pkg_resources.DistributionNotFound:
    print("PyGithub is not installed")

print(f"Python version: {sys.version}")
