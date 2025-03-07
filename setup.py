import setuptools

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setuptools.setup(
    name="tgslicer",
    version="1.0",
    author="Lucas Eckert",
    author_email="eckert@student.tugraz.at",
    description="Tool for Efficient Stimuli Extraction from Large Speech Corpora",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SPSC-TUGraz/SLICER",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.8",
    install_requires=[
        "matplotlib",
        "numpy",
        "scipy",
        "sounddevice",
        "soundfile",
        "textgrid",
        "tkinter-tooltip"
    ]
)
