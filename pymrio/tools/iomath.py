""" Mathematical functions for input output calculations

All methods here should follow the functional programming paradigm

Note
----
To avoid namespace pollution everythin here starts with calc_

"""

import pandas as pd
import numpy as np

import pymrio.tools.ioutil as ioutil

def calc_x(Z, Y):
    """ Calculate the industry output x from the Z and Y matrix 
   
    Parameters
    ----------
    Z : pandas.DataFrame or numpy.array
        Symmetric input output table (flows)
    Y : pandas.DataFrame or numpy.array
        final demand with categories (1.order) for each country (2.order)

    Returns
    -------
    pandas.DataFrame or numpy.array
        Industry output x as column vector
        The type is determined by the type of Z. If DataFrame index as Z

    """
    result = np.reshape(np.sum(np.hstack((Z, Y)), 1 ), (-1, 1))
    if type(Z) is pd.DataFrame:
        result = pd.DataFrame(result, index = Z.index, columns = ['indout'])
    return result

def calc_x_from_L(L, y):
    """ Calculate the industry output x from L and a y vector
   
    Parameters
    ----------
    L : pandas.DataFrame or numpy.array
        Symmetric input output Leontief table
    y : pandas.DataFrame or numpy.array
        a column vector of the total final demand

    Returns
    -------
    pandas.DataFrame or numpy.array
        Industry output x as column vector
        The type is determined by the type of L. If DataFrame index as L

    """
    x = L.dot(y)
    if type(L) is pd.DataFrame:
        x.columns = ['indout']
    return x

def calc_Z(A, x):
    """ calculate the Z matrix (flows) from A and x

    Parameters
    ----------
    A : pandas.DataFrame or numpy.array
        Symmetric input output table (coefficients)
    x : pandas.DataFrame or numpy.array
        Industry output column vector

    Returns
    -------
    pandas.DataFrame or numpy.array
        Symmetric input output table (flows) Z
        The type is determined by the type of A. 
        If DataFrame index/columns as A

    """
    if type(x) is pd.DataFrame:
        x=x.values
    x=x.reshape((1, -1)) # use numpy broadcasting - much faster 
    # (but has to ensure that x is a row vector)
    #return A.dot(np.diagflat(x)) # old mathematical form
    if type(A) is pd.DataFrame:
        return pd.DataFrame(A.values * x, index=A.index, columns=A.columns)
    else:
        return A*x

def calc_A(Z, x):
    """ Calculate the A matrix (coefficients) from Z and x 

    Parameters
    ----------
    Z : pandas.DataFrame or numpy.array
        Symmetric input output table (flows)
    x : pandas.DataFrame or numpy.array
        Industry output column vector

    Returns
    -------
    pandas.DataFrame or numpy.array
        Symmetric input output table (coefficients) A
        The type is determined by the type of Z. 
        If DataFrame index/columns as Z

    """
    if type(x) is pd.DataFrame:
        x=x.values
    if (type(x) is not np.ndarray) and (x == 0):
        recix=0
    else:
        recix = 1/x
        recix[recix==np.inf]=0
        recix=recix.reshape((1, -1))  # use numpy broadcasting - factor ten faster 
    #return Z.dot(np.diagflat(recix)) # Mathematical form - slow
    if type(Z) is pd.DataFrame:
        return pd.DataFrame(Z.values * recix, index=Z.index, columns=Z.columns)
    else:
        return Z*recix

def calc_L(A):
    """ Calculate the Leontief L from A 

    Parameters
    ----------
    A : pandas.DataFrame or numpy.array
        Symmetric input output table (coefficients)

    Returns
    -------
    pandas.DataFrame or numpy.array
        Leontief input output table L
        The type is determined by the type of A. 
        If DataFrame index/columns as A

    """
    I = np.eye(A.shape[0])
    if type(A) is pd.DataFrame:
        return pd.DataFrame(np.linalg.inv(I-A), 
                index=A.index, columns=A.columns)
    else:
        return np.linalg.inv(I-A) 

def calc_S(F, x):
    """ Calculate extensions/factor inputs coefficients

    Parameters
    ----------
    F : pandas.DataFrame or numpy.array
        Total direct impacts
    x : pandas.DataFrame or numpy.array
        Industry output column vector

    Returns
    -------
    pandas.DataFrame or numpy.array
        Direct impact coefficients S
        The type is determined by the type of F. 
        If DataFrame index/columns as F

    """ 
    return calc_A(F, x)

