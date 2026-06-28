import os

from setuptools import Extension, setup

USE_CYTHON = "USE_CYTHON" in os.environ
FILE_SUFFIX = ".pyx" if USE_CYTHON else ".c"

extensions = [
    Extension(
        "shirotsume_tools.archive._decrypt",
        [
            "shirotsume_tools/archive/_decrypt" + FILE_SUFFIX,
            "shirotsume_tools/archive/decrypt.cpp",
        ],
        include_dirs=["shirotsume_tools/archive"],
    ),
]

if USE_CYTHON:
    from Cython.Build import cythonize

    extensions = cythonize(
        extensions,
        annotate=True,
        compiler_directives={"language_level": "3"},
    )


setup(
    ext_modules=extensions,
)
