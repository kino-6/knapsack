import random
import numpy
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import pandas as pd
import sys
import os
import csv

# stub3
# capacity_list = [10,4,1,2,10,10]
# value_list = [5.5,7.2,3.1,6.1,11,4.5,2.0]
# CAP_OVER_TH = -2.4

# load problem
if len(sys.argv) < 2:
    print("please input arg[1] = csv file")
    exit()

# 不揃いなcsv読み込み対策
rows = csv.reader(open(sys.argv[1], 'rt'))
data = []
for row in rows:
    data.append(row)
df = pd.DataFrame(data)
print(df)
elm_list = list(df.loc[:][0])
capacity_list = list(df.loc[elm_list.index("capacity")][1:])        # 容量
capacity_list = [float(item) for item in capacity_list if item is not None]

value_list = list(df.loc[elm_list.index("weight")][1:])             # 重さ
value_list = [float(item) for item in value_list if item is not None]

CAP_OVER_TH = float(df.loc[elm_list.index("CAP_OVER_TH")][1])       # 容量オーバー許容量
n_gene = len(value_list)                                            # 1個体あたりの遺伝子数
n_individuals = int(df.loc[elm_list.index("n_individuals")][1])     # 1世代あたりの個体数
n_generations = int(df.loc[elm_list.index("n_generations")][1])     # 世代数
p_cxpb = float(df.loc[elm_list.index("p_cxpb")][1])                 # 交叉率（交叉する個体数）
p_mutpb = float(df.loc[elm_list.index("p_mutpb")][1])               # 変異率（変異する個体数）
p_mutate_rate = float(df.loc[elm_list.index("p_mutate_rate")][1])   # 変異確率（遺伝子の変異率）
p_mutate = int(len(capacity_list) * p_mutate_rate)                  # 1個体の変異遺伝子数

print("==== params ================================================")
print("capacity_list: ", capacity_list)
print("value_list: ", value_list)
print("CAP_OVER_TH: ", CAP_OVER_TH)
print("n_gene: ", n_gene)
print("n_individuals: ", n_individuals)
print("n_generations: ", n_generations)
print("p_cxpb: ", p_cxpb)
print("p_mutpb: ", p_mutpb)
print("p_mutate_rate: ", p_mutate_rate)
print("p_mutate: ", p_mutate)

def evalKnapsack(individual):
    """individualの遺伝子(割付ID)を基に重さの評価を実施"""
    score = 0
    result = capacity_list[:]

    for i in range(len(individual)):
        result[ individual[i] ] -= value_list[i]

    for i in range(len(result)):
        if result[i] >= CAP_OVER_TH:
            score += result[i]
        else:
            score = sum(capacity_list)

    return score, 

def init_creator():
    """目的関数の方向性を設定"""
    # 評価する目的関数は1つ、個体の適応度を最大化
    creator.create("Fitness", base.Fitness, weights=(-1.0,))
    # numpy.ndarrayクラスを継承して、
    # fitness=creator.FitnessMaxというメンバ変数を追加したIndividualクラスを作成する
    creator.create("Individual", numpy.ndarray, fitness=creator.Fitness)
    return creator

def my_gene_generator(min, max):
    """遺伝子生成関数"""
    return random.randint(min, max)

def init_generator(creator):
    """遺伝子、個体、世代の生成手法の設定"""
    toolbox = base.Toolbox()
    # 遺伝子を生成する関数の定義
    toolbox.register("attr_item", my_gene_generator, 0, len(capacity_list)-1)
    # 個体を生成する関数の定義
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_item, n_gene)
    # 世代を生成する関数の定義
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    return toolbox

def mutateGene(min, max):
    return random.randint(min, max)

def mutateKnapsack(individual, indpb):
    mutate_list = random.choices(individual, k=indpb)
    for mutate_id in mutate_list:
        individual[mutate_id] = mutateGene(0,len(capacity_list)-1)
    return individual,

def operator_registration(toolbox):
    """評価関数・戦略の設定"""
    toolbox.register("evaluate", evalKnapsack)                              # evaluate = 評価関数
    toolbox.register("mate", tools.cxTwoPoint)                              # mate = 2点交叉
    toolbox.register("mutate", mutateKnapsack, indpb=p_mutate)            # mutate = bit反転
    toolbox.register("select", tools.selNSGA2)                          # select = tournament(3)

def stats_register():
    """ステート定義設定"""
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)
    return stats

def get_cxpoint(size):
    """2点交叉用 2点の設定"""
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else: # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1
    return cxpoint1, cxpoint2

def cxTwoPointCopy(ind1, ind2):
    """numpy用 2点交叉"""
    size = min(len(ind1), len(ind2))
    cxpoint1, cxpoint2 = get_cxpoint(size)
    
    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
        = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()
        
    return ind1, ind2

def print_result(individual, elm_list):
    """terminalへ結果出力"""
    print("sum of capacity_list:", sum(capacity_list))
    print("sum of value_list:", sum(value_list))

    cap_overed = (sum(capacity_list) - sum(value_list)) - CAP_OVER_TH

    if cap_overed < 0:
        print("  cap over! (over value:%f)" % cap_overed)
        print("  please recheck setting or CAP_OVER_TH (currently:%f)" % CAP_OVER_TH)

    for i in elm_list:
        print(i)


def main(toolbox):
    random.seed(42)

    # 初期世代の生成
    pop = toolbox.population(n=n_individuals)

    # numpy用 elite=1 戦略
    hof = tools.HallOfFame(1, similar=numpy.array_equal)

    # stats定義
    stats = stats_register()

    # main loop
    algorithms.eaSimple(pop, toolbox, cxpb=p_cxpb, mutpb=p_mutpb, ngen=n_generations, stats=stats,
                        halloffame=hof)

    # best個体の表示
    eval = float(evalKnapsack(hof[0])[0])
    print("Best individual is \n Eval:\n  %s, \n Gene:\n  %s" % (eval, hof[0]))
    elm_list = write_result(hof[0])
    print_result(hof[0], elm_list)

    return pop, stats, hof

def write_result(individual):
    """csv形式で結果を出力"""
    import datetime
    import time
    dt = datetime.datetime.fromtimestamp(time.time())

    input_path = sys.argv[1]
    output_name = str(os.path.dirname(input_path)) \
        + "\\" + str(os.path.splitext(os.path.basename(input_path))[0]) + "_" \
        + str(dt.strftime('%Y_%m_%d_%H_%M_%S')) \
        + str(os.path.splitext(input_path)[1])
    print("output file = ", output_name)

    elm_list = []
    line_list = []

    for i in range(len(capacity_list)+1):
        if i == 0:
            line_list.append("/")
        else:
            line_list.append(capacity_list[i-1])

    elm_list.append(line_list)

    for i in range(len(value_list)):
        line_list = []
        line_list.append(value_list[i])
        for j in range(len(capacity_list)):
            if individual[i] == j:
                line_list.append("o")
            else:
                line_list.append("-")
        elm_list.append(line_list)

    df_out = pd.DataFrame(elm_list)
    df_out.to_csv(output_name)

    return elm_list

if __name__ == "__main__":
    # 目的関数の方向性を設定
    creator = init_creator()
    # 遺伝子、個体、世代の生成手法の設定
    toolbox = init_generator(creator)

    # 進化手法の設定
    operator_registration(toolbox)

    # メインルーチン
    main(toolbox)