def calc_F(S,x):
    """ Calculate total direct impacts from the impact coefficients

    Parameters
    ----------
    S : pandas.DataFrame or numpy.array
        Direct impact coefficients S
    x : pandas.DataFrame or numpy.array
        Industry output column vector

    Returns
    -------
    pandas.DataFrame or numpy.array
        Total direct impacts F
        The type is determined by the type of S. 
        If DataFrame index/columns as S

    """ 
    return calc_Z(S, x)


def calc_M(S, L):
    """ Calculate multipliers of the extensions

    Parameters
    ----------
    L : pandas.DataFrame or numpy.array
        Leontief input output table L
    S : pandas.DataFrame or numpy.array
        Direct impact coefficients

    Returns
    -------
    pandas.DataFrame or numpy.array
        Multipliers M
        The type is determined by the type of D. 
        If DataFrame index/columns as D

    """ 
    return S.dot(L)

def calc_e(M, Y):
    """ Calculate total impacts (footprints of consumption Y) 

    Parameters
    ----------
    M : pandas.DataFrame or numpy.array
        Multipliers 
    Y : pandas.DataFrame or numpy.array
        Final consumption

    TODO - this must be completely redone (D, check for dataframe, ...)

    Returns
    -------
    pandas.DataFrame or numpy.array
        Multipliers m
        The type is determined by the type of M. 
        If DataFrame index/columns as M   
    The calcubased on multipliers M and finald demand Y """

    return M.dot(Y)

def recalc_M(S, D_fp, Y, nr_sectors):
    """ Calculate Multipliers based on footprints.

    Parameters
    ----------
    D_fp : pandas.DataFrame or numpy array
        Footprint per sector and country
    Y : pandas.DataFrame or numpy array
        Final demand: aggregated across categories or just one category, one
        column per country. This will be diagonalized per country block.
        The diagonolized form must be invertable for this method to work.
    nr_sectors : int
        Number of sectors in the MRIO

    Returns
    -------

    pandas.DataFrame or numpy.array
        Multipliers M
        The type is determined by the type of D_fp. 
        If DataFrame index/columns as D_fp   


    """

    Y_diag = ioutil.diagonalize_blocks(Y.values, blocksize = nr_sectors)
    Y_inv = np.linalg.inv(Y_diag)
    M = D_fp.dot(Y_inv)
    if type(D_fp) is pd.DataFrame:
        M.columns = D_fp.columns
        M.index = D_fp.index

    return M

def calc_accounts(S, L, Y, nr_sectors):
    """ Calculate sector specific footprints, terr, imp and exp accounts

    The total industry output x for the calculation 
    is recalculated from L and y

    Parameters
    ----------
    L : pandas.DataFrame
        Leontief input output table L
    S : pandas.DataFrame
        Direct impact coefficients
    Y : pandas.DataFrame
        Final demand: aggregated across categories or just one category, one
        column per country
    nr_sectors : int
        Number of sectors in the MRIO


    Returns
    -------
    Tuple 
        (D_fp, D_terr, D_imp, D_exp)

        Format: D_row x L_col (=nr_countries*nr_sectors)

        - D_fp        Footprint per sector and country
        - D_terr      Total factur use per sector and country
        - D_imp       Total global factor use to satisfy total final demand in
                      the country per sector
        - D_exp       Total factor use in one country to satisfy final demand in
                      all other countries (per sector)
    """
    # diagonalize each sector block per country
    # this results in a disaggregated y with final demand per country per
    # sector in one column
    Y_diag = ioutil.diagonalize_blocks(Y.values, blocksize = nr_sectors)
    x_diag = L.dot(Y_diag)
    x_tot  = x_diag.values.sum(1)
    del Y_diag

    D_fp = pd.DataFrame(S.values.dot(x_diag), 
                        index=S.index, 
                        columns = S.columns)
    #D_terr = S.dot(np.diagflat(x_tot))
    D_terr = pd.DataFrame(S.values*x_tot.reshape((1, -1)), 
                          index = S.index, 
                          columns = S.columns) # faster broadcasted calculation
    
    # for the traded accounts set the domestic industry output to zero
    dom_block = np.zeros((nr_sectors, nr_sectors))
    x_trade = ioutil.set_block(x_diag.values, dom_block)   
    D_imp = pd.DataFrame(S.values.dot(x_trade), 
                         index=S.index, 
                         columns = S.columns)

    x_exp = x_trade.sum(1)
    #D_exp = S.dot(np.diagflat(x_exp))
    D_exp = pd.DataFrame(S.values * x_exp.reshape((1, -1)), 
                         index = S.index, 
                         columns = S.columns)   # faster broadcasted version

    return (D_fp, D_terr, D_imp, D_exp)


