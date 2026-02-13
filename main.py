import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import src.expense_manager as em
import src.transaction as tr
import utils.validators as val


def main():
    # cat_data = val.get_category_data()
    # food = em.Category(*cat_data)

    # print(food.name)
    # print(food.budget)

    # food.budget = 100
    # print(food.budget)

    tr_data = val.get_transaction_data()
    t1 = tr.Transaction(*tr_data)

    print(t1.amount)
    print(t1.category)
    print(t1.description)
    print(t1.date)
    print(t1.type)





if __name__ == "__main__":
    main()
