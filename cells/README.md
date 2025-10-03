# README: Cells 

Bones are build from cells, those smaller building blockes have a more limited focus that a complete bone. 
This is a container best understood as a mono-repository inside the outer library.

When matured the cells will be split into their own repository, but for now they are part of the surrounding bone package.

Cells might be implement in another programming language than Python, but if they are they will all provide a API for Python.

This means that regardless of the underlying implementation, the cells will expose a consistent interface that can be used from Python code or via executable with a tight integration to Python (like `uv` from Astra). This allows for greater flexibility and the ability to leverage existing Python tooling and libraries. ()