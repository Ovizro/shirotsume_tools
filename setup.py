import os
from setuptools import setup, Extension


USE_CYTHON = "USE_CYTHON" in os.environ
FILE_SUFFIX = ".pyx" if USE_CYTHON else ".c"

extensions = [
    Extension(
        "shirotsume_tools.decrypt",
        ["shirotsume_tools/decrypt" + FILE_SUFFIX, "shirotsume_tools/_decrypt.cpp"],
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
