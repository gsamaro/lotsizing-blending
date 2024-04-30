import os
import re
import types
from itertools import chain
from multiprocessing import Pool
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
        size = comm.Get_size()
        name = MPI.Get_processor_name()
    else:
        rank = None
        size = None
        name = "localhost"
    print(
        f"Instance = {data.instance} Cap = {data.capacity} Produtos {data.amount_of_end_products} {status} Process {rank} of {size} on {name}"
    )


def add_new_kpi(kpis: Dict[str, any], result, data: DataAbstractClass) -> dict:
    kpis["Instance"] = data.instance
    kpis["Best Bound"] = result.solve_details.best_bound
    kpis["Gap"] = result.solve_details.gap
    kpis["Nodes Processed"] = result.solve_details.gap
    kpis["Tempo de Solução"] = result.solve_details.time
    kpis["capacity"] = data.capacity
    kpis["capacity_multiplier"] = data.capacity_multiplier
    kpis["amount_of_end_products"] = data.amount_of_end_products
    return kpis


def get_value_df(mdl, variable, value_name, key_columns):
    return mdl.solution.get_value_df(
        variable, value_column_name=value_name, key_column_names=key_columns
    ).melt(id_vars=key_columns, value_vars=[value_name])


def get_and_save_results(path_to_read: str, path_to_save: Path) -> None:
    list_files = []
    for file in Path(path_to_read).glob("*"):
        list_files.append(pd.read_excel(file, engine="openpyxl"))
    df_results_optimized = pd.concat(list_files)
    df_results_optimized.to_excel(
        Path.resolve(Path(path_to_read) / Path(path_to_save)),
        index=False,
        engine="openpyxl",
    )


def solve_optimized_model(
    dataset: str,
    Formulacao: FormulacaoType,
    amount_of_end_products,
    capacity_multiplier,
):
    data = DataMultipleProducts(
        dataset,
        capacity_multiplier=capacity_multiplier,
        amount_of_end_products=amount_of_end_products,
    )
    f1 = Formulacao(data)
    mdl = f1.model
    mdl.set_time_limit(constants.TIMELIMIT)
    mdl.context.cplex_parameters.threads = 1
    result = mdl.solve()

    if result == None:
        print_info(data, "infactível")
        return None

    produto_periodo = ["produto", "periodo"]
    ingrediente_produto_periodo = ["ingrediente"] + produto_periodo
    ingrediente_periodo = ["ingrediente", "periodo"]
    end_products = get_value_df(
        mdl, f1.end_products, value_name="end_products", key_columns=produto_periodo
    )
    setup_end_products = get_value_df(
        mdl,
        f1.setup_end_products,
        value_name="setup_end_products",
        key_columns=produto_periodo,
    )
    inventory_end_products = get_value_df(
        mdl,
        f1.inventory_end_products,
        value_name="inventory_end_products",
        key_columns=produto_periodo,
    )
    ingredient_proportion = get_value_df(
        mdl,
        f1.ingredient_proportion,
        value_name="ingredient_proportion",
        key_columns=ingrediente_produto_periodo,
    )
    ingredients = get_value_df(
        mdl, f1.ingredients, value_name="ingredients", key_columns=ingrediente_periodo
    )
    setup_ingredients = get_value_df(
        mdl,
        f1.setup_ingredients,
        value_name="setup_ingredients",
        key_columns=ingrediente_periodo,
    )
    inventory_ingredients = get_value_df(
        mdl,
        f1.inventory_ingredients,
        value_name="inventory_ingredients",
        key_columns=ingrediente_periodo,
    )
    var_results = pd.concat(
        (
            end_products,
            setup_end_products,
            inventory_end_products,
            ingredient_proportion,
            ingredients,
            setup_ingredients,
            inventory_ingredients,
        )
    )
    var_results["amount_of_end_products"] = data.amount_of_end_products
    var_results["instance"] = data.instance
    var_results["capacity_multiplier"] = data.capacity_multiplier

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
    df_results_optimized.to_excel(
        f"{complete_path_to_save}.xlsx", index=False, engine="openpyxl"
    )

    print_info(data, "concluído")
    gc.collect()
    return var_results


def running_all_instance_with_chosen_capacity(
    Formulacao: FormulacaoType, path_to_save: str
):
    final_results = []

    if not MPI_BOOL:
        with Pool() as executor:
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

    pd.concat(final_results[0]).to_excel(
        Path(Path(constants.FINAL_PATH) / Path("variaveis.xlsx")), engine="openpyxl"
    )

    get_and_save_results(
        path_to_read=constants.OTIMIZADOS_INDIVIDUAIS_PATH,
        path_to_save=str(Path.resolve(Path(constants.FINAL_PATH) / Path(path_to_save))),
    )
    print(f"Concluído")
