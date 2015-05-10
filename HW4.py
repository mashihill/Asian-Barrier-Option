#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from math import *
import scipy.stats
import logging

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def BOPF(data):

    # Initial value
    S = data['S']
    X = data['X']
    t = data['t']
    n = data['n']
    H = data['H']
    s = data['s'] / 100  # convert from percentage to decimal
    r = data['r'] / 100
    k = data['k']
    u = exp(s * sqrt(t / n))
    d = 1 / u   # d = exp(-s * sqrt(t / n))
    r_ = r * t / n
    R = exp(r_)
    #a = ceil(log(X / (S * (d ** n))) / log(u / d))  # Smallest int S_T >= X
    p = (R - d) / (u - d)  # Risk-neutral P

    def Amax(j, i):
        maxsum = (S * ((1 - u ** (j - i + 1)) / (1 - u) + \
                        u ** (j-i) * d * (1 - d ** i) / (1 - d) ))
        return maxsum / (j + 1)

    def Amin(j, i):
        minsum = (S * ((1 - d ** (i + 1)) / (1 - d) + \
                        d ** i * u * (1 - u ** (j - i)) / (1 - u) ))
        return minsum / (j + 1)

    def Average(m, j, i):
        return (((k - m) / k) * Amin(j, i) + (m / k) * Amax(j, i))

    def findl(A, j, i):
        for l in range(k):
            if Average(l, j, i) <= A and A <= Average(l+1, j, i):
                return l
        #raise ValueError
        logger.warning('l not found')
        if A < Average(0, j, i):
            logger.warning('l return 0')
            return 0
        elif (A > Average(k, j, i)):
            logger.warning('l return k')
            return k
        else:
            logger.error('l error')
            return 0

    C = [[max(0, Average(m, n, i) - X) * (Average(m, n, i) <= H) for m in range(k+1)] for i in range(n+1)]
    logger.debug("C: %r", C)
    D = [None] * (k+1)

    # Asian barrier option
    for j in range(n)[::-1]:
        for i in range(j+1):
            for m in range(k+1):
                logger.debug("loop j=%s, i=%s, m=%s", j, i, m)
                a = Average(m, j, i)
                A_u = ((j+1) * a + S * u ** (j+1-i) * d ** i) / (j+2)
                logger.debug("A_u: %s", A_u)
                logger.debug("Amax: %s", Amax(j, i))
                logger.debug("Amin: %s", Amin(j, i))
                l = findl(A_u, j+1, i)
                try:
                    x = (A_u - Average(l+1, j+1, i)) / (Average(l, j+1, i) - Average(l+1, j+1, i))
                    C_u = x * C[i][l] + (1-x) * C[i][l+1]
                except:
                    x = 1
                    C_u = C[i][l]

                A_d = ((j+1) * a + S * u ** (j-i) * d ** (i+1)) / (j + 2)
                l = findl(A_d, j+1, i+1)
                try:
                    x = (A_d - Average(l+1, j+1, i+1)) / (Average(l, j+1, i+1) - Average(l+1, j+1, i+1))
                    C_d = x * C[i+1][l] + (1-x) * C[i+1][l+1]
                except:
                    x = 1
                    C_d = C[i+1][l]
                D[m] = 0 if a >= H else ((p * C_u + (1-p) * C_d) / R)
            for num in range(k+1):
                C[i][num] = D[num]

    print C[0][0]








    #callValueFlow = [max((S * (u ** (n-i)) * (d ** i)) - X, 0) for i in range(n+1)]

    # European Options
    #CallSum1 = CallSum2 = 0
    #PutSum1 = PutSum2 = 0

    #for _ in range(int(a), n):
    #    CallSum1 += scipy.stats.binom.pmf(_, n, p * u / R)
    #    CallSum2 += scipy.stats.binom.pmf(_, n, p)

    #for _ in range(int(a)):
    #    PutSum1 += scipy.stats.binom.pmf(_, n, p * u / R)
    #    PutSum2 += scipy.stats.binom.pmf(_, n, p)

    #EuroCall = S * CallSum1 - X * exp(-r_ * n) * CallSum2
    #EuroPut = X * exp(-r_ * n) * PutSum2 - S * PutSum1

    ###### America put
    ###### Initialize Value at time t
    #####ValueFlow = [max(X - (S * (u ** (n-i)) * (d ** i)), 0) for i in range(n+1)]
    #####callValueFlow = [max((S * (u ** (n-i)) * (d ** i)) - X, 0) for i in range(n+1)]

    ###### Run backward to time 0
    #####for time in reversed(range(n)):
    #####    # Payoff of early exercise
    #####    EarlyExercise = [max(X - (S * (u ** (time-i)) * (d ** i)), 0) for
    #####                     i in range(time+1)]

    #####    #callEarlyExercise = [max((S * (u ** (time-i)) * (d ** i)) - X, 0) for
    #####    #                 i in range(time+1)]
    #####    # Continuation value
    #####    ValueFlow = [((p * ValueFlow[i] + (1-p) * ValueFlow[i+1]) / R) for
    #####                 i in range(time+1)]

    #####    #callValueFlow = [((p * callValueFlow[i] + (1-p) * callValueFlow[i+1]) / R) for
    #####    #             i in range(time+1)]

    #####    # Find the larger value
    #####    ValueFlow = [max(EarlyExercise[i], ValueFlow[i]) for
    #####                 i in range(len(ValueFlow))]

    #####    #callValueFlow = [max(callEarlyExercise[i], callValueFlow[i]) for
    #####    #             i in range(len(callValueFlow))]

    # Output Information

    #####outputs = [('European Call', str(EuroCall)),
    #####           #('European Put', str(EuroPut)),
    #####           ('American Call', str(EuroCall)),
    #####           ('American Call', str(callValueFlow[0])),
    #####           ('American Put', str(ValueFlow[0]))]

    ###### Aligned output
    #####print "S=%r, X=%r, s=%r%%, t=%r, n=%r, r=%r %%:" % (S, X, data['s'],
    #####                                                    t, n, data['r'])
    #####for output in outputs:
    #####    print "- {item:13}: {value[0]:>4}.{value[1]:<12}".format(
    #####          item=output[0], value=output[1].split('.') if
    #####          '.' in output[1] else (output[1], '0'))


import sys
import json
if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location) as data_file:
            data = json.load(data_file)
        for test in data:
            BOPF(test)
        print "~~ end ~~"
    else:
        print 'This requires an input file.  Please select one from the data \
               directory. (e.g. python HW2.py ./data)'
