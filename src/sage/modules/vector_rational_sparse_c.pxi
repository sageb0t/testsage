#############################################################
#
#    Sparse Vector over mpq_t (the GMP rationals)
#
#############################################################

include "../ext/cdefs.pxi"

cdef struct mpq_vector:
    mpq_t *entries      # array of nonzero entries
    int   *positions    # positions of those nonzero entries, starting at 0
    int    degree       # the degree of this sparse vector
    int    num_nonzero  # the number of nonzero entries of this vector.

cdef int allocate_mpq_vector(mpq_vector* v, int num_nonzero) except -1:
    """
    Allocate memory for a mpq_vector -- most user code won't call this.
    num_nonzero is the number of nonzero entries to allocate memory for.

    This function *does* call mpq_init on each mpq_t that is allocated.
    It does *not* clear the entries of v, if there are any.
    """
    cdef int i
    v.entries = <mpq_t*>sage_malloc(num_nonzero*sizeof(mpq_t))
    if v.entries == <mpq_t*> 0:
        raise MemoryError, "Error allocating memory"
    for i from 0 <= i < num_nonzero:
        mpq_init(v.entries[i])
    v.positions = <int*>sage_malloc(num_nonzero*sizeof(int))
    if v.positions == <int*> 0:
        raise MemoryError, "Error allocating memory"
    return 0

cdef int init_mpq_vector(mpq_vector* v, int degree, int num_nonzero) except -1:
    """
    Initialize a mpq_vector -- most user code *will* call this.
    """
    allocate_mpq_vector(v, num_nonzero)
    v.num_nonzero = num_nonzero
    v.degree = degree

cdef void clear_mpq_vector(mpq_vector* v):
    cdef int i
    # Free all mpq objects allocated in creating v
    for i from 0 <= i < v.num_nonzero:
        mpq_clear(v.entries[i])
    # Free entries and positions of those entries.
    # These were allocated from the Python heap.
    # If init_mpq_vector was not called, then this
    # will (of course!) cause a core dump.
    sage_free(v.entries)
    sage_free(v.positions)

cdef int mpq_binary_search0(mpq_t* v, int n, mpq_t x):
    """
    Find the position of the rational x in the array v, which has length n.
    Returns -1 if x is not in the array v.
    """
    cdef int i, j, k, c
    if n == 0:
        return -1
    i = 0
    j = n-1
    while i<=j:
        if i == j:
            if mpq_equal(v[i],x):
                return i
            return -1
        k = (i+j)/2
        c = mpq_cmp(v[k],x)
        if c > 0:       # v[k] > x
            j = k-1
        elif c < 0:     # v[k] < x
            i = k+1
        else:   # only possibility is that v[k] == x
            return k
    return -1

cdef int mpq_binary_search(mpq_t* v, int n, mpq_t x, int* ins):
    """
    Find the position of the integer x in the array v, which has length n.
    Returns -1 if x is not in the array v, and in this case ins is
    set equal to the position where x should be inserted in order to
    obtain an ordered array.

    INPUT:
       v -- array of mpq_t  (rational)
       n -- integer (length of array v)
       x -- mpq_t  (rational)
    OUTPUT:
       position of x (as an int)
       ins -- (call be pointer), the insertion point if x is not found.
    """
    cdef int i, j, k, c
    if n == 0:
        ins[0] = 0
        return -1
    i = 0
    j = n-1
    while i<=j:
        if i == j:
            c = mpq_cmp(v[i],x)
            if c == 0:          # v[i] == x
                ins[0] = i
                return i
            if c < 0:           # v[i] < x
                ins[0] = i + 1
            else:
                ins[0] = i
            return -1
        k = (i+j)/2
        c = mpq_cmp(v[k], x)
        if c > 0:               # v[k] > x
            j = k-1
        elif c < 0:             # v[k] < x
            i = k+1
        else:   # only possibility is that v[k] == x
            ins[0] = k
            return k
    # end while
    ins[0] = j+1
    return -1

