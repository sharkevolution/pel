Title: Вычисление расстояний на сфере
Date: 2022-01-01 23:50
Author: Sitala
Tags: Python, Earth, coordinates, algorithm
Cover: /images/calc_coords.png
Summary:

## Алгоритм вычисления расстояния на сфере между двумя координатными точками wgs-84

#### Координаты заданы в десятичных градусах

#### Пример

```python
import math

def calc_dist(origin, destination):
    '''Вычисление расстояний на сфере'''

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

```