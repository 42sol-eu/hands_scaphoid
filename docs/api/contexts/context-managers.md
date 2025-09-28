# Context Managers

A context manager in Python is a construct that allows for the setup and teardown of resources automatically. It is typically used with the `with` statement to ensure that resources are properly managed, even in the presence of errors.

## Using context anagers

To use a context manager, you define a class with `__enter__` and `__exit__` methods, or you can use the `contextlib` module to create one easily. Here's an example:

```python
from contextlib import contextmanager as context_manager

@context_manager
def managed_resource():
    # Setup code
    resource = acquire_resource()
    try:
        yield resource
    finally:
        # Teardown code
        release_resource(resource)
```

You can then use this context manager as follows:

```python
with managed_resource() as res:
    # Use the resource
```

## Benefits of context managers

1. **Automatic resource management**: Context managers handle resource allocation and deallocation automatically, reducing the risk of resource leaks.
2. **Cleaner code**: They help to keep your code clean and readable by encapsulating setup and teardown logic.
3. **Error handling**: Context managers can handle exceptions gracefully, ensuring that resources are released even if an error occurs.
