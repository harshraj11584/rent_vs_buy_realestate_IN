import numpy as np
import pandas as pd
import numpy_financial as npf
from datetime import datetime
import amortization


class BuyOrRentModel:
    def __init__(self,
                 house_cost_price, house_downpayment_percent, home_loan_interest_rate, home_loan_tenure_years,
                 house_rental_start_period, house_rental_amount_today, house_sale_tenure_years,
                 house_appreciation_percent,
                 rent_monthly_cost, rent_yearly_appreciation, rent_savings_growth_percent):

        self.HOUSE_COST_PRICE = house_cost_price
        self.HOUSE_DOWNPAYMENT_PERCENT = house_downpayment_percent
        self.HOUSE_LOAN_INTEREST_RATE = home_loan_interest_rate
        self.HOUSE_LOAN_TENURE_YEARS = home_loan_tenure_years
        self.HOUSE_RENTAL_START_PERIOD = house_rental_start_period
        self.HOUSE_RENTAL_AMOUNT_AT_START = house_rental_amount_today
        self.HOUSE_SALE_TENURE_YEARS = house_sale_tenure_years
        self.HOUSE_APPRECIATION_PERCENT = house_appreciation_percent

        self.RENT_MONTHLY_COST = rent_monthly_cost
        self.RENT_YEARLY_APPRECIATION = rent_yearly_appreciation
        self.RENT_SAVINGS_GROWTH_PERCENT = rent_savings_growth_percent

        self.buying_cashflow = pd.DataFrame(data=None, columns=['Period', 'Payment', 'Comment'])
        self.renting_cashflow = pd.DataFrame(data=None, columns=['Period', 'Payment', 'Comment'])

    def get_house_purchase_cashflows(self):
        this_cashflow = list()

        # downpayment
        this_cashflow.append({'Period': 0,
                              'Payment': -1 * self.HOUSE_DOWNPAYMENT_PERCENT * self.HOUSE_COST_PRICE,
                              'Comment': 'Downpayment'})

        # loan emi paid
        period_index = np.arange(self.HOUSE_LOAN_TENURE_YEARS * 12) + 1
        loan_principal = (1 - self.HOUSE_DOWNPAYMENT_PERCENT) * self.HOUSE_COST_PRICE
        interest_monthly = npf.ipmt(rate=self.HOUSE_LOAN_INTEREST_RATE/12, per=period_index,
                                    nper=self.HOUSE_LOAN_TENURE_YEARS * 12, pv=loan_principal)
        principal_monthly = npf.ppmt(rate=self.HOUSE_LOAN_INTEREST_RATE/12, per=period_index,
                                     nper=self.HOUSE_LOAN_TENURE_YEARS * 12, pv=loan_principal)
        monthly_payments = np.add(principal_monthly, interest_monthly)

        period_index_until_emi_paid = min(self.HOUSE_SALE_TENURE_YEARS * 12, self.HOUSE_LOAN_TENURE_YEARS * 12)
        remaining_loan_balance = loan_principal - np.sum(principal_monthly[:period_index_until_emi_paid]) if (
                period_index_until_emi_paid <= self.HOUSE_LOAN_TENURE_YEARS * 12) else 0

        for i in range(period_index_until_emi_paid):
            this_cashflow.append({'Period': period_index[i],
                                  'Payment': monthly_payments[i],
                                  'Comment': 'EMI'})

        # sale
        selling_price = self.HOUSE_COST_PRICE * pow(1 + self.HOUSE_APPRECIATION_PERCENT, self.HOUSE_SALE_TENURE_YEARS)
        this_cashflow.append({'Period': period_index_until_emi_paid + 1,
                              'Payment': -1 * remaining_loan_balance,
                              'Comment': 'Remaining Loan Balance'})
        this_cashflow.append({'Period': period_index_until_emi_paid + 1,
                              'Payment': selling_price,
                              'Comment': 'Sale Proceeds'})
        selling_profit = selling_price - remaining_loan_balance

        # rent
        future_value_rent = 0
        rental_period_index = np.arange(self.HOUSE_RENTAL_START_PERIOD, self.HOUSE_SALE_TENURE_YEARS*12)
        for index in rental_period_index:
            year_index = (index // 12) + 1
            rent = self.HOUSE_RENTAL_AMOUNT_AT_START * (1+self.RENT_YEARLY_APPRECIATION)**(year_index-1)
            this_cashflow.append({'Period': index, 'Payment': rent, 'Comment': 'Rent Proceeds'})
            years_compounding = (self.HOUSE_SALE_TENURE_YEARS * 12 - index - 1) / 12
            future_value_rent += rent * ((1 + self.RENT_SAVINGS_GROWTH_PERCENT) ** years_compounding)

        future_value = future_value_rent + selling_profit
        return future_value, pd.DataFrame(this_cashflow)

    def get_house_rent_cashflows(self):
        this_cashflow = []
        future_value = 0

        future_value += self.HOUSE_DOWNPAYMENT_PERCENT*self.HOUSE_COST_PRICE*(
                        (1+self.RENT_SAVINGS_GROWTH_PERCENT)**self.HOUSE_SALE_TENURE_YEARS)
        emi_on_buying = (npf.ipmt(rate=self.HOUSE_LOAN_INTEREST_RATE/12,
                                  per=np.arange(self.HOUSE_LOAN_TENURE_YEARS * 12) + 1,
                                  nper=self.HOUSE_LOAN_TENURE_YEARS * 12,
                                  pv=(1 - self.HOUSE_DOWNPAYMENT_PERCENT) * self.HOUSE_COST_PRICE) +
                         npf.ppmt(rate=self.HOUSE_LOAN_INTEREST_RATE/12,
                                  per=np.arange(self.HOUSE_LOAN_TENURE_YEARS * 12) + 1,
                                  nper=self.HOUSE_LOAN_TENURE_YEARS * 12,
                                  pv=(1 - self.HOUSE_DOWNPAYMENT_PERCENT) * self.HOUSE_COST_PRICE))[0]

        rental_period_index = np.arange(self.HOUSE_SALE_TENURE_YEARS * 12) + 1
        for index in rental_period_index:
            year_index = (index // 12) + 1
            rent_given = self.RENT_MONTHLY_COST*(1+self.RENT_YEARLY_APPRECIATION)**(year_index-1)
            rent_earned = self.HOUSE_RENTAL_AMOUNT_AT_START *(1+self.RENT_YEARLY_APPRECIATION)**(year_index-1)
            this_savings = -emi_on_buying - rent_earned
            years_compounding = (self.HOUSE_SALE_TENURE_YEARS*12-index-1)/12
            future_value += this_savings*((1+self.RENT_SAVINGS_GROWTH_PERCENT)**years_compounding)
            this_cashflow.append({'Period': index, 'Savings': this_savings, 'Comment': 'Savings (Not given in EMI)'})

        return future_value, pd.DataFrame(this_cashflow)