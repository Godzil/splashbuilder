import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='splashbuilder',
    use_scm_version={
        'write_to': 'ws_splashbuilder/_version.py',
    },
    setup_requires=['setuptools_scm'],
#    version_format='{tag}',
#    setup_requires=['setuptools-git-version'],
    author="Manoel <godzil> Trapier",
    author_email="wssplashbuilder@godzil.net",
    description="A tool to build WonderSwan Color boot splash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['bin/splashbuilder', 'bin/cel2wst', 'bin/map2wsm'],
    url="https://github.com/godzil/splashbuilder",
    packages=["ws_splashbuilder"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires='>=3.6',
)
