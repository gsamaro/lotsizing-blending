DEFAULT_SINGLE_PRODUCTS = 1
DEFAULT_CAPACITY_MULTIPLIER = {"N": 2, "L": 1.3}
DEFAULT_TYPE_INGREDIENTS_CAPACITY = "W"
CAPACITY_INGREDIENTS = ["S"]
TIMELIMIT = 180
OTIMIZADOS_INDIVIDUAIS_PATH = "SOLUTION/INDIVIDUAIS/"
FINAL_PATH = "SOLUTION/FINAL/"
END_PRODUCTS = [1, 5, 10]
INSTANCES = ["2LLL1.DAT.dat"]
INSTANCES = [f"{i}LLL{j}.DAT.dat" for i in [2, 5, 10] for j in range(1, 11)] + [
    f"{i}HHH{j}.DAT.dat" for i in [2, 5, 10] for j in range(1, 11)
]
COEFICIENTS_CAPACITY = [2, 1.3]
COEFICIENTS_CAPACITY = [1.7, 1.4, 1.3, 1.1, 1.05, 1.03, 1.005, 1]
