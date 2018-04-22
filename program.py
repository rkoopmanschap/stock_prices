import pandas as pd
import os.path

class StockReport:
	def __init__(self, available_stocks):
		self.stocks = available_stocks
		self.owned_stocks = []
		self.cached_invested_money = None
		self.cached_stocks_with_positive_reversed_position_scaled = None
		self.cached_owned_stocks_with_negative_reversed_position_scaled = None

		for stock in available_stocks:
			if(stock.owned > 0):
				self.owned_stocks.append(stock)

	def owning_stocks(self):
		if(len(self.owned_stocks) > 0):
			return True
		else:
			return False

	def print_stock_report(self):
		print("========= STOCK REPORT =========")
		print("---------- POSITIVE STOCKS ------------")
		for stock in self.stocks_with_positive_reversed_position_scaled():
			stock.print_stock()
		print("----------------------------")

		print("---------- NEGATIVE STOCKS ------------")
		for stock in self.owned_stocks_with_negative_reversed_position_scaled():
			stock.print_stock()
		print("----------------------------")

		print("---------- OWNED STOCKS ------------")
		for stock in self.owned_stocks:
			stock.print_stock()
		print("----------------------------")
		print("========================")

	def invested_money(self):
		if(self.cached_invested_money):
			return self.cached_invested_money

		result = 0
		for stock in self.owned_stocks:
			result += self.invested_money

		self.cached_invested_money = result
		return self.cached_invested_money

	def owned_stocks_with_negative_reversed_position_scaled(self):
		if(self.cached_owned_stocks_with_negative_reversed_position_scaled):
			return self.cached_owned_stocks_with_negative_reversed_position_scaled

		result = []

		for stock in self.owned_stocks:
			if(stock.reversed_position_scaled() <= 0):
				result.append(stock)

		result.sort(key=lambda stock: stock.reversed_position_scaled())

		self.cached_owned_stocks_with_negative_reversed_position_scaled = result
		return self.cached_owned_stocks_with_negative_reversed_position_scaled

	def stocks_with_positive_reversed_position_scaled(self):
		if(self.cached_stocks_with_positive_reversed_position_scaled):
			return self.cached_stocks_with_positive_reversed_position_scaled

		result = []

		for stock in self.stocks:
			if(stock.reversed_position_scaled() > 0):
				result.append(stock)

		result.sort(key=lambda stock: stock.reversed_position_scaled(), reverse=True)
		self.cached_stocks_with_positive_reversed_position_scaled = result
		return self.cached_stocks_with_positive_reversed_position_scaled

	def longest_data_available(self):
		max_historic_data = 0
		for stock in self.stocks:
			if(stock.amount_of_historic_data > max_historic_data):
				max_historic_data = stock.amount_of_historic_data

		return max_historic_data

	def cheapest_stock(self):
		cheapest_price = 9999
		cheapest_stock = None
		for stock in self.stocks:
			if(stock.current_price < cheapest_price):
				cheapest_stock = stock
				cheapest_price = stock.current_price

		return cheapest_stock

class BuyLowSellHighAi:
	def __init__(self, spendable_money, stock_report):
		self.spendable_money = spendable_money
		self.stock_report = stock_report
		self.choices = []

	def buy(self, stock):
		max_buyable = self.spendable_money // stock.current_price
		self.spendable_money -= max_buyable * stock.current_price
		if(max_buyable > 0):
			self.choices.append((stock.name, "BUY", int(max_buyable)))

	def sell(self, stock):
		max_sellable = stock.owned

		self.choices.append((stock.name, "SELL", max_sellable))

	def make_choices(self):
		longest_data_available = stock_report.longest_data_available()

		if(longest_data_available < 15):
			self.buy(self.stock_report.cheapest_stock())
			if(longest_data_available % 10 == 0):
				for stock in self.stock_report.owned_stocks:
					self.sell(stock)
		else:
			for stock in stock_report.owned_stocks_with_negative_reversed_position_scaled():
				self.sell(stock)

			for stock in stock_report.stocks_with_positive_reversed_position_scaled():
				self.buy(stock)

		return self.choices

