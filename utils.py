import os
import re
import types
from itertools import chain
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

from data import Data, DataAbstractClass, DataMultipleProducts

try:
    from mpi4py import MPI
    from mpi4py.futures import MPIPoolExecutor

    MPI_BOOL = True
except:
    print("mpi4py not running")
    MPI_BOOL = False

import gc
from abc import ABC

import constants


class FormulacaoType(ABC):
    data: DataAbstractClass
    model: object


def print_info(data: DataAbstractClass, status: str) -> None:
    if MPI_BOOL:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
    else:
        rank = None
    print(f"Instance = {data.instance} Cap = {data.capacity} {status} Process {rank}")


def add_new_kpi(kpis: Dict[str, any], result, data: DataAbstractClass) -> dict:
    kpis["Instance"] = data.instance
    kpis["Best Bound"] = result.solve_details.best_bound
    kpis["Gap"] = result.solve_details.gap
    kpis["Nodes Processed"] = result.solve_details.gap
    kpis["Tempo de Solução"] = result.solve_details.time
    kpis["capacity"] = data.capacity
    return kpis


def get_and_save_results(path_to_read: str, path_to_save: Path) -> None:
    list_files = []
    for file in Path(path_to_read).glob("*"):
        list_files.append(pd.read_excel(file))
    df_results_optimized = pd.concat(list_files)
    df_results_optimized.to_excel(path_to_save, index=False)


def solve_optimized_model(
    dataset: str,
    Formulacao: FormulacaoType,
    amount_of_end_products,
    capacity_multiplier,
) -> None:
    data = DataMultipleProducts(
        dataset,
        capacity_multiplier=capacity_multiplier,
        amount_of_end_products=amount_of_end_products,
    )
    f1 = Formulacao(data)
    mdl = f1.model
    mdl.parameters.timelimit = constants.TIMELIMIT
    result = mdl.solve()

    if result == None:
        print_info(data, "infactível")
        return None

    kpis = mdl.kpis_as_dict(result, objective_key="objective_function")
    kpis = add_new_kpi(kpis, result, data)

    # Cálculo da relaxação linear
    relaxed_model = mdl.clone()
    status = relaxed_model.solve(url=None, key=None, log_output=False)

    relaxed_objective_value = relaxed_model.objective_value
    kpis["Relaxed Objective Value"] = relaxed_objective_value

    suffix_path = str(data)
    complete_path_to_save = Path.resolve(
        Path(constants.OTIMIZADOS_INDIVIDUAIS_PATH) / Path(suffix_path)
    )

    df_results_optimized = pd.DataFrame([kpis])
    df_results_optimized.to_excel(f"{complete_path_to_save}.xlsx", index=False)

    print_info(data, "concluído")
    gc.collect()


def running_all_instance_with_chosen_capacity(
    Formulacao: FormulacaoType, path_to_save: str
):
    final_results = []

    if not MPI_BOOL:
        for dataset in constants.INSTANCES:
            for end_products in constants.END_PRODUCTS:
                for capmult in constants.DEFAULT_CAPACITY_MULTIPLIER.keys():

                    best_result = solve_optimized_model(
                        dataset,
                        Formulacao,
                        amount_of_end_products=end_products,
                        capacity_multiplier=capmult,
                    )

                    if best_result:
                        final_results.append(best_result)
    else:
        with MPIPoolExecutor() as executor:
            futures = executor.starmap(
                solve_optimized_model,
                (
                    (dataset, Formulacao, end_products, capmult)
                    for dataset in constants.INSTANCES
                    for end_products in constants.END_PRODUCTS
                    for capmult in constants.DEFAULT_CAPACITY_MULTIPLIER.keys()
                ),
            )
            final_results.append(futures)
            executor.shutdown(wait=True)

    get_and_save_results(
        path_to_read=constants.OTIMIZADOS_INDIVIDUAIS_PATH,
        path_to_save=Path.resolve(Path(constants.FINAL_PATH) / Path(path_to_save)),
    )
    print(f"Concluído")
