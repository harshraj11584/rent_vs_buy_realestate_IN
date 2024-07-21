from calculator import BuyOrRentModel

model = BuyOrRentModel(house_cost_price=10000000,
                       house_downpayment_percent=0.2,
                       home_loan_interest_rate=0.085,
                       home_loan_tenure_years=20,
                       house_rental_start_period=30,
                       house_rental_amount_today=45000,
                       house_sale_tenure_years=8,
                       house_appreciation_percent=0.05,
                       rent_monthly_cost=40000,
                       rent_yearly_appreciation=0.03,
                       rent_savings_growth_percent=0.15)
future_value_buying, buying_cashflows = model.get_house_purchase_cashflows()
future_value_renting, renting_cashflows = model.get_house_rent_cashflows()
print("Buying\n", buying_cashflows.to_markdown())
print("Renting\n", renting_cashflows.to_markdown())
print("Buy FV", future_value_buying, "Rent FV", future_value_renting)
