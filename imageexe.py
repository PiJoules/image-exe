#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from PIL import Image
import numpy as np

import py_compile


BYTE_LEN = 8  # Num of bits in a byte


def inject_bits(val, bits, num_bits=2):
    return ((val << num_bits) | bits) & 0xff


def reverse_bits(x, n=8, chunk=2):
    result = 0
    for i in xrange(0, n, chunk):
        part = (x >> i) & (2**chunk - 1)
        result |= part << (n - i - chunk)
    return result


def char_generator(filename):
    with open(filename, "rb") as f:
        for line in f:
            for c in line:
                yield c


class ImgManager(object):
    def __init__(self, img, chunk_size=2):
        self.__img = img
        self.__x = self.__y = 0
        self.__h = img.size[1]
        self.__w = img.size[0]
        self.__pixdata = img.load()
        self.__chunk_size = chunk_size

    def next_coords(self):
        if self.__y >= self.__h:
            return None

        if self.__x >= self.__w:
            self.__x = 0
            self.__y += 1

        coord = (self.__x, self.__y)
        self.__x += 1
        return coord

    def apply_byte(self, byte):
        # Aplied in reverse order for simple decoding
        pixdata = self.__pixdata
        n = self.__chunk_size

        rev_data = reverse_bits(byte)
        for i in xrange(0, BYTE_LEN, n):
            coords = self.next_coords()
            if not coords:
                raise RuntimeError("Ran out of space")

            x, y = coords
            r, g, b = pixdata[x, y]

            part = rev_data & (2**n - 1)
            r = inject_bits(r, part)
            rev_data = rev_data >> n

            pixdata[x, y] = (r, g, b)

    def apply_null(self):
        self.apply_byte(ord("\0"))

    def encode(self, stream):
        for c in stream:
            self.apply_byte(ord(c))
        self.apply_null()

    def decode(self):
        img = self.__img
        pixdata = self.__pixdata
        n = self.__chunk_size

        s = ""
        c = 0
        i = 0
        for y in xrange(img.size[1]):
            for x in xrange(img.size[0]):
                r, g, b = pixdata[x, y]

                # Read from red
                bits = r & (2**n - 1)
                c = (c << n) | bits
                i += n
                if i >= 8:
                    if not c:
                        return s
                    s += chr(c)
                    c = 0
                    i = 0

        return s

    def run(self):
        from tempfile import NamedTemporaryFile
        import subprocess
        with NamedTemporaryFile() as f:
            s = self.decode()
            f.write(s)
            f.flush()
            #execfile(f.name)
            # For some reason, execfile does not recognize user defined
            # functions in the file.
            subprocess.call("python {}".format(f.name).split())
            #exec s


def get_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("-f", "--filename")
    parser.add_argument("-i", "--img")

    return parser.parse_args()


def main():
    assert reverse_bits(0x66) == 0x99

    args = get_args()
    img = Image.open(args.img)
    img.convert("RGBA")

    img_man = ImgManager(img)
    if args.filename:
        img_man.encode(char_generator(args.filename))
    img_man.run()

    img.close()

    return 0


if __name__ == "__main__":
    main()


