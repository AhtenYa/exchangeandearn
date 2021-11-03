from django.utils import timezone
from django.shortcuts import render
from django.views.generic import DetailView

import datetime, requests, math

from .models import Currency, CurrencyStat
from .forms import DateFromToForm, ExchangeForm


class IndexView(DetailView):
    template_name = 'stock/index.html'

    def exchange(self, exchange_data):
        val_date = {}
        code = exchange_data['code']
        type = exchange_data['type']

        curr = Currency.objects.get(currency_code=code)

        if code != 'PLN':
            url = f"https://api.nbp.pl/api/exchangerates/rates/c/{code}/last?format=JSON"

            try:
                data = requests.get(url).json()['rates'][0]
            except requests.exceptions.RequestException as e:
                data = CurrencyStat.objects.filter(currency=curr).last()
                date = data.effective_date

                date = date.strftime('%Y-%m-%d')
                date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

                rate = data.value_ask
            else:
                date = data['effectiveDate']

                date = datetime.datetime.strptime(date, "%Y-%m-%d")
                date = timezone.make_aware(date, timezone.get_current_timezone())
                date = date.date()

                rate = float(data[type])
        else:
            date = datetime.date.today()
            rate = float(1)

        val_date['rate'] = rate
        val_date['date'] = date

        return val_date

    def get(self, request):
        context = {}

        form_exchange = ExchangeForm()
        context['form_exchange'] = form_exchange

        return render(request, 'stock/index.html', context)

    def post(self, request):
        context = {}

        ask_amount = float(request.POST['ask_amount'])
        ask_amount = math.floor(ask_amount * 100)/100.0

        currency_ask = request.POST['currency_ask']
        currency_bid = request.POST['currency_bid']

        code_ask = Currency.objects.get(id=currency_ask).currency_code
        code_bid = Currency.objects.get(id=currency_bid).currency_code

        exchange_ask = {}
        exchange_bid = {}

        exchange_ask['code'] = code_ask
        exchange_ask['type'] = 'ask'
        exchange_bid['code'] = code_bid
        exchange_bid['type'] = 'bid'

        val_date_ask = self.exchange(exchange_ask)
        val_date_bid = self.exchange(exchange_bid)

        bid_amount = ask_amount * val_date_ask['rate'] / val_date_bid['rate']

        bid_amount = math.floor(bid_amount * 100)/100.0

        context['cur_ask'] = code_ask
        context['cur_bid'] = code_bid
        context['ask_amount'] = ask_amount
        context['bid_amount'] = bid_amount
        context['date_ask'] = val_date_ask['date']
        context['date_bid'] = val_date_bid['date']

        form_exchange = ExchangeForm()
        context['form_exchange'] = form_exchange

        return render(request, 'stock/index.html', context)


class AboutView(DetailView):
    template_name = 'stock/about.html'

    def add_stats(self, currency_data):
        p_currency, created = Currency.objects.get_or_create(currency_code=currency_data['currency_code'], defaults={'currency_name': currency_data['currency_name']})

        f_date = datetime.datetime.strptime(currency_data['effective_date'], "%Y-%m-%d")
        p_effective_date = timezone.make_aware(f_date, timezone.get_current_timezone())

        p_value_mid = currency_data['value_mid']
        p_value_bid = currency_data['value_bid']
        p_value_ask = currency_data['value_ask']

        currencyStats, created = CurrencyStat.objects.get_or_create(currency=p_currency,
        effective_date=p_effective_date, value_mid=p_value_mid, value_bid=p_value_bid, value_ask=p_value_ask)

    def get_data_from_net_to_db(self):
        effective_date = CurrencyStat.objects.all().last().effective_date.strftime('%Y-%m-%d')
        effective_date = datetime.datetime.strptime(effective_date, "%Y-%m-%d").date()

        end_date = datetime.date.today()

        stock_data = {}
        currency_data = {}

        while effective_date <= end_date:
            url_tables = f"https://api.nbp.pl/api/exchangerates/tables/a/{effective_date}?format=json"

            try:
                stock_tables = requests.get(url_tables).json()
            except:
                pass
            else:
                for table in stock_tables:
                    currency_data['effective_date'] = table['effectiveDate']
                    rates = table['rates']
                    print(currency_data['effective_date'])

                    for rate in rates:
                        currency_data['currency_name'] = rate['currency']
                        currency_data['currency_code'] = rate['code']
                        currency_data['value_mid'] = rate['mid']

                        url_rates = f"https://api.nbp.pl/api/exchangerates/rates/c/{currency_data['currency_code']}/{currency_data['effective_date']}?format=json"

                        try:
                            stock_rate = requests.get(url_rates).json()['rates'][0]
                        except:
                            pass
                        else:
                            currency_data['value_bid'] = stock_rate['bid']
                            currency_data['value_ask'] = stock_rate['ask']

                            self.add_stats(currency_data)

            effective_date = effective_date + datetime.timedelta(days=1)

        return stock_data

    def get_data_from_net(self, date_from, date_to):
        stock_data = {}
        currency_data = {}

        url_tables = f"https://api.nbp.pl/api/exchangerates/tables/a/{date_from}/{date_to}?format=json"

        try:
            stock_tables = requests.get(url_tables).json()
        except:
            return {}
        else:
            for table in stock_tables:
                codes = table['rates']

                for rate_code in codes:
                    code = rate_code['code']

                    url_rates = f"https://api.nbp.pl/api/exchangerates/rates/a/{code}/{date_from}/{date_to}?format=json"

                    try:
                        rates = requests.get(url_rates).json()['rates']
                    except:
                        stock_data[code] = {}
                    else:
                        for rate in rates:
                            currency_data[rate['effectiveDate']] = rate['mid']

                    stock_data[code] = currency_data

        return stock_data

    def set_data_from_net(self, date_from, date_to):
        stock = {}

        date_from = date_from.strftime('%Y-%m-%d')
        date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
        date_to = date_to.strftime('%Y-%m-%d')
        date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()

        stock = self.get_data_from_net(date_from, date_to)

        return stock

    def set_data(self, date_from, date_to):
        stock = {}

        currencys = Currency.objects.filter(base_currency=False)
        currencys = currencys.order_by('index')

        for currency in currencys:
            currencyStats = CurrencyStat.objects.filter(currency=currency, effective_date__range=(date_from, date_to))
            currencyStats = currencyStats.order_by('effective_date')
            stock[currency.currency_code] = currencyStats

        data = {'stock': stock, 'currencys': currencys}

        return data

    def get(self, request):
        #self.get_data()

        end_date = timezone.now()
        start_date = end_date - datetime.timedelta(days=93)

        context = self.set_data(date_from=start_date, date_to=end_date)

        form_calendar = DateFromToForm()
        context['form_calendar'] = form_calendar

        return render(request, 'stock/about.html', context)

    def post(self, request):
        context = {}
        start_date = request.POST['date_from']
        end_date = request.POST['date_to']

        form = DateFromToForm(request.POST)

        if form.is_valid():
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            end_date = timezone.make_aware(end_date, timezone.get_current_timezone())

            context = self.set_data(date_from=start_date, date_to=end_date)

        context['form_calendar'] = form

        return render(request, 'stock/about.html', context)
