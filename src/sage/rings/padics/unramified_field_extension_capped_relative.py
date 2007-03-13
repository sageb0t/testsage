import sage.rings.polynomial_element
import sage.rings.padics.padic_field_capped_relative
import sage.rings.padics.unramified_extension_generic
import sage.rings.padics.padic_field_extension_generic
import sage.rings.padics.unramified_extension_capped_relative_element
import sage.rings.padics.padic_field_generic
import sage.rings.infinity

infinity = sage.rings.infinity.infinity
Polynomial = sage.rings.polynomial_element.Polynomial
pAdicFieldCappedRelative = sage.rings.padics.padic_field_capped_relative.pAdicFieldCappedRelative
UnramifiedExtensionGeneric = sage.rings.padics.unramified_extension_generic.UnramifiedExtensionGeneric
pAdicFieldExtensionGeneric = sage.rings.padics.padic_field_extension_generic.pAdicFieldExtensionGeneric
UnramifiedExtensionCappedRelativeElement = sage.rings.padics.unramified_extension_capped_relative_element.UnramifiedExtensionCappedRelativeElement
pAdicFieldGeneric = sage.rings.padics.padic_field_generic.pAdicFieldGeneric

class UnramifiedFieldExtensionCappedRelative(UnramifiedExtensionGeneric, pAdicFieldExtensionGeneric):
    r"""
    Unramified Extension of a p-adic field with capped absolute precision

    You should not create this class directly unless you know what you're doing.  Use ExtensionFactory.
    """
    def __init__(self, base, poly, names, prec, halt, print_mode):
        UnramifiedExtensionGeneric.__init__(self, poly, names, prec, print_mode)

    def __call__(self, x, absprec = infinity, relprec = infinity):
        return UnramifiedExtensionCappedRelativeElement(self, x, absprec, relprec)

    def gen(self, n = 0):
        if n == 0:
            try:
                return self._gen
            except AttributeError:
                self._gen = UnramifiedExtensionCappedRelativeElement(self, self.polynomial_ring().gen(), check = False, construct = True)
                return self._gen
