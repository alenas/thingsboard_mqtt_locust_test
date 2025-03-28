import time

class PayloadGenerator:
    arr = [[37.76767, -122.21994],[37.76767, -122.21995],[37.76767, -122.21994],[37.7595, -122.21303],[37.75264, -122.20693],[37.74618, -122.20138],[37.74475, -122.1962],[37.740997, -122.20101],[37.74086, -122.19651],[37.73724, -122.1922],[37.73724, -122.1922]]
    inc = 0
    step = 0

    def __getData(self):
        if (self.inc==0):
            self.step = self.step + 1
        else:
            self.step = self.step - 1

        if self.step < 0:
            self.step = 0
            self.inc = 0
        if self.step >= len(self.arr):
            self.inc = 1
            self.step = len(self.arr) - 1
        return self.arr[self.step]

    def next(self):
        lat, lng = self.__getData()

        payload = {
            "ts": int(time.time() * 1000),
            "values": {
                "alt": 10.0,
                "crs": 45.0,
                "lat": lat,
                "lon": lng,
                "spd": 1.0,
            }
        }
        return payload