# This is here in Cython so we can get the interpreter globals

import sage_timeit

class SageTimeit:
    """
    Time execution of a command or block of commands.  Displays the
    best WALL TIME for execution of the given code.  This is based on
    the Python timeit module, which avoids a number of common traps
    for measuring execution times.   It is also based on IPython's
    %timeout command.

    TYPICAL INPUT FORMAT:
        timeit(statement, preparse=None, number=0, repeat=3, precision=3)

    EXAMPLES:
        sage: timeit('2^10000')
        625 loops, best of 3: ... per loop

    We illustrate some options:
        sage: timeit('2+2',precision=2,number=20,repeat=5)
        20 loops, best of 5: ... per loop

    The preparser is on by default (if it is on), but the preparse option
    allows us to override it.
        sage: timeit('2^10000', preparse=False, number=50)
        50 loops, best of 3: ... per loop

    The input can contain newlines:
        sage: timeit("a = 2\nb=131\nfactor(a^b-1)", number=25)
        25 loops, best of 3: ... per loop
    """
    def eval(self, code, globs=None, locals=None, **kwds):
        r"""
        This eval function is called when doing \%timit in the notebook.

        INPUT:
            code   -- string of code to evaluate; may contain newlines
            globs  -- global variables; if not given, uses module scope globals
            locals -- ignored completely
            kwds   -- passed onto sage_timeit.
                          preparse, number, repeat, precision

        OUTPUT:
            string -- timing information as a string

        EXAMPLES:
            sage: timeit.eval("2+2")                     # random output
            '625 loops, best of 3: 1.47 us per loop'

        We emphasize that timeit times WALL TIME.  This is good in the context of
        Sage where commands often call out to other subprocesses that don't appear
        in CPU time.
            sage: timeit('sleep(0.5)', number=3)
            3 loops, best of 3: ... ms per loop
        """
        if globs is None:
            globs = globals()
        return sage_timeit.sage_timeit(code, globs, **kwds)

    def __call__(self, code, globals=None, preparse=None, **kwds):
        """
        INPUT:
            code -- a string (a line or block of code, which may contain newlines)
            globals -- optional global variables; if not given the globals
                       of the calling module are used (e.g., if using this
                       from the command line, the globals of the command line
                       are used).
            preparse -- (default: same as shell default); whether or
                       not to preparse the input code using the Sage
                       preparser.  If not specified, do the same thing
                       as whatever was set by the preparser command.
            **kwds -- passed onto self.eval(...)

        OUTPUT:
            side effect of printing timing information

        EXAMPLES:
            sage: timeit('2^10000', preparse=False, number=100)
            100 loops, best of 3: ... per loop
        """
        print self.eval(code, globals, preparse=preparse, **kwds)

timeit = SageTimeit()
