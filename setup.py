from setuptools import setup, find_packages

setup(
    name="pebble-lang",
    version="1.0.0",
    description="Pebble programming language interpreter in Python",
    author="Rasa8877",
    author_email="letperhut@gmail.com",
    url="https://github.com/Rasa8877/Pebble-lang",
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
