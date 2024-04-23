from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

import numpy as np
from numpy import ndarray

from constants import *
from read_file import ReadData


class DataAbstractClass(ABC):
    instance: str
    capacity: int
    amount_of_end_products: int

    @abstractmethod
    def __init__(self, file_to_read: str, capacity_multiplier: str) -> None:
        super().__init__()


@dataclass
class Data(DataAbstractClass):
    PERIODS: ndarray
    END_PRODUCTS: ndarray
    INGREDIENTS: ndarray
    INGREDIENTS_OF_PRODUCT: Dict
    ub: ndarray
    lb: ndarray
    demand_end: ndarray
    sum_demand_end: ndarray
    holding_cost_end: ndarray
    setup_cost_end: ndarray
    production_cost_end: ndarray
    production_time_end: ndarray
    setup_time_end: ndarray
    capacity_end: ndarray
    holding_cost_ingredient: ndarray
    setup_cost_ingredient: ndarray
    production_cost_ingredient: ndarray
    file_to_read: str
    instance: str
    capacity: int
    amount_of_end_products: int
    capacity_multiplier: str

    def __str__(self):
        return f"{self.instance}"

    def __init__(self, file_to_read: str, capacity_multiplier="N"):
        df = ReadData(file_to_read).get_df()
        self.file_to_read = file_to_read
        self.instance = self.file_to_read.split(".")[0]

        self.END_PRODUCTS = np.arange(
            DEFAULT_SINGLE_PRODUCTS
        )  # Original instances are single end product
        self.amount_of_end_products = self.END_PRODUCTS.shape[0]
        self.INGREDIENTS = np.arange(int(df.iloc[0, 1]))
        self.PERIODS = np.arange(int(df.iloc[0, 2]))
        inicio = 1
        fim = inicio + 1
        self.capacity_end = (
            np.array(df.iloc[inicio:fim, 0].astype(float), dtype=int)
            * DEFAULT_CAPACITY_MULTIPLIER[capacity_multiplier]
        )
        self.capacity_multiplier = capacity_multiplier
        self.capacity = self.capacity_end[0]
        inicio, fim = fim, fim + self.END_PRODUCTS.shape[0]
        self.production_time_end = np.array(
            df.iloc[inicio:fim, 0].astype(float),
        )
        self.holding_cost_end = np.array(
            df.iloc[inicio:fim, 1].astype(float),
        )
        self.setup_time_end = np.array(
            df.iloc[inicio:fim, 2].astype(float),
        )
        self.setup_cost_end = np.array(
            df.iloc[inicio:fim, 3].astype(float),
        )
        self.production_cost_end = np.array(
            df.iloc[inicio:fim, 4].astype(float),
        )
        inicio, fim = fim, fim + self.INGREDIENTS.shape[0]
        self.holding_cost_ingredient = np.array(
            df.iloc[inicio:fim, 0].astype(float),
        )
        self.setup_cost_ingredient = np.array(
            df.iloc[inicio:fim, 1].astype(float),
        )
        self.production_cost_ingredient = np.array(
            df.iloc[inicio:fim, 2].astype(float),
        )
        inicio, fim = fim, fim + self.PERIODS.shape[0]
        self.demand_end = np.array(df.iloc[inicio:fim, 0].astype(float), dtype=int)
        self.sum_demand_end = np.array(
            list(self.demand_end[t:].sum() for t in self.PERIODS)
        ).reshape(self.END_PRODUCTS.shape[0], self.PERIODS.shape[0], 1)
        self.ub = np.full(
            (self.INGREDIENTS.shape[0], self.END_PRODUCTS.shape[0]),
            1 / self.INGREDIENTS.shape[0],
        )
        self.lb = np.full(
            (self.INGREDIENTS.shape[0], self.END_PRODUCTS.shape[0]),
            1 / self.INGREDIENTS.shape[0],
        )


class DataMultipleProducts(Data):

    def __str__(self):
        return f"{super().__str__()}_prod_{self.END_PRODUCTS.shape[0]}"

    def __init__(
        self, file_to_read: str, capacity_multiplier, amount_of_end_products: int
    ):
        super().__init__(file_to_read, capacity_multiplier)
        self.END_PRODUCTS = np.arange(amount_of_end_products)
        self._update_demand()

    def _update_demand(self):
        self._original_demand_end = self.demand_end
        self.demand_end = np.repeat(
            self._original_demand_end[:, np.newaxis], self.END_PRODUCTS.shape[0], axis=1
        ).T
        self._original_sum_demanda_product = self.sum_demand_end
        sum_demand_product = []
        for k in self.END_PRODUCTS:
            sum_demand_product.append(
                np.array(list(self.demand_end[k][t:].sum() for t in self.PERIODS))
            )
        self.sum_demand_end = np.array(sum_demand_product).reshape(
            self.END_PRODUCTS.shape[0], self.PERIODS.shape[0], 1
        )
        self.amount_of_end_products = self.END_PRODUCTS.shape[0]


class MockData(Data):
    def __init__(self, file_to_read: str):
        super().__init__("mock")
        self.PERIODS = np.arange(2)
        self.END_PRODUCTS = np.arange(2)
        self.INGREDIENTS = np.arange(4)
        self.ub = np.array([[0.3, 0], [0.7, 0], [0.2, 0.5], [0.1, 0.8]])
        self.lb = np.array([[0.3, 0], [0.5, 0], [0.0, 0.2], [0.1, 0.8]])
        self.demand_end = np.array([[1, 1], [1, 1]])
        sum_demand_product = []
        for k in self.END_PRODUCTS:
            sum_demand_product.append(
                np.array(list(self.demand_end[k][t:].sum() for t in self.PERIODS))
            )
        self.sum_demand_end = np.array(sum_demand_product).reshape(
            self.END_PRODUCTS.shape[0], self.PERIODS.shape[0], 1
        )
        self.holding_cost_end = np.full(
            shape=(self.END_PRODUCTS.shape[0], self.PERIODS.shape[0]), fill_value=1
        )
        self.setup_cost_end = np.full(
            shape=(self.END_PRODUCTS.shape[0], self.PERIODS.shape[0]), fill_value=1
        )
        self.production_cost_end = np.full(
            shape=(self.END_PRODUCTS.shape[0], self.PERIODS.shape[0]), fill_value=0
        )
        self.production_time_end = np.full(
            shape=(self.END_PRODUCTS.shape[0], self.PERIODS.shape[0]), fill_value=1
        )
        self.setup_time_end = np.full(
            shape=(self.END_PRODUCTS.shape[0], self.PERIODS.shape[0]), fill_value=1
        )
        self.capacity_end = np.full(
            shape=(self.END_PRODUCTS.shape[0], self.PERIODS.shape[0]), fill_value=10
        )
        self.holding_cost_ingredient = np.full(
            shape=(self.INGREDIENTS.shape[0], self.PERIODS.shape[0]), fill_value=1
        )
        self.setup_cost_ingredient = np.full(
            shape=(self.INGREDIENTS.shape[0], self.PERIODS.shape[0]), fill_value=1
        )
        self.production_cost_ingredient = np.full(
            shape=(self.INGREDIENTS.shape[0], self.PERIODS.shape[0]), fill_value=0
        )


if __name__ == "__main__":
    data = DataMultipleProducts("2HHH1.DAT.dat")
    pass
