DEFAULT_SINGLE_PRODUCTS = 1
DEFAULT_CAPACITY_MULTIPLIER = {"N": 2, "L": 1.3}
TIMELIMIT = 10
OTIMIZADOS_INDIVIDUAIS_PATH = "SOLUTION/INDIVIDUAIS/"
FINAL_PATH = "SOLUTION/FINAL/"
END_PRODUCTS = [1, 2, 5]
INSTANCES = ["2LLL1.DAT.dat", "2LLL3.DAT.dat"]
INSTANCES = [f"{i}LLL{j}.DAT.dat" for i in range(1, 11) for j in range(1, 11)] + [
    f"{i}HHH{j}.DAT.dat" for i in range(1, 11) for j in range(1, 11)
]
