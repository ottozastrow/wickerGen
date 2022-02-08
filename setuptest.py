import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wickerGen-ottozastrow",
    version="0.1",
    author="Otto von Zastrow-Marcks",
    author_email="otto.zastrow@hotmail.de",
    description="a package for generating wicker patterns for robotic manufactoring of willow construction components",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ottozastrow/wickerGen",
    project_urls={
        "Bug Tracker": "https://github.com/ottozastrow/wickerGen/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved ::  GPL-3.0 License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)
