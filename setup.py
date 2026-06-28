from setuptools import Extension, setup

try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

FILE_SUFFIX = ".pyx" if USE_CYTHON else ".c"

extensions = [
    Extension(
        "shirotsume_tools.archive.crypt",
        [
            "shirotsume_tools/archive/crypt" + FILE_SUFFIX,
            "shirotsume_tools/archive/repipack.cpp",
        ],
        include_dirs=["shirotsume_tools/archive"],
    ),
]

if USE_CYTHON:
    extensions = cythonize(
        extensions,
        annotate=True,
        compiler_directives={"language_level": "3"},
    )

setup(ext_modules=extensions)
