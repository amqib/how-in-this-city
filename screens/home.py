import requests
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import timezone
import pytz


class Home(MDScreen):

    api_key =  "f660336cd37671a6310d8480c3fd5f93"
    
    def __init__(self, **kw):
        Builder.load_file("kv/home.kv")
        super().__init__(**kw)

    def on_start(self):
        try:
            soup = BeautifulSoup(request.get(f"https://www.google.com/search?q=weather+at+my+current+location").text, "html.parser")
            temp = soup.find("span", class_ = "BNeawe tAd8D AP7Wnd")
            location = ''.join(filter(lambda item: not item.isdigit(), temp.text)).split(",",1)
            self.get_weather(location[0])
        except request.ConnectionError:
            print("No Internet Connection")
            exit()

    def get_weather(self, city_name):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={self.api_key}"
            response = requests.get(url)
            X = response.json()

            if X["cod"] != "404":
                lon = str(X["coord"]["lon"])
                lat = str(X["coord"]["lat"])
                temperature = round(X["main"]["temp"]-273.15)
                humidity = X["main"]["humidity"]
                weather = X["weather"][0]["main"]
                id = str(X["weather"][0]["id"])
                wind_speed = round(X["wind"]["speed"]*18/5)
                location = X["name"] + ","+ X["sys"]["country"]
                self.ids.temperature.text = f"[b]{temperature}[/b]°"
                self.ids.humidity.text = f"{humidity}%"
                self.ids.weather.text = str(weather)
                self.ids.wind_speed.text = f"{wind_speed} km/h"
                self.ids.location.text = location
                now, timeZone = self.get_times(lon, lat)
                
                sunrise_start, sunrise_end = self.on_timezone(X["sys"]["sunrise"], timeZone)
                sunset_start, sunset_end = self.on_timezone(X["sys"]["sunset"], timeZone)

                if id == "800":
                    if now > sunrise_end and now < sunset_start :
                        self.ids.weather_image.source = "Assets/images/sun.png" #Clear Sky noon
                    if now >= sunrise_start and now <= sunrise_end :
                        self.ids.weather_image.source = "Assets/images/sunrise.png" #sunrise
                    if now < sunrise_start or now > sunset_end :
                        self.ids.weather_image.source = "Assets/images/moon.png" #Clear Sky night
                    if now >= sunset_start and now <= sunset_end :
                        self.ids.weather_image.source = "Assets/images/sunsets.png" #sunset
                if id > "800":
                    if now < sunset_start and now > sunrise_end:
                        self.ids.weather_image.source = "Assets/images/cloudy.png" #Clouds
                    if now >= sunset_start and now <= sunset_end :
                        self.ids.weather_image.source = "Assets/images/sunsets.png" #Clear Sky
                    if now >= sunrise_start and now <= sunrise_end :
                        self.ids.weather_image.source = "Assets/images/sunrise.png" #Clear Sky
                    if now < sunrise_start or now > sunset_end:
                        self.ids.weather_image.source = "Assets/images/night.png" #Clouds
                if "200" <= id <= "232" and id != "211":
                    self.ids.weather_image.source = "Assets/images/storm.png" #ThunderStorm with Rain
                if id == "211":
                    self.ids.weather_image.source = "Assets/images/thunder.png" #Only Thunder
                if "300" <= id <= "321":
                    self.ids.weather_image.source = "Assets/images/rain2.png" #Drizzle
                if "500" <= id <= "504":
                    if now < sunrise_start or now > sunset_end:
                        self.ids.weather_image.source = "Assets/images/nightrain.png" #Light Rain
                    else:
                        self.ids.weather_image.source = "Assets/images/rain1.png" #Light Rain
                    # self.ids.weather_image.source = "Assets/images/rain1.png" #Light Rain
                if id == "511":
                    self.ids.weather_image.source = "Assets/images/blizzard.png" #Freezing Rain
                if "520" <= id <= "531":
                    self.ids.weather_image.source = "Assets/images/rain.png" #Shower Rain
                if "600" <= id <= "622":
                    self.ids.weather_image.source = "Assets/images/snow.png" #Snow
                if "701" <= id <= "781":
                    self.ids.weather_image.source = "Assets/images/cloud.png" #smoke
   
            else:
                print("City Not Found")

        except requests.ConnectionError:
            print("No Internet Connection")


    def get_times(self, lon, lat):
        try:
            url = f"https://www.timeapi.io/api/Time/current/coordinate?latitude={lat}&longitude={lon}"
            response = requests.get(url)
            X = response.json()
            loc_time = X["time"]
            loc_day = X["dayOfWeek"]+ "   "+ X["date"]
            self.ids.loc_time.text = loc_time
            self.ids.loc_day.text = loc_day
            return loc_time, X["timeZone"]

        except requests.ConnectionError:
            print("No Internet Connection")


    def on_timezone(self, ts, tz):
        utc = pytz.utc
        utc_time = utc.localize(datetime.utcfromtimestamp(ts))
        loc_tz = timezone(tz)
        loc_dt = utc_time.astimezone(loc_tz)
        loc_dt_end = loc_dt + timedelta(minutes = 15)
        return loc_dt.strftime("%H:%M"), loc_dt_end.strftime("%H:%M")

    def search_weather(self):
        city_name =self.ids.city_name.text
        if city_name != "":
            self.get_weather(city_name)

