from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pebble-lang",
    version="1.1.5",
    description="Pebble programming language interpreter in Python",
    long_description=long_description,         # <-- add this
    long_description_content_type="text/markdown",  # <-- important
    author="Rasa8877",
    author_email="letperhut@gmail.com",
    url="https://github.com/Rasa8877/pebble-lang",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pebble=pebble.interpreter:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
