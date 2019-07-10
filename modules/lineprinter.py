#!/usr/bin/env python3

'''Simple class for update last line out in console

printer = LinePrinter(format_line, format_kwargs)
printer._print()
printer._print(new_format_line, new_format_kwargs)

'''

from sys import stdout

class LinePrinter():
    __slots__ = ['format_string', 'data', 'length']

    def __init__(self, *args, **kwargs):
        if not args:
            args = [""]

        self.format_string = args[0]
        self.data = kwargs

        string = self.format_string.format(**self.data)
        # Cut last spaces
        list_cutted = string.rsplit(maxsplit=0)
        self.length = len(list_cutted[0]) if list_cutted else 0

    def print(self, *args, **kwargs):
        if args:
            self.format_string = args[0]
        self.data.update(kwargs)

        string = self.format_string.format(**self.data)

        # You can send lineprinter format string in key
        # Don't use with notformat strings contain { or }. Otherwise comment this
        string = string.format(**self.data)
        
        string = string + ' '*(self.length - len(string))
        list_cutted = string.rsplit(maxsplit=0)
        self.length = len(list_cutted[0]) if list_cutted else 0

        stdout.write('\r' + string)
        stdout.flush()

    def __del__(self, *args, **kwargs):
        stdout.write('\n')

if __name__ == '__main__':
    printer = LinePrinter()
    i = 0
    try:
        while True:
            i += 1
            printer.print('[{lol:{alig}{ln}}]', 
                          lol=i%1000000, 
                          alig='<^>'[i%60000//20000],
                          ln=[35, 30, 25][i%60000//20000])
    except KeyboardInterrupt: # Ctrl+C
        pass
