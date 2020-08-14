# knapsack
knapsack by deap

# setup
1. install conda  

autor env:
  conda version : 4.8.2

2. install deap
```bat
pip install deap
```

# abstruct
1. Input problem file(csv)

example: data\problem_01.csv

```csv:problem_01.csv
# allocation_of_program
capacity,16,32,64       <- knapsack size
weight,30,12,60         <- baggage
# setting
CAP_OVER_TH,0           <- allow capacity over
n_individuals,1000
n_generations,100
p_cxpb,0.5
p_mutpb,0.2
p_mutate_rate,0.2
```

2. Run knapsack.py

```bat
python knapsack.py data\problem_01.csv
```

3. Output Data

example: data\problem_01_2020_08_14_22_57_03.csv  <- time stamp

```csv
,0,1,2,3
0,/,16,32,64
1,30,-,o,-
2,12,o,-,-
3,60,-,-,o
```
-> Optimal combination is...

```
baggage/capacity
    16  32  64
30  -   o   -
12  o   -   -
60  -   -   o
```

