from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pebble-lang",
    version="2.2.0",
    author="Rasa8877",
    author_email="letperhut@gmail.com",
    description="Pebble programming language interpreter in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rasa8877/pebble-lang",
    packages=find_packages(include=["pebble", "pebble.*"]),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pebble=pebble.interpreter:main",
        ],
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
    ],
)
