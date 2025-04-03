from setuptools import setup, find_packages

setup(
    name="github-review-agent",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "transformers",
        "torch",
        "networkx",
        "numpy",
        "scikit-learn",
        "requests",
    ],
    python_requires=">=3.8",
)
