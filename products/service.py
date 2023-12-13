import math
from functools import reduce

import numpy as np
from scipy.optimize import minimize

nutrients_energy = dict({
    'fats': 9,
    'proteins': 4,
    'carbohydrates': 4,
})


def get_constraint_fun(name, constr_type, kkal_amount, energy_restrictions):
    def min_constraint(x: list, products):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get(name)
        return sum_energy*nutrients_energy.get(name) - kkal_amount*energy_restrictions.get(name)[0]

    def max_constraint(x: list, products):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get(name)
        return kkal_amount*energy_restrictions.get(name)[1] - sum_energy*nutrients_energy.get(name)
    return min_constraint if constr_type == 'min' else max_constraint


def optimize_products_bucket(products, constr, max_sum, kkal_per_day, energy_restrictions, days = 1):
    kkal_amount = kkal_per_day*days

    def objective(x: list):
        pr = products
        sum_prices = 0
        for index, xi in enumerate(x):
            sum_prices = sum_prices + xi*pr[index].get('price')
        return sum_prices

    def price_constraint(x: list, pr):
        sum_prices = 0
        for index, xi in enumerate(x):
            sum_prices = sum_prices + xi*pr[index].get('price')
        return max_sum - sum_prices

    def energy_constraint(x: list, pr):
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get('energy')
        return sum_energy - kkal_amount

    def get_init_guess(x):
        guess_list = list()
        for index, xi in enumerate(x):
            guess_list.append(1)
        return guess_list

    def get_bounds():
        pr = products
        bounds = list()
        for index, xi in enumerate(pr):
            equal_bound = [restriction for restriction in xi.get('restrictions') if restriction.get('comparator') == 'EQ']
            if len(equal_bound):
                bounds.append((equal_bound[0].get('amount')*days, equal_bound[0].get('amount')*days))
                continue
            min_restriction = [restriction for restriction in xi.get('restrictions') if restriction.get('comparator') == 'GT']
            max_restriction = [restriction for restriction in xi.get('restrictions') if restriction.get('comparator') == 'LT']
            min_bound = min_restriction[0].get('amount') if len(min_restriction) else 0
            max_bound = max_restriction[0].get('amount') if len(max_restriction) else 200

            bound = (min_bound*days, max_bound*days)
            bounds.append(bound)
        return bounds

    con1 = {'type': 'ineq', 'fun': price_constraint, 'args': [products]}
    con2 = {'type': 'eq', 'fun': energy_constraint, 'args': [products]}
    con3 = {'type': 'ineq', 'fun': get_constraint_fun('carbohydrates', 'min', kkal_amount, energy_restrictions), 'args': [products]}
    con4 = {'type': 'ineq', 'fun': get_constraint_fun('carbohydrates', 'max', kkal_amount, energy_restrictions), 'args': [products]}
    con5 = {'type': 'ineq', 'fun': get_constraint_fun('fats', 'min', kkal_amount, energy_restrictions), 'args': [products]}
    con6 = {'type': 'ineq', 'fun': get_constraint_fun('fats', 'max', kkal_amount, energy_restrictions), 'args': [products]}
    con7 = {'type': 'ineq', 'fun': get_constraint_fun('proteins', 'min', kkal_amount, energy_restrictions), 'args': [products]}
    con8 = {'type': 'ineq', 'fun': get_constraint_fun('proteins', 'max', kkal_amount, energy_restrictions), 'args': [products]}

    constr = [con1, con2, con3, con4, con5, con6, con7, con8]
    bounds = get_bounds()
    print('bounds', bounds)
    sol = minimize(objective, get_init_guess(products), method='SLSQP', bounds=bounds, constraints=constr)
    amounts = sol.x

    res = list()
    general = {
        'energy': 0,
        'price': 0,
        'carbohydrates': 0,
        'proteins': 0,
        'fats': 0,
    }
    for index, product in enumerate(products):
        general['energy'] = general['energy'] + amounts[index] * product.get('energy')
        general['price'] = general['price'] + amounts[index] * product.get('price')
        general['carbohydrates'] = general['carbohydrates'] + amounts[index] * product.get('carbohydrates')
        general['proteins'] = general['proteins'] + amounts[index] * product.get('proteins')
        general['fats'] = general['fats'] + amounts[index] * product.get('fats')

        if round(amounts[index], 4) != 0:
            product_res = {
                'id': product.get('id'),
                'name': product.get('name'),
                'amount': round(amounts[index]),
                'unit': product.get('unit') if product.get('unit') == 'шт' else 'гр',
                'price': round(amounts[index] * product.get('price'), 2),
                'states': [{
                    'state': product.get('state'),
                    'energy': round(amounts[index] * product.get('energy'), 2),
                    'carbohydrates': round(amounts[index] * product.get('carbohydrates'), 2),
                    'proteins': round(amounts[index] * product.get('proteins'), 2),
                    'fats': round(amounts[index] * product.get('fats'), 2),
                }]
            }
            res.append(product_res)
    return {'product_bucket': res, 'general': general}
