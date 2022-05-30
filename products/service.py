import math
from functools import reduce

import numpy as np
from scipy.optimize import minimize


def optimize_products_bucket(products, constr, max_sum, kkal_per_day):

    def objective(x: list):
        pr = products
        sum_prices = 0
        for index, xi in enumerate(x):
            sum_prices = sum_prices + xi*pr[index].get('price')
        return sum_prices

    def constraint1(x: list):
        pr = products
        sum_prices = 0
        for index, xi in enumerate(x):
            sum_prices = sum_prices + xi*pr[index].get('price')
        return max_sum - sum_prices

    def constraint2(x: list):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get('energy')
        return sum_energy - kkal_per_day

    def constraint3(x: list):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get('carbohydrates')
        return sum_energy*4 - kkal_per_day*0.55

    def constraint4(x: list):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get('carbohydrates')
        return kkal_per_day*0.6 - sum_energy*4


    def constraint5(x: list):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get('proteins')
        return sum_energy*4 - kkal_per_day*0.15

    def constraint6(x: list):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get('fats')
        return kkal_per_day*0.20 - sum_energy*9

    def constraint7(x: list):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get('fats')
        return sum_energy*9 - kkal_per_day*0.20

    def constraint8(x: list):
        pr = products
        sum_energy = 0
        for index, xi in enumerate(x):
            sum_energy = sum_energy + xi*pr[index].get('proteins')
        return kkal_per_day*0.25 - sum_energy*4


    def get_init_guess(x):
        guess_list = list()
        for index, xi in enumerate(x):
            guess_list.append(1)
        return guess_list

    def get_bounds():
        pr = products
        bounds = list()
        for index, xi in enumerate(pr):
            bound = (0, 200)
            bounds.append(bound)
        return bounds

    con1 = {'type': 'ineq', 'fun': constraint1}
    con2 = {'type': 'eq', 'fun': constraint2}
    con3 = {'type': 'ineq', 'fun': constraint3}
    con4 = {'type': 'ineq', 'fun': constraint4}
    con5 = {'type': 'ineq', 'fun': constraint5}
    con6 = {'type': 'ineq', 'fun': constraint6}
    con7 = {'type': 'ineq', 'fun': constraint7}
    con8 = {'type': 'ineq', 'fun': constraint8}

    constr = [con1, con2, con3, con4, con5, con6, con7, con8]
    bounds = get_bounds()

    sol = minimize(objective, get_init_guess(products), method='SLSQP', bounds=bounds, constraints=constr)
    amounts = sol.x
    sum1 = 0
    sum2 = 0
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
                'unit': product.get('unit'),
                'price': round(amounts[index] * product.get('price'), 4),
                'states': [{
                    'state': product.get('state'),
                    'energy': round(amounts[index] * product.get('energy'), 4),
                    'carbohydrates': round(amounts[index] * product.get('carbohydrates'), 4),
                    'proteins': round(amounts[index] * product.get('proteins'), 4),
                    'fats': round(amounts[index] * product.get('fats'), 4),
                }]
            }
            res.append(product_res)
    return {'product_bucket': res, 'general': general}
