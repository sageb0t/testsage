import sys

def reset():
    """
    Delete all user defined variables, reset all globals variables
    back to their default state, and reset all interfaces to other
    computer algebra systems.
    """
    G = globals()  # this is the reason the code must be in SageX.
    T = type(sys)
    for k in G.keys():
        if k[0] != '_' and type(k) != T:
            del G[k]
    restore()
    reset_interfaces()

def restore(vars=None):
    """
    Restore predefined global variables to their default values.

    INPUT:
       vars -- string or list (default: None) if not None, restores
               just the given variables to the default value.

    EXAMPLES:
        sage: x = 10; y = 15/3; QQ='red'
        sage: QQ
        'red'
        sage: restore('QQ')
        sage: QQ
        Rational Field
        sage: x
        10
        sage: restore('x  y')
        sage: x
        x
        sage: y
        y
        sage: x = 10; y = 15/3; QQ='red'
        sage: ww = 15
        sage: restore()
        sage: x,y,QQ,ww
        (x, y, Rational Field, 15)
        sage: restore('ww')
        sage: ww
        Traceback (most recent call last):
        ...
        NameError: name 'ww' is not defined
    """
    G = globals()  # this is the reason the code must be in SageX.
    import sage.all
    D = sage.all.__dict__
    if vars is None:
        for k, v in D.iteritems():
            G[k] = v
    else:
        if isinstance(vars, str):
            if ',' in vars:
                vars = vars.split(',')
            else:
                vars = vars.split()
        for k in vars:
            if D.has_key(k):
                G[k] = D[k]
            else:
                del G[k]      # the default value was "unset"

def reset_interfaces():
    from sage.interfaces.quit import expect_quitall
    expect_quitall()

##     import sys
##     M = sys.modules
##     for k in M.keys():
##         if 'sage.interfaces' in k:
##             if not M[k] is None:
##                 reload(M[k])

##     import sage.interfaces.all
##     G = globals()
##     for k, v in sage.interfaces.all.__dict__.iteritems():
##         G[k] = v
