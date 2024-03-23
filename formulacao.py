from docplex.mp.model import Model

from data import Data, DataMultipleProducts, MockData


class Formulacao1:
    def __init__(self, data: Data):
        self.data = data
        self.model = Model()
        self.build_variables()

        self.balance_inventory_end_products_constraint()
        self.setup_end_products_constraint()
        self.capacity_end_products_constraint()
        self.balance_inventory_ingredients_constraint()
        self.setup_ingredients_constraint()
        self.upper_ingredients_constraint()
        self.lower_ingredients_constraint()
        self.total_proportion_end_products_constraint()

        self.model.add_kpi(
            self.setup_cost_end_products(), publish_name="setup_cost_end_products"
        )
        self.model.add_kpi(
            self.production_cost_end_products(),
            publish_name="production_cost_end_products",
        )
        self.model.add_kpi(
            self.holding_cost_end_products(), publish_name="holding_cost_end_products"
        )
        self.model.add_kpi(self.end_products_cost(), publish_name="end_products_cost")

        self.model.add_kpi(
            self.setup_cost_ingredients(), publish_name="setup_cost_ingredients"
        )
        self.model.add_kpi(
            self.production_cost_ingredients(),
            publish_name="production_cost_ingredients",
        )
        self.model.add_kpi(
            self.holding_cost_end_ingredients(),
            publish_name="holding_cost_end_ingredients",
        )
        self.model.add_kpi(self.ingredients_cost(), publish_name="ingredients_cost")

        self.model.minimize(self.end_products_cost() + self.ingredients_cost())

    def build_variables(self):
        self._build_end_products_var()
        self._build_setup_end_products_var()
        self._build_inventory_end_products_var()
        self._build_ingredient_proportion_var()
        self._build_ingredients_var()
        self._build_setup_ingredients_var()
        self._build_inventory_ingredients_var()

    def _build_end_products_var(self):
        self.end_products = self.model.continuous_var_matrix(
            self.data.END_PRODUCTS.shape[0],
            self.data.PERIODS.shape[0],
            name="xE",
        )

    def _build_setup_end_products_var(self):
        self.setup_end_products = self.model.binary_var_matrix(
            self.data.END_PRODUCTS.shape[0],
            self.data.PERIODS.shape[0],
            name="yE",
        )

    def _build_inventory_end_products_var(self):
        self.inventory_end_products = self.model.continuous_var_matrix(
            self.data.END_PRODUCTS.shape[0],
            self.data.PERIODS.shape[0],
            name="sE",
        )

    def _build_ingredient_proportion_var(self):
        self.ingredient_proportion = self.model.continuous_var_cube(
            self.data.INGREDIENTS.shape[0],
            self.data.END_PRODUCTS.shape[0],
            self.data.PERIODS.shape[0],
            name="p",
        )

    def _build_ingredients_var(self):
        self.ingredients = self.model.continuous_var_matrix(
            self.data.INGREDIENTS.shape[0],
            self.data.PERIODS.shape[0],
            name="x",
        )

    def _build_setup_ingredients_var(self):
        self.setup_ingredients = self.model.binary_var_matrix(
            self.data.INGREDIENTS.shape[0],
            self.data.PERIODS.shape[0],
            name="y",
        )

    def _build_inventory_ingredients_var(self):
        self.inventory_ingredients = self.model.continuous_var_matrix(
            self.data.INGREDIENTS.shape[0],
            self.data.PERIODS.shape[0],
            name="s",
        )

    def balance_inventory_end_products_constraint(self):
        self.model.add_constraints(
            self.end_products[k, 0]
            == self.data.demand_end[k, 0] + self.inventory_end_products[k, 0]
            for k in self.data.END_PRODUCTS
        )

        self.model.add_constraints(
            self.inventory_end_products[k, t - 1] + self.end_products[k, t]
            == self.data.demand_end[k, t] + self.inventory_end_products[k, t]
            for k in self.data.END_PRODUCTS
            for t in self.data.PERIODS[self.data.PERIODS > 0]
        )

    def setup_end_products_constraint(self):
        self.model.add_constraints(
            self.end_products[k, t]
            <= self.data.sum_demand_end[k, t, 0] * self.setup_end_products[k, t]
            for k in self.data.END_PRODUCTS
            for t in self.data.PERIODS
        )

    def capacity_end_products_constraint(self):
        self.model.add_constraints(
            self.data.setup_time_end[k] * self.setup_end_products[k, t]
            + self.data.production_time_end[k] * self.end_products[k, t]
            <= self.data.capacity_end[k]
            for k in self.data.END_PRODUCTS
            for t in self.data.PERIODS
        )

    def balance_inventory_ingredients_constraint(self):
        self.model.add_constraints(
            self.ingredients[i, 0]
            == self.model.sum(
                self.ingredient_proportion[i, k, 0] for k in self.data.END_PRODUCTS
            )
            + self.inventory_ingredients[i, 0]
            for i in self.data.INGREDIENTS
        )

        self.model.add_constraints(
            self.inventory_ingredients[i, t - 1] + self.ingredients[i, t]
            == self.model.sum(
                self.ingredient_proportion[i, k, t] for k in self.data.END_PRODUCTS
            )
            + self.inventory_ingredients[i, t]
            for i in self.data.INGREDIENTS
            for t in self.data.PERIODS[self.data.PERIODS > 0]
        )

    def setup_ingredients_constraint(self):
        self.model.add_constraints(
            self.ingredients[i, t]
            <= self.model.sum(self.data.ub[i, k] for k in self.data.END_PRODUCTS)
            * self.model.sum(
                self.data.sum_demand_end[k, t, 0] for k in self.data.END_PRODUCTS
            )
            * self.setup_ingredients[i, t]
            for i in self.data.INGREDIENTS
            for t in self.data.PERIODS
        )

    def upper_ingredients_constraint(self):
        self.model.add_constraints(
            self.ingredient_proportion[i, k, t]
            <= self.data.ub[i, k] * self.end_products[k, t]
            for k in self.data.END_PRODUCTS
            for i in self.data.INGREDIENTS
            for t in self.data.PERIODS
        )

    def lower_ingredients_constraint(self):
        self.model.add_constraints(
            self.ingredient_proportion[i, k, t]
            >= self.data.lb[i, k] * self.end_products[k, t]
            for k in self.data.END_PRODUCTS
            for i in self.data.INGREDIENTS
            for t in self.data.PERIODS
        )

    def total_proportion_end_products_constraint(self):
        self.model.add_constraints(
            self.model.sum(
                self.ingredient_proportion[i, k, t] for i in self.data.INGREDIENTS
            )
            == self.end_products[k, t]
            for k in self.data.END_PRODUCTS
            for t in self.data.PERIODS
        )

    def setup_cost_end_products(self):
        return self.model.sum(
            self.data.setup_cost_end[k] * self.setup_end_products[k, t]
            for k in self.data.END_PRODUCTS
            for t in self.data.PERIODS
        )

    def production_cost_end_products(self):
        return self.model.sum(
            self.data.production_cost_end[k] * self.end_products[k, t]
            for k in self.data.END_PRODUCTS
            for t in self.data.PERIODS
        )

    def holding_cost_end_products(self):
        return self.model.sum(
            self.data.holding_cost_end[k] * self.inventory_end_products[k, t]
            for k in self.data.END_PRODUCTS
            for t in self.data.PERIODS
        )

    def end_products_cost(self):
        return (
            self.setup_cost_end_products()
            + self.production_cost_end_products()
            + self.holding_cost_end_products()
        )

    def setup_cost_ingredients(self):
        return self.model.sum(
            self.data.setup_cost_ingredient[i] * self.setup_ingredients[i, t]
            for i in self.data.INGREDIENTS
            for t in self.data.PERIODS
        )

    def production_cost_ingredients(self):
        return self.model.sum(
            self.data.production_cost_ingredient[i] * self.ingredients[i, t]
            for i in self.data.INGREDIENTS
            for t in self.data.PERIODS
        )

    def holding_cost_end_ingredients(self):
        return self.model.sum(
            self.data.holding_cost_ingredient[i] * self.inventory_ingredients[i, t]
            for i in self.data.INGREDIENTS
            for t in self.data.PERIODS
        )

    def ingredients_cost(self):
        return (
            self.setup_cost_ingredients()
            + self.production_cost_ingredients()
            + self.holding_cost_end_ingredients()
        )


if __name__ == "__main__":
    data = DataMultipleProducts("10LLL5.DAT.dat", capacity_multiplier="L")
    f1 = Formulacao1(data)
    print(f1.model.export_as_lp_string())
    f1.model.set_time_limit(10)
    solution = f1.model.solve()
    f1.model.print_solution()
