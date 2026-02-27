import math
from typing import Tuple


def get_bounding_box(
    latitude: float,
    longitude: float,
    radius_km: float,
) -> Tuple[float, float, float, float]:
    """
    Возвращает границы координатного квадрата (bounding box)
    вокруг точки с заданным радиусом (в км).

    :param latitude: широта центра
    :param longitude: долгота центра
    :param radius_km: радиус в километрах
    :return: (min_lat, max_lat, min_lon, max_lon)
    """

    lat_delta = radius_km / 111
    lon_delta = radius_km / (111 * math.cos(math.radians(latitude)))

    min_lat = latitude - lat_delta
    max_lat = latitude + lat_delta
    min_lon = longitude - lon_delta
    max_lon = longitude + lon_delta

    return min_lat, max_lat, min_lon, max_lon
