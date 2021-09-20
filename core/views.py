from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import pdb

# Create your views here.


def get_html_content(request):
    # web scraping google weather content
    city = request.GET.get('city')
    city = city.replace(" ", "+")
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE

    html_content_weather = session.get(f'https://www.google.com/search?q=weather+{city}').content
    html_content_sunset_time = session.get(f'https://www.google.com/search?q=sunset+{city}').text
    html_content_sunrise_time = session.get(f'https://www.google.com/search?q=sunrise+{city}').text
    return html_content_weather, html_content_sunset_time, html_content_sunrise_time


def get_time_status(sunset_time, sunrise_time, current_time):

    # sunset_time and sunrise_time are received like 6:27 a.m. or 8:16 p.m.
    sunset_time = sunset_time.split(' ')
    sunset_time = sunset_time[0].split(':')
    sunset_time_in_min = (int(sunset_time[0]) * 60) + int(sunset_time[1]) + 720  # 720 min in 12 hours

    sunrise_time = sunrise_time.split(' ')
    sunrise_time = sunrise_time[0].split(':')
    sunrise_time_in_min = (int(sunrise_time[0]) * 60) + int(sunrise_time[1])

    current_time = current_time.split(' ')
    if current_time[2] == "a.m.":
        current_time = current_time[1].split(':')
        current_time_in_min = (int(current_time[0]) * 60) + int(current_time[1])
    else:
        current_time = current_time[1].split(':')
        current_time_in_min = (int(current_time[0]) * 60) + int(current_time[1]) + 720

    # after all the times are converted into minutes, compare to determine if it is night or day
    if (current_time_in_min > sunset_time_in_min) or (current_time_in_min < sunrise_time_in_min):
        time_status = "night"
    else:
        time_status = "day"

    return time_status


def home(request):
    extracted_data = None
    if 'city' in request.GET:
        # html_content is a tuple of size 3
        html_content = get_html_content(request)
        weather_soup = BeautifulSoup(html_content[0], 'html.parser')
        sunset_soup = BeautifulSoup(html_content[1], 'html.parser')
        sunrise_soup = BeautifulSoup(html_content[2], 'html.parser')
        extracted_data = dict()
        extracted_data['region'] = weather_soup.find('span', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
        current_temp_str = weather_soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
        extracted_data['current_temp'] = farenheit_to_celcius(int(current_temp_str[:-2]))
        time_status_str = weather_soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
        time_status_list = time_status_str.splitlines()
        extracted_data['time'] = time_status_list[0].strip()
        extracted_data['status'] = time_status_list[1]

        sunset_time = sunset_soup.find("div", attrs={"class": "MUxGbd t51gnb lyLwlc lEBKkf"})
        if sunset_time == None:  # if the class isn't found, use default sunset time of 6:00 am
            sunset_time = "7:30 p.m."
        else:
            sunset_time = sunset_time.text

        sunrise_time = sunrise_soup.find("div", attrs={"class": "MUxGbd t51gnb lyLwlc lEBKkf"})
        if sunrise_time == None:  # if the class isn't found, use default sunrise time of 6:00 am
            sunrise_time = "6:00 a.m."
        else:
            sunrise_time = sunrise_time.text

        extracted_data['time_status'] = get_time_status(sunset_time, sunrise_time, extracted_data['time'])
        pass

    return render(request, 'core/home.html', {'extracted_data': extracted_data})

def farenheit_to_celcius(farenheit):
    return int((farenheit - 32) * 5/9)