cdef int mpq_vector_get_entry(mpq_t* ans, mpq_vector* v, int n) except -1:
    """
    Returns the n-th entry of the sparse vector v.  This
    would be v[n] in Python syntax.

    The return is done using the pointer ans, which is to an mpq_t
    that *must* have been initialized using mpq_init.
    """
    if n >= v.degree:
        raise IndexError, "Index must be between 0 and %s."%(v.degree - 1)
    cdef int m
    m = binary_search0(v.positions, v.num_nonzero, n)
    if m == -1:
        mpq_set_si(ans[0], 0,1)
        return 0
    mpq_set(ans[0], v.entries[m])
    return 0

cdef object mpq_vector_to_list(mpq_vector* v):
    """
    Returns a Python list of 2-tuples (i,x), where x=v[i] runs
    through the nonzero elements of x, in order.
    """
    cdef X
    cdef sage.rings.rational.Rational a
    cdef int i
    X = []
    for i from 0 <= i < v.num_nonzero:
        a = sage.rings.rational.Rational()
        a.set_from_mpq(v.entries[i])
        X.append( (v.positions[i], a) )
    return X

cdef int mpq_vector_set_entry(mpq_vector* v, int n, mpq_t x) except -1:
    """
    Set the n-th component of the sparse vector v equal to x.
    This would be v[n] = x in Python syntax.
    """
    if n >= v.degree or n < 0:
        raise IndexError, "Index must be between 0 and the degree minus 1."
        return -1
    cdef int i, m, ins
    cdef int m2, ins2
    cdef int *pos
    cdef mpq_t *e

    m = binary_search(v.positions, v.num_nonzero, n, &ins)

    if m != -1:
        # The position n was found in the array of positions.
        # Now there are two cases:
        #   1. x =/= 0, which is easy, and
        #   2. x = 0, in which case we have to recopy
        #      positions and entries, without the m-th
        #      element, and change num_nonzero.
        if mpq_sgn(x) != 0:   # x != 0,  case 1
            # v.entries[m] = x
            mpq_set(v.entries[m], x)
        else:        # case 2
            e = v.entries
            pos = v.positions
            allocate_mpq_vector(v, v.num_nonzero - 1)
            for i from 0 <= i < m:
                # v.entries[i] = e[i]
                mpq_set(v.entries[i], e[i])
                v.positions[i] = pos[i]
            for i from m < i < v.num_nonzero:
                # v.entries[i-1] = e[i]
                mpq_set(v.entries[i-1], e[i])
                v.positions[i-1] = pos[i]
            sage_free(e)
            sage_free(pos)
            v.num_nonzero = v.num_nonzero - 1
    else:
        # Allocate new memory and copy over elements from the
        # old array.  This is similar to case 2 above,
        # except we are inserting a new entry rather than
        # deleting an old one.  The new entry should be inserted
        # at position ins, which was computed using binary search.
        #
        # There is one exception -- if the new entry is 0, we
        # do nothing and return.
        if mpq_sgn(x) == 0:
            return 0
        v.num_nonzero = v.num_nonzero + 1
        e = v.entries
        pos = v.positions
        allocate_mpq_vector(v, v.num_nonzero)
        for i from 0 <= i < ins:
            # v.entries[i] = e[i]
            mpq_set(v.entries[i], e[i])
            v.positions[i] = pos[i]
        # v.entries[ins] = x
        mpq_set(v.entries[ins], x)
        v.positions[ins] = n
        for i from ins < i < v.num_nonzero:
            mpq_set(v.entries[i], e[i-1])
            v.positions[i] = pos[i-1]
        # Free the memory occupie by GMP rationals.
        # This -1 is because we incremented v.num_nonzero above.
        for i from 0 <= i < v.num_nonzero-1:
            mpq_clear(e[i])
        sage_free(e)
        sage_free(pos)

cdef mpq_t mpq_set_tmp
mpq_init(mpq_set_tmp)
cdef int mpq_vector_set_entry_str(mpq_vector* v, int n, char *x_str) except -1:
    """
    Set the n-th component of the sparse vector v equal to x.
    This would be v[n] = x in Python syntax.
    """
    mpq_set_str(mpq_set_tmp, x_str, 0)
    mpq_vector_set_entry(v, n, mpq_set_tmp)

