##############################################################################
#       Copyright (C) 2010 Nathann Cohen <nathann.cohen@gmail.com>
#  Distributed under the terms of the GNU General Public License (GPL)
#  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
##############################################################################

from sage.numerical.backends.generic_backend cimport GenericBackend

include '../../ext/stdsage.pxi'
include '../../ext/cdefs.pxi'

from libcpp cimport bool

# apparently sage's cython can't import string! until it does...
#cdef extern from "<string>" namespace "std":
#    cdef cppclass string:
#        string()
#        string(char *)
#        char * c_str()

cdef extern from *:
    ctypedef double* const_double_ptr "const double*"

cdef extern from "../../local/include/coin/CbcStrategy.hpp":
    cdef cppclass CbcStrategy:
        pass
    cdef cppclass CbcStrategyDefault(CbcStrategy):
        CbcStrategyDefault(int cutsOnlyAtRoot=?, int numberStrong = ?, int numberBeforeTrust = ?, int printLevel = ?)

cdef extern from "../../local/include/coin/CoinPackedVectorBase.hpp":
    cdef cppclass CoinPackedVectorBase:
        pass

cdef extern from "../../local/include/coin/CoinPackedVector.hpp":
     cdef cppclass CoinPackedVector(CoinPackedVectorBase):
         void insert(float, float)
     CoinPackedVector *new_CoinPackedVector "new CoinPackedVector" ()
     void del_CoinPackedVector "delete" (CoinPackedVector *)

cdef extern from "../../local/include/coin/CoinShallowPackedVector.hpp":
     cdef cppclass CoinShallowPackedVector:
         void insert(float, float)
         int * getIndices ()
         double * getElements ()
         int getNumElements ()
     CoinShallowPackedVector *new_CoinShallowPackedVector "new CoinShallowPackedVector" ()
     void del_CoinShallowPackedVector "delete" (CoinShallowPackedVector *)

cdef extern from "../../local/include/coin/CoinPackedMatrix.hpp":
     cdef cppclass CoinPackedMatrix:
         void setDimensions(int, int)
         void appendRow(CoinPackedVector)
         CoinShallowPackedVector getVector(int)
     CoinPackedMatrix *new_CoinPackedMatrix "new CoinPackedMatrix" (bool, double, double)
     void del_CoinPackedMatrix "delete" (CoinPackedMatrix *)

cdef extern from "../../local/include/coin/CoinMessageHandler.hpp":
     cdef cppclass CoinMessageHandler:
         void setLogLevel (int)
         int LogLevel ()
     CoinMessageHandler *new_CoinMessageHandler "new CoinMessageHandler" ()
     void del_CoinMessageHandler "delete" (CoinMessageHandler *)

cdef extern from "../../local/include/coin/OsiSolverParameters.hpp":
    cdef enum OsiIntParam:
        OsiMaxNumIteration = 0, OsiMaxNumIterationHotStart, OsiNameDiscipline, OsiLastIntParam

cdef extern from "../../local/include/coin/OsiSolverInterface.hpp":

     cdef cppclass OsiSolverInterface:

        # clone
        OsiSolverInterface * clone(bool copyData)

        # info about LP -- see also info about variable data
        int getNumCols()
        int getNumRows()
        double * getObjCoefficients()
        double getObjSense()
        double * getRowLower()
        double * getRowUpper()
        CoinPackedMatrix * getMatrixByRow()
        #string getRowName(int rowIndex, unsigned maxLen=?)
        #string setObjName(int ndx, string name)
        #string getObjName(unsigned maxLen=?)
        #void setObjName(string name)

        # info about solution or solver
        int isAbandoned()
        int isProvenPrimalInfeasible()
        int isProvenDualInfeasible()
        int isPrimalObjectiveLimitReached()
        int isDualObjectiveLimitReached()
        int isIterationLimitReached()
        int isProvenOptimal()
        double getObjValue()
        double * getColSolution()

        # initialization
        int setIntParam(OsiIntParam key, int value)
        void setObjSense(double s)

        # set upper, lower bounds
        void setColLower(double * array)
        void setColLower(int elementIndex, double elementValue)
        void setColUpper(double * array)
        void setColUpper(int elementIndex, double elementValue)

        # set variable data
        void setContinuous(int index)
        void setInteger(int index)
        void setObjCoeff( int elementIndex, double elementValue )
        void addCol(int numberElements, int * rows, double * elements, double collb, double colub, double obj)

        # info about variable data -- see also info about solution or solver
        int isContinuous(int colNumber)
        double * getColLower()
        double * getColUpper()

        # add, delete rows
        void addRow(CoinPackedVectorBase & vec, double rowlb, double rowub)
        void deleteRows(int num, int *)

        # io
        void writeMps(char *filename, char *extension, double objSense)
        void writeLp(char *filename, char *extension, double epsilon, int numberAcross, int decimals, double objSense, bool useRowNames)

        # miscellaneous
        double getInfinity()

cdef extern from "../../local/include/coin/CbcModel.hpp":
     cdef cppclass CbcModel:
         # default constructor
         CbcModel()
         # constructor from solver
         CbcModel(OsiSolverInterface & si)
         # assigning, owning solver
         void assignSolver(OsiSolverInterface * & solver, bool deleteSolver=?)
         void setModelOwnsSolver(bool ourSolver)
         # get solver
         OsiSolverInterface * solver()
         # copy constructor
         CbcModel(CbcModel & rhs, int cloneHandler = ?)
         # shut up
         void setLogLevel(int value)
         int logLevel()
         # assign strategy
         void setStrategy(CbcStrategy & strategy)
         # threads
         void setNumberThreads (int)
         int getSolutionCount()
         # solve
         void branchAndBound(int doStatistics = ?)
         # not sure we need this but it can't hurt
         CoinMessageHandler * messageHandler ()
     void CbcMain0(CbcModel m)

     CbcModel *new_CbcModel "new CbcModel" ()
     void del_CbcModel "delete" (CbcModel *)

cdef extern from "../../local/include/coin/ClpSimplex.hpp":
    cdef cppclass ClpSimplex:
        void setNumberThreads(int)

cdef extern from "../../local/include/coin/OsiClpSolverInterface.hpp":

     cdef cppclass OsiClpSolverInterface(OsiSolverInterface):

        # ordinary constructor
        OsiClpSolverInterface()
        # copy constructor
        OsiClpSolverInterface(OsiClpSolverInterface &si)
        # log level
        void setLogLevel(int value)

cdef class CoinBackend(GenericBackend):

    cdef OsiSolverInterface * si
    cdef CbcModel * model
    cdef int log_level

    cdef list col_names, row_names
    cdef str prob_name

    cpdef CoinBackend copy(self)
