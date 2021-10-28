from django.utils import timezone
from django.shortcuts import render
from django.views.generic import DetailView

import datetime, requests, math

from .models import Currency, CurrencyStat
from .forms import DateFromToForm, ExchangeForm


class IndexView(DetailView):
    template_name = 'stock/index.html'

    def add_stats(self, currency_data):
        p_currency, created = Currency.objects.get_or_create(currency_code=currency_data['currency_code'], defaults={'currency_name': currency_data['currency_name']})

        f_date = datetime.datetime.strptime(currency_data['effective_date'], "%Y-%m-%d")
        p_effective_date = timezone.make_aware(f_date, timezone.get_current_timezone())

        p_value_mid = currency_data['value_mid']
        p_value_bid = currency_data['value_bid']
        p_value_ask = currency_data['value_ask']

        p_currency = Currency.objects.get(currency_code=currency_data['currency_code'])

        currencyStats, created = CurrencyStat.objects.get_or_create(currency=p_currency,
        effective_date=p_effective_date, value_mid=p_value_mid, value_bid=p_value_bid, value_ask=p_value_ask)

    def get_data(self):
        effective_date = CurrencyStat.objects.all().last().effective_date.strftime('%Y-%m-%d')
        effective_date = datetime.datetime.strptime(effective_date, "%Y-%m-%d").date()

        end_date = datetime.date.today()

        stock_data = {}
        currency_data = {}

        while effective_date < end_date:
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

    def get(self, request):
        context = {}

        form_exchange = ExchangeForm()
        context['form_exchange'] = form_exchange

        return render(request, 'stock/index.html', context)

    def post(self, request):
        context = {}

        ask_amount = float(request.POST['amount'])

        currency_ask = request.POST['currency_ask']
        code_ask = Currency.objects.get(id=currency_ask).currency_code

        if code_ask != 'PLN':
            url_ask = f"https://api.nbp.pl/api/exchangerates/rates/c/{code_ask}/last?format=JSON"
            date_ask = requests.get(url_ask).json()['rates'][0]['effectiveDate']
            rate_ask = float(requests.get(url_ask).json()['rates'][0]['ask'])
        else:
            rate_ask = float(1)

        currency_bid = request.POST['currency_bid']
        code_bid = Currency.objects.get(id=currency_bid).currency_code

        if code_bid != 'PLN':
            url_bid = f"https://api.nbp.pl/api/exchangerates/rates/c/{code_bid}/last?format=JSON"
            date_bid = requests.get(url_bid).json()['rates'][0]['effectiveDate']
            rate_bid = float(requests.get(url_bid).json()['rates'][0]['bid'])
        else:
            rate_bid = float(1)

        bid_amount = ask_amount * rate_ask / rate_bid

        bid_amount = math.floor(bid_amount * 100)/100.0

        context['cur_ask'] = code_ask
        context['cur_bid'] = code_bid
        context['ask_amount'] = ask_amount
        context['bid_amount'] = bid_amount

        form_exchange = ExchangeForm()
        context['form_exchange'] = form_exchange

        return render(request, 'stock/index.html', context)


class AboutView(DetailView):
    template_name = 'stock/about.html'

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
        start_date = request.POST['date_from']
        end_date = request.POST['date_to']

        context = self.set_data(date_from=start_date, date_to=end_date)

        form_calendar = DateFromToForm()
        context['form_calendar'] = form_calendar

        return render(request, 'stock/about.html', context)