class StockBroker:
	def __init__(self, spendable_money, stock_report):
		self.spendable_money = spendable_money
		self.stock_broker_ai = BuyLowSellHighAi(spendable_money, stock_report)

	def make_decisions(self):
		# stock_report.print_stock_report()
		choices = self.stock_broker_ai.make_choices()
		self.process_choices(choices)

	def process_choices(self, choices):
		print(len(choices))
		for choice in choices:
			print(choice[0], choice[1], choice[2], sep=' ')

class Stock:
	def __init__(self, name, owned, latest_prices, min_price, max_price):
		self.latest_prices = latest_prices
		self.amount_of_historic_data = len(latest_prices)
		self.name = name
		self.min = min_price
		self.max = max_price
		self.current_price = latest_prices[-1]
		self.owned = owned
		self.cached_reversed_position_scaled = None

	# calculate the position of the stock: ie:
	# Min ---Current-------------- Max
	# is better than:
	# Min --------------Current--- Max
	# Uses historic data
	# final answer is divided by the current price, so cheap stocks are better than expensive ones because you can buy more of them
	def calculate_reversed_position_scaled(self):
		distance_to_max = self.max - self.current_price
		distance_to_min = self.current_price - self.min
		reversed_position = (distance_to_max - distance_to_min)
		reversed_position_scaled = reversed_position / self.current_price
		return reversed_position_scaled

	def reversed_position_scaled(self):
		if(not(self.cached_reversed_position_scaled)):
			self.cached_reversed_position_scaled = self.calculate_reversed_position_scaled()
		return self.cached_reversed_position_scaled

	def print_stock(self):
		print("======== STOCK ========")
		print("name: ", self.name)
		print("owned: ", self.owned)
		print("reversed_position_scaled", self.reversed_position_scaled())
		print("min: ", self.min)
		print("max: ", self.max)
		print("current_price: ", self.current_price)
		print("latest_prices: ", self.latest_prices)
		print("======================")

	def invested_money(self):
		return self.current_price * self.owned

	def trend(self):
		return latest_prices[-1] - latest_prices[-4]

def process_input(historic_data):
	input_report = {}

	input_data = input().strip().split(" ")
	input_report['spendable_money'] = float(input_data[0])
	input_report['number_of_stocks'] = int(input_data[1])
	input_report['days_remaining'] = int(input_data[2])
	input_report['available_stocks'] = []

	for _ in range(input_report['number_of_stocks']):
		input_stock = input().strip().split(" ")
		name = input_stock[0]
		owned = int(input_stock[1])
		latest_values = [float(value) for value in input_stock[2:]]

		if(name in historic_data['data']):
			latest_values = list(historic_data['data'][name]) + [latest_values[-1]]

		stock = Stock(name, owned, latest_values, min(latest_values), max(latest_values))
		input_report['available_stocks'].append(stock)

	return input_report	

def read_historic_data():
	if(os.path.exists('data.csv')):
		data = pd.read_csv('data.csv')

		return { 'data': data }
	else:
		return { 'data': [] }

def write_historic_data(available_stocks):
	stock_dict = {}
	max_length = 0
	for stock in available_stocks:
		stock_dict[stock.name] = stock.latest_prices
		current_length = len(stock.latest_prices)
		if(current_length > max_length):
			max_length = current_length

	keys_to_update = []
	for key, value in stock_dict.items():
		if(len(value) != max_length):
			keys_to_update.append(key)
			
	for key in keys_to_update:
		stock_dict[key] = [0] * (max_length - len(stock_dict[key])) + stock_dict[key]

	# print("stock_dict = ", stock_dict)
	data = pd.DataFrame(data=stock_dict)
	# print("data = ", stock_dict)
	data.to_csv("data.csv")

historic_data = read_historic_data()
input_report = process_input(historic_data)
write_historic_data(input_report["available_stocks"])
stock_report = StockReport(input_report['available_stocks'])
stock_broker = StockBroker(input_report['spendable_money'], stock_report)
stock_broker.make_decisions()

