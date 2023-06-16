import random

from TSPGA_Problem import MyProblem

import geatpy as ea


# 定义outFunc()函数
def outFunc(alg, pop):  # alg 和 pop为outFunc的固定输入参数，分别为算法对象和每次迭代的种群对象。
    # alg.recOper.XOVR = 0.5  # probability of crossover
    alg.mutOper.Pm = 0.7  # probability of mutation
    # res = alg.BestIndi.Phen
    # print('第 %d 代' % alg.currentGen)
    # print(alg.BestIndi.Phen, alg.BestIndi.ObjV, alg.recOper.XOVR, alg.mutOper.Pm)
    # return res


def ga():
    i = random.randint(0, 100)
    # print(i)
    # 实例化问题
    problem = MyProblem()

    # 构建算法
    algorithm = ea.soea_SEGA_templet(problem,
                                    ea.Population(Encoding='RI', NIND=20),
                                    MAXGEN=250,  # 最大进化代数
                                    logTras=1,  # 表示每隔多少代记录一次日志信息，0表示不记录。
                                    trappedValue=1e-6,  # 单目标优化陷入停滞的判断阈值。
                                    maxTrappedCount=10,  # 进化停滞计数器最大上限值。
                                    outFunc=outFunc)

    # 求解
    res = ea.optimize(algorithm, seed=i, verbose=False, drawing=0, outputMsg=True, drawLog=False, saveFlag=True,
                      dirName='result')
    # print(res)
    return res


if __name__ == '__main__':
    ga()
