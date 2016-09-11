## Run Images in Python
Store code in images and run those images as if they were valid python files.

This feature is built into the default CPython interpreter.

Only works with pngs for now.

## Building + Usage
Building is the same as building python from source.
```sh
$ mkdir build
$ cd build
$ ../configure
$ make
$ ./python -p myimage.png samples/fib.py
55  # Runs normally, but also saves the code in the image
$ ./python myimage.png
55
```


## Limitations
As for as I've tested, code stored in images do not seem to be able to user frameworks from virtualenvs.


## Dependencies
- C
  - libpng
