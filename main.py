import os
import requests
import arcade
from distance import lonlat_distance

GEO_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
SEARCH_KEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
STATIC_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"


class PharmacyTen(arcade.Window):
    def __init__(self, address):
        super().__init__(600, 450, "10 ближайших аптек")
        self.address = address
        self.background = None

    def setup(self):
        geo_params = {"apikey": GEO_KEY, "geocode": self.address, "format": "json"}
        geo_res = requests.get("http://geocode-maps.yandex.ru/1.x/", params=geo_params).json()
        user_coords = geo_res["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        user_lonlat = tuple(map(float, user_coords.split()))

        search_params = {
            "apikey": SEARCH_KEY,
            "text": "аптека",
            "lang": "ru_RU",
            "ll": f"{user_lonlat[0]},{user_lonlat[1]}",
            "type": "biz",
            "results": 10
        }
        search_res = requests.get("https://search-maps.yandex.ru/v1/", params=search_params).json()

        points = []
        points.append(f"{user_lonlat[0]},{user_lonlat[1]},pm2rdl")

        max_dist = 0

        for organization in search_res["features"]:
            org_coords = organization["geometry"]["coordinates"]
            metadata = organization["properties"]["CompanyMetaData"]

            d = lonlat_distance(user_lonlat, org_coords)
            if d > max_dist:
                max_dist = d

            if "Hours" not in metadata:
                color = "gr"
            elif "Availability" in metadata["Hours"] and \
                    metadata["Hours"]["Availability"].get("Everyday") and \
                    metadata["Hours"]["Availability"].get("TwentyFourHours"):
                color = "gn"
            else:
                color = "bl"

            points.append(f"{org_coords[0]},{org_coords[1]},pm2{color}m")

        print(round(max_dist))

        map_params = {
            "apikey": STATIC_KEY,
            "l": "map",
            "pt": "~".join(points)
        }

        map_res = requests.get("https://static-maps.yandex.ru/v1", params=map_params)
        with open("map.png", "wb") as f:
            f.write(map_res.content)
        self.background = arcade.load_texture("map.png")

    def on_draw(self):
        self.clear()
        if self.background:
            arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, self.width, self.height))


if __name__ == "__main__":
    addr = input("Введите адрес:")

    window = PharmacyTen(addr)
    window.setup()
    arcade.run()
    if os.path.exists("map.png"):
        os.remove("map.png")