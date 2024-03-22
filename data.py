from abc import ABC, abstractmethod
from typing import Any, Dict

import numpy as np
from numpy import ndarray


class ReadData(ABC):
    @abstractmethod
    def __init__(self, file_to_read: str):
        pass


class Data(ReadData):
    PERIODS: ndarray[Any, int]
    END_PRODUCTS: ndarray[Any, int]
    INGREDIENTS: ndarray[Any, int]
    INGREDIENTS_OF_PRODUCT: Dict[int, int]
    ub: ndarray[(Any, Any), float]
    lb: ndarray[(Any, Any), float]
    demand_end: ndarray[(Any, Any), float]
    sum_demand_end: ndarray[(Any, Any), float]
    holding_cost_end: ndarray[(Any, Any), float]
    setup_cost_end: ndarray[(Any, Any), float]
    production_cost_end: ndarray[(Any, Any), float]
    production_time_end: ndarray[(Any, Any), float]
    setup_time_end: ndarray[(Any, Any), float]
    capacity_end: ndarray[(Any, Any), float]
    holding_cost_ingredient: ndarray[(Any, Any), float]
    setup_cost_ingredient: ndarray[(Any, Any), float]
    production_cost_ingredient: ndarray[(Any, Any), float]
    file_to_read: str

    def __init__(self, file_to_read: str):
        self.file_to_read = file_to_read
        pass


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
                np.array(
                    list(self.demand_end[k][t:].sum() for t in self.PERIODS)
                )
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
    MockData("mock")