cdef int add_mpq_vector_init(mpq_vector* sum,
                             mpq_vector* v,
                             mpq_vector* w,
                             mpq_t multiple) except -1:
    """
    Initialize sum and set sum = v + multiple*w.
    """
    if v.degree != w.degree:
        print "Can't add vectors of degree %s and %s"%(v.degree, w.degree)
        raise ArithmeticError, "The vectors must have the same degree."

    cdef int nz, i, j, k, do_multiply
    cdef mpq_vector* z
    cdef mpq_t tmp
    mpq_init(tmp)
    if mpq_cmp_si(multiple, 0, 1) == 0:
        init_mpq_vector(sum, v.degree, 0)
        return 0
    # Do not do the multiply if the multiple is 1.
    do_multiply = mpq_cmp_si(multiple, 1,1)

    z = sum
    # ALGORITHM:
    # 1. Allocate enough memory to hold the union of the two
    #    lists of positions.  We allocate the sum of the number
    #    of positions of both (up to the degree), to avoid
    #    having to make two passes.  This might be slightly wasteful of
    #    memory, but is faster.
    # 2. Move along the entries of v and w, copying them into the
    #    new position / entry array.  When position are the same,
    #    add modulo p.
    # 3. Set num_nonzero and return success code.

    # 1. Allocate memory:
    nz = v.num_nonzero + w.num_nonzero
    if nz > v.degree: nz = v.degree
    init_mpq_vector(z, v.degree, nz)
    # 2. Merge entries
    i = 0  # index into entries of v
    j = 0  # index into entries of w
    k = 0  # index into z (the vector we are creating)
    while i < v.num_nonzero or j < w.num_nonzero:
        if i >= v.num_nonzero:   # just copy w in
            z.positions[k] = w.positions[j]

            if do_multiply:
                # This means: z.entries[k] = (multiple*w.entries[j])
                mpq_mul(z.entries[k], multiple, w.entries[j])
            else:
                mpq_set(z.entries[k], w.entries[j])
            j = j + 1
            k = k + 1
        elif j >= w.num_nonzero:  # just copy v in
            z.positions[k] = v.positions[i]
            # This means: z.entries[k] = v.entries[i]
            mpq_set(z.entries[k], v.entries[i])
            i = i + 1
            k = k + 1
        elif v.positions[i] < w.positions[j]:  # copy entry from v in
            z.positions[k] = v.positions[i]
            # This means: z.entries[k] = v.entries[i]
            mpq_set(z.entries[k], v.entries[i])
            i = i + 1
            k = k + 1
        elif v.positions[i] > w.positions[j]: # copy entry from w in
            if do_multiply:
                # This means: tmp = multiple*w.entries[j]
                mpq_mul(tmp, multiple, w.entries[j])
                # This means: z.entries[k] = tmp
                mpq_set(z.entries[k], tmp)
            else:
                mpq_set(z.entries[k], w.entries[j])
            z.positions[k] = w.positions[j]
            k = k + 1
            j = j + 1
        else:                                 # equal, so add and copy
            if do_multiply:
                # This means: tmp = v.entries[i] + multiple*w.entries[j]
                mpq_mul(tmp, multiple, w.entries[j])
                mpq_add(tmp, tmp, v.entries[i])
            else:
                mpq_add(tmp, v.entries[i], w.entries[j])
            if mpq_sgn(tmp) != 0:
                z.positions[k] = v.positions[i]
                # This means: z.entries[k] = tmp
                mpq_set(z.entries[k], tmp)
                k = k + 1     # only increment if sum is nonzero!
            i = i + 1
            j = j + 1
        #end if
    # end while
    z.num_nonzero = k
    mpq_clear(tmp)
    return 0

cdef int scale_mpq_vector(mpq_vector* v, mpq_t scalar) except -1:
    if mpq_sgn(scalar) == 0:  # scalar = 0
        clear_mpq_vector(v)
        init_mpq_vector(v, v.degree, 0)
        return 0
    cdef int i
    for i from 0 <= i < v.num_nonzero:
        # v.entries[i] = scalar * v.entries[i]
        mpq_mul(v.entries[i], v.entries[i], scalar)
    return 0

cdef int mpq_vector_cmp(mpq_vector* v, mpq_vector* w):
    if v.degree < w.degree:
        return -1
    elif v.degree > w.degree:
        return 1
    cdef int i, c
    for i from 0 <= i < v.num_nonzero:
        c = mpq_cmp(v.entries[i], w.entries[i])
        if c < 0:
            return -1
        elif c > 0:
            return 1
    return 0
