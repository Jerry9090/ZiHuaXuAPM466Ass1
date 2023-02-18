import matplotlib.pyplot as plt
import math
import numpy as np
from datetime import date
import datetime
from scipy.linalg import eig


def calculate_last(this_date: str, star_date: str, p=182):
    d = this_date.split('/')
    this_date = date(int(d[0]), int(d[1]), int(d[2]))
    d = star_date.split('/')
    star_date = date(int(d[0]), int(d[1]), int(d[2]))
    # print(star_date,this_date)
    return star_date - datetime.timedelta(math.ceil((this_date - star_date).days % p))


def caulate_ytm(copon_rate: float, n: int, price: float, fv: float = 100):
    lr = 0.0000001
    num_itr = 1000
    ytm = 0.01
    l=[]
    v=[]
    for i in range(num_itr):
        ytm = ytm - lr * ytm_direative(copon_rate, ytm, n, price, fv)
        l.append(ytm)
        v.append(np.abs(ytm_value(copon_rate,ytm,n,price)))
    t=[]
    for i in range(10):
        t.append(ytm_value(copon_rate,i,n,price))
    return ytm


def ytm_value(copon_rate: float, curr_ytm: float, n: int, price: float, fv: float = 100):
    l = np.asarray([fv*copon_rate]*n)
    l[-1]=l[-1]+fv
    n=np.asarray(list(range(n)))+1
    return np.sum(l/(1+curr_ytm)**n)-price


def ytm_direative(copon_rate: float, curr_ytm: float, n: int, price: float, fv: float = 100):
    nl = np.asarray(list(range(n))) + 1
    #print(-np.sum(copon_rate*fv*nl/((1+curr_ytm)**(nl+1))),fv/((1+curr_ytm)**(n+1)))
    if ytm_value(copon_rate,curr_ytm,n,price,fv)>0:
        return -np.sum(copon_rate*fv*nl/((1+curr_ytm)**(nl+1))) - fv/((1+curr_ytm)**(n+1))
    return np.sum(copon_rate*fv*nl/((1+curr_ytm)**(nl+1))) + fv/((1+curr_ytm)**(n+1))


def dirty(clean: float, settle_date: date, last_coupoundate: date, coupondrate: float):
    return clean + (settle_date - last_coupoundate).days / 365 * coupondrate * 100


def spot_rate(coupondrate: float, dirty_price: float, year_to_maturity: float):
    return coupondrate * 100 / 200 + (100 / dirty_price - 1) / year_to_maturity


def foward_rate(ra, rb, ta):
    return ((1 + ra) ** ta / (1 + rb) - 1) ** (1 / (ta - 1))


if __name__ == '__main__':
    f = open("Selected Data A1.csv", 'r')
    raw_data = f.read().split('\n')
    data = [i.split(',') for i in raw_data][:-1]
    #print(data)
    header = data[0]
    #print(header)
    values = data[1:]
    #print(values)
    clean_prices = []
    for i in values:
        clean_prices.append(list((float(k) for k in i[8:-1])))
    #print(clean_prices)
    last_coupoudate = []
    for i in values:
        # print("i:",i)
        last_coupoudate.append(calculate_last(i[7], "2023/1/16"))
    #print(last_coupoudate)
    cop_rate = []
    for i in values:
        cop_rate.append(float(i[2][:-1]) / 100)
    #print(cop_rate)
    year_to_mat = []
    for i in values:
        year_to_mat.append(float(i[4]) / 12)
    #print(year_to_mat)

    settle_date = []
    for i in header[8:-1]:
        d = i.split('/')

        settle_date.append(date(int(d[0]), int(d[1]), int(d[2])))
    #print(settle_date)

    dirty_price = []
    for i in range(len(clean_prices)):
        a = []
        for j in range(len(clean_prices[i])):
            a.append(dirty(clean_prices[i][j], settle_date[j], last_coupoudate[i], cop_rate[i]))
        dirty_price.append(a)
    #print('d', dirty_price)

    spot = []
    for i in range(len(dirty_price)):
        a = []
        for j in range(len(dirty_price[i])):
            a.append(spot_rate(cop_rate[i], dirty_price[i][j], year_to_mat[i]))
        spot.append(a)
    #print(spot)
    f = []
    for i in range(len(spot)):
        a = []
        for j in range(1, 5):
            a.append(foward_rate(spot[i][j], spot[i][0], j + 1))
        f.append(a)
    #print(f)

    ytm = []
    for i in range(len(dirty_price)):
        a=[]
        for j in range(len(dirty_price[i])):
            a.append(caulate_ytm(cop_rate[i],10,dirty_price[i][j]))
        ytm.append(a)
    #print(ytm)
    # print(raw_data)
    # print(data)
    sytm = np.asarray(ytm).T
    for i in sytm:
        plt.plot(year_to_mat,i)
    plt.show()
    sp = np.asarray(spot).T
    for i in sp:
        plt.plot(year_to_mat, i)
    plt.show()
    fp = np.asarray(f).T
    for i in f:
        plt.plot([2, 3, 4, 5], i)
    plt.show()

    # Covariance matrices
    matrix_yield = np.zeros([5, 9])
    matrix_forward = np.zeros([4, 9])
    # YIELD
    for i in range(5):
        for j in range(9):
            matrix_yield[i, j] = np.log(ytm[i][j + 1] / ytm[i][j])
    for i in range(4):
        for j in range(9):
            matrix_forward[i, j] = np.log(f[j + 1][i] / f[j][i])

    Cov_yield = np.cov(matrix_yield)
    Cov_forward = np.cov(matrix_forward)

    print("Covariance Yield: ",Cov_yield)

    eig_yield = eig(Cov_yield)
    print("Eigen Yield: ", eig_yield)

    print("Forward Covariance: ",Cov_forward)

    eig_for = eig(Cov_forward)
    print("Forward Eigen: ",eig_for)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
