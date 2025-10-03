# Motivatoin

## Python is awesome

!!! warning "Python's Philosopy"

    "Python comes with batteries included!" - The Zen of Python, by Tim Peters [>>](https://llego.dev/posts/zen-python-guide-design-philosophy-readability/)

Python is a powerful and versatile programming language that emphasizes code readability and simplicity. It has a large standard library that provides many useful modules and functions for various tasks, such as file I/O, regular expressions, data serialization, networking, and more. 

Python also has a rich ecosystem of third-party packages that extend its functionality and enable developers to build complex applications with ease. Forerunners of this are `requests` for HTTP requests, `pandas` for data analysis, `numpy` for numerical computing, `flask` for web development, `rich` for rich text and beautiful formatting or `click` for command-line interfaces.

But Python has quite a bit of history and if you look closely, you will notice that for example handling file system object is quite scattered in different parts of the standard library. `os` and `pathlib` are the main modules for file system operations, but they have different approaches and APIs. `os` is more low-level and provides functions that work with file descriptors and paths as strings, while `pathlib` is more high-level and provides an object-oriented interface for manipulating paths as objects. But you can not do anything in `pathlib`. And there is more because some functions need other packages like `copy` and `shutils`. **This can lead to confusion and inconsistency when working with file system objects in Python.**. 

Furthermore, as with all things created by humans, there is always room for improvement. Python is defining `snake_case` as its naming convention, which promotes readability and consistency across the language. However many standard library modules and functions do not follow this convention, which can lead to confusion and inconsistency when using them. For example, the `os` module has functions like `listdir`, `mkdir`, and `getcwd`, while the `pathlib` module has methods like `iterdir`, `mkdir`, and `cwd`. This inconsistency can make it harder for developers to learn and use the language effectively. Even uglier are functions like `isinstance`, `hasattr` or `getattr`. Keeping those functions for backwards compatibility is surely a good thing, but do you realize how easy it is to rectify those short commings?

``` python
is_instance = isinstance
# or if you aiming for "take a name that is already known:"
cd = os.changedir
```

!!! note 'Constructive and Loving Critique'

    This is not meant as a rant against Python. I love Python and use it daily. I just want to point out some areas where it could be improved. I also want to show how we can leverage Python's strengths and create packages that complement and enhance its capabilities.

**Hands Magic** comes to the rescue. You can think of it as **rechargeable batteries** for your Python projects. Its first goal is to provide anything you need for a smooth and consistent automation and testing experiance. Its part are - as the wounderfull idea of a human hand - build by multiple smaller packages that focus on specific aspects of this big goal.  


**Hands Scaphoid** aims to provide a unified and consistent interface for handling file system objects in Python. It combines the best features of `os` and `pathlib` and adds more functionality and flexibility. It also integrates with other packages like `cells_validator` for validation and `cells_logger` for logging.

