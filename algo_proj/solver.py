from math import ceil
from scipy import sparse
import numpy as np
import cvxpy as cvx

#Calculate equilibrium matrix B


def calcB(Nd, Cn, dof):
    m, n1, n2 = len(Cn), Cn[:,0].astype(int), Cn[:,1].astype(int)
    l, X, Y, Z = Cn[:,2], Nd[n2,0]-Nd[n1,0], Nd[n2,1]-Nd[n1,1], Nd[n2,2]-Nd[n1,2]
    d0, d1, d2, d3, d4, d5 = dof[n1*3], dof[n1*3+1], dof[n2*3], dof[n2*3+1], dof[n1*3+2], dof[n2*3+2]
    s = np.concatenate((-X/l * d0, -Y/l * d1, -Z/l * d4, X/l * d2, Y/l * d3, Z/l * d5))
    r = np.concatenate((n1*3, n1*3+1, n1*3+2, n2*3, n2*3+1, n2*3+2))
    c = np.tile(np.arange(m), 6)
    return sparse.coo_matrix((s, (r, c)), shape = (len(Nd)*3, m))
#Solve linear programming problem
def solveLP(Nd, Cn, f, dof, st, sc, jc):
    l = Cn[:, 2] + jc
    B = calcB(Nd, Cn, dof)
    a = cvx.Variable(len(Cn))
    obj = cvx.Minimize(np.transpose(l) * a)
    q, eqn, cons= [],  [], [a>=0]
    for k, fk in enumerate(f):
        q.append(cvx.Variable(len(Cn)))
        eqn.append(B * q[k] == fk * dof)
        cons.extend([eqn[k], q[k] >= -sc * a, q[k] <= st * a])
    prob = cvx.Problem(obj, cons)
    vol = prob.solve()
    q = [np.array(qi.value).flatten() for qi in q]
    a = np.array(a.value).flatten()
    u = [-(np.array(eqnk.dual_value).flatten()) for eqnk in eqn]
    return vol, a, q, u
#Check dual violation
def stopViolation(Nd, PML, dof, st, sc, u, jc):
    lst = np.where(PML[:,3]==False)[0]
    Cn = PML[lst]
    l = Cn[:,2] + jc
    B = calcB(Nd, Cn, dof).tocsc()
    y = np.zeros(len(Cn))
    for uk in u:

        yk = np.multiply(B.transpose().dot(uk) / l, np.array([[st], [(-1)*sc]]))
        y += np.amax(yk, axis=0)
    vioCn = np.where(y>1.0001)[0]
    vioSort = np.flipud(np.argsort(y[vioCn]))
    num = ceil(min(len(vioSort), 0.05*max( [len(Cn)*0.05, len(vioSort)])))
    for i in range(num):
            PML[lst[vioCn[vioSort[i]]]][3] = True
    return num == 0

#Member adding loop (inside)
def solveLoop(Nd, PML, dof, f, initials):
    init_Nd = np.array(Nd)
    init_PML = np.array(PML)
    Nds = []
    volumes = []
    Cns = []
    a_s = []
    qs = []
    us = []
    PMLs = []
    for itr in range(1, 100):
        Cn = PML[(PML[:, 3] + PML[:,4]) > 0]
        vol, a, q, u = solveLP(Nd, Cn, f, dof, initials[0], initials[1], initials[2])
        print("Itr: %d, vol: %f, mems: %d" % (itr, vol, len(Cn)))
        volumes.append(vol)
        need_stop =  stopViolation(Nd, PML, dof, initials[0], initials[1], u, initials[2])
        Cns.append(np.array(Cn))
        Nds.append(np.array(Nd))
        a_s.append(np.array(a))
        qs.append(np.array(q))
        us.append(np.array(u))
        PMLs.append(np.array(PML))
        if need_stop: break
    print("Volume: %f" % (vol))
    return init_Nd, init_PML, Cns, Nds, volumes, a_s, qs, us, PMLs





