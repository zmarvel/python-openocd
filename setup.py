#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name="python-openocd",
        author="Zack Marvel",
        author_email="zpmarvel@gmail.com",
        description="Communication with OpenOCD server",
        url="https://github.com/zmarvel/python-openocd.git",
        packages=setuptools.find_packages(where="src"),
        package_dir={"": "src"}
    )

