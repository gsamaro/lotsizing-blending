from formulacao import Formulacao1
from utils import running_all_instance_with_chosen_capacity

if __name__ == "__main__":
    running_all_instance_with_chosen_capacity(
        Formulacao1, path_to_save="formulacao1.xlsx"
    )
