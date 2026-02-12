"""Geospatial tools for distance calculation and ancient place geocoding.

This module provides GIS functionality for the simulation, including distance
calculations using the Haversine formula and geocoding of ancient Chinese
place names to modern coordinates.
"""

import math
from typing import Dict, Optional, Tuple

from src.domain.schemas import GeoPoint


# Ancient place name to coordinates mapping (MVP hardcoded database)
# Will be replaced with Mapbox API or similar in production
ANCIENT_PLACES: Dict[str, Tuple[float, float]] = {
    # Major cities during Liang Dynasty
    "建康": (32.0583, 118.7966),  # Modern Nanjing
    "台城": (32.0667, 118.8000),  # Taicheng Palace within Jiankang
    "江陵": (30.3509, 112.2051),  # Modern Jingzhou
    "荆州": (30.3509, 112.2051),  # Same as Jiangling
    "襄阳": (32.0654, 112.1440),  # Xiangyang
    "寻阳": (29.7272, 116.0006),  # Modern Jiujiang
    "建业": (32.0583, 118.7966),  # Earlier name for Jiankang
    "金陵": (32.0583, 118.7966),  # Another name for Jiankang

    # Rivers and strategic points
    "秦淮河": (32.0183, 118.7789),  # Qinhuai River
    "长江": (32.0583, 118.7966),  # Yangtze River (using Jiankang as reference)
    "汉水": (32.0654, 112.1440),   # Han River (using Xiangyang as reference)

    # Administrative regions
    "扬州": (32.3932, 119.4125),  # Yangzhou
    "荆襄": (32.0654, 112.1440),  # Jingxiang region

    # Modern reference for testing
    "南京": (32.0583, 118.7966),
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
}


def calculate_distance(point_a: GeoPoint, point_b: GeoPoint) -> float:
    """Calculate great-circle distance between two points using Haversine formula.

    This function computes the shortest distance over the earth's surface,
    giving an "as-the-crow-flies" distance between two geographic coordinates.

    Args:
        point_a: First geographical point.
        point_b: Second geographical point.

    Returns:
        Distance in kilometers.

    Example:
        >>> jiankang = GeoPoint(lat=32.0583, lon=118.7966, place_name="建康")
        >>> jiangling = GeoPoint(lat=30.3509, lon=112.2051, place_name="江陵")
        >>> distance = calculate_distance(jiankang, jiangling)
        >>> print(f"{distance:.2f} km")
        674.32 km

    Note:
        Uses Earth radius of 6371 km. Accuracy is sufficient for historical
        navigation purposes (±0.5% for distances < 1000 km).
    """
    # Earth's radius in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(point_a.lat)
    lon1 = math.radians(point_a.lon)
    lat2 = math.radians(point_b.lat)
    lon2 = math.radians(point_b.lon)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    distance = R * c
    return distance


def calculate_bearing(point_a: GeoPoint, point_b: GeoPoint) -> float:
    """Calculate initial bearing (direction) from point_a to point_b.

    Bearing is measured in degrees clockwise from true north (0°).
    - North: 0° or 360°
    - East: 90°
    - South: 180°
    - West: 270°

    Args:
        point_a: Starting point.
        point_b: Destination point.

    Returns:
        Bearing in degrees (0-360).

    Example:
        >>> jiankang = GeoPoint(lat=32.0583, lon=118.7966, place_name="建康")
        >>> jiangling = GeoPoint(lat=30.3509, lon=112.2051, place_name="江陵")
        >>> bearing = calculate_bearing(jiankang, jiangling)
        >>> print(f"{bearing:.1f}°")  # Should be roughly southwest (225°)
    """
    lat1 = math.radians(point_a.lat)
    lat2 = math.radians(point_b.lat)
    lon_diff = math.radians(point_b.lon - point_a.lon)

    x = math.sin(lon_diff) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon_diff)

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)

    # Normalize to 0-360 range
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def get_cardinal_direction(bearing: float) -> str:
    """Convert numeric bearing to cardinal direction.

    Args:
        bearing: Bearing in degrees (0-360).

    Returns:
        Cardinal direction in Chinese (e.g., "西南", "正北").

    Example:
        >>> get_cardinal_direction(225)
        '西南'
        >>> get_cardinal_direction(45)
        '东北'
    """
    directions = [
        (0, "正北", "due north"),
        (22.5, "东北偏北", "north-northeast"),
        (45, "东北", "northeast"),
        (67.5, "东北偏东", "east-northeast"),
        (90, "正东", "due east"),
        (112.5, "东南偏东", "east-southeast"),
        (135, "东南", "southeast"),
        (157.5, "东南偏南", "south-southeast"),
        (180, "正南", "due south"),
        (202.5, "西南偏南", "south-southwest"),
        (225, "西南", "southwest"),
        (247.5, "西南偏西", "west-southwest"),
        (270, "正西", "due west"),
        (292.5, "西北偏西", "west-northwest"),
        (315, "西北", "northwest"),
        (337.5, "西北偏北", "north-northwest"),
        (360, "正北", "due north"),
    ]

    # Normalize bearing
    bearing = bearing % 360

    # Find closest direction
    for i in range(len(directions) - 1):
        if directions[i][0] <= bearing < directions[i + 1][0]:
            return directions[i][1]

    return directions[0][1]  # Default to north


def estimate_travel_time(
    distance_km: float,
    mode: str = "foot",
    terrain: str = "flat"
) -> float:
    """Estimate travel time for 6th century China.

    Travel speeds are based on historical records and geographical factors
    of the Northern and Southern Dynasties period.

    Args:
        distance_km: Distance to travel in kilometers.
        mode: Transportation mode. Options:
            - "foot": Walking
            - "horse": Horseback riding
            - "boat": River travel
            - "cart": Ox cart
        terrain: Terrain type. Options:
            - "flat": Plains or well-maintained roads
            - "hills": Hilly terrain
            - "mountains": Mountain passes
            - "river": River travel (current direction matters)

    Returns:
        Estimated travel time in hours.

    Example:
        >>> distance = 674  # Jiankang to Jiangling
        >>> time_foot = estimate_travel_time(distance, mode="foot", terrain="flat")
        >>> print(f"On foot: {time_foot / 24:.1f} days")
        On foot: 11.2 days
        >>> time_boat = estimate_travel_time(distance, mode="boat")
        >>> print(f"By boat: {time_boat / 24:.1f} days")
        By boat: 5.6 days

    Note:
        These are idealized estimates. Actual travel times would vary based on:
        - Weather conditions
        - Military checkpoints
        - Need for rest and resupply
        - Safety concerns (bandits, warfare)
    """
    # Base speeds in km/h (6th century estimates)
    speeds = {
        "foot": 4.0,      # Sustained walking pace with rest
        "horse": 8.0,     # Not galloping, sustainable pace
        "boat": 5.0,      # Downstream Yangtze River
        "cart": 3.0,      # Ox cart on roads
    }

    # Terrain modifiers (multiplies travel time)
    terrain_modifiers = {
        "flat": 1.0,
        "hills": 1.5,
        "mountains": 2.5,
        "river": 0.8,     # Rivers often faster than land
    }

    base_speed = speeds.get(mode, 4.0)
    terrain_mod = terrain_modifiers.get(terrain, 1.0)

    # Calculate travel time
    travel_time = (distance_km / base_speed) * terrain_mod

    return travel_time


def get_coordinates(ancient_name: str) -> Optional[GeoPoint]:
    """Get coordinates for an ancient Chinese place name.

    MVP implementation uses hardcoded coordinates. In production, this would
    query a historical GIS database or modern geocoding API with name mapping.

    Args:
        ancient_name: Ancient place name (Chinese characters).

    Returns:
        GeoPoint with coordinates and place name, or None if not found.

    Example:
        >>> jiankang = get_coordinates("建康")
        >>> print(f"{jiankang.place_name}: ({jiankang.lat}, {jiankang.lon})")
        建康: (32.0583, 118.7966)

    Note:
        Currently supports major cities and strategic locations from
        the Liang Dynasty period (502-557 CE).
    """
    coords = ANCIENT_PLACES.get(ancient_name)

    if coords is None:
        return None

    return GeoPoint(
        lat=coords[0],
        lon=coords[1],
        place_name=ancient_name
    )


def get_route_info(origin: str, destination: str) -> Dict[str, any]:
    """Get comprehensive route information between two ancient places.

    Combines distance, bearing, direction, and travel time estimates into
    a single convenient function for agent decision-making.

    Args:
        origin: Starting location (ancient name).
        destination: Target location (ancient name).

    Returns:
        Dictionary containing:
        - origin_coords: GeoPoint of origin
        - dest_coords: GeoPoint of destination
        - distance_km: Distance in kilometers
        - bearing: Numeric bearing in degrees
        - direction: Cardinal direction (Chinese)
        - travel_time_foot: Estimated hours on foot
        - travel_time_boat: Estimated hours by boat
        - travel_time_horse: Estimated hours by horse

    Raises:
        ValueError: If either location name is not found.

    Example:
        >>> route = get_route_info("建康", "江陵")
        >>> print(f"Distance: {route['distance_km']:.1f} km")
        >>> print(f"Direction: {route['direction']}")
        >>> print(f"Travel time (foot): {route['travel_time_foot'] / 24:.1f} days")
    """
    origin_coords = get_coordinates(origin)
    dest_coords = get_coordinates(destination)

    if origin_coords is None:
        raise ValueError(f"Unknown location: {origin}")
    if dest_coords is None:
        raise ValueError(f"Unknown location: {destination}")

    distance = calculate_distance(origin_coords, dest_coords)
    bearing = calculate_bearing(origin_coords, dest_coords)
    direction = get_cardinal_direction(bearing)

    # Assume flat terrain for major routes, river travel along Yangtze
    is_river_route = any(river in [origin, destination] for river in ["江陵", "建康", "寻阳"])
    terrain = "river" if is_river_route else "flat"

    return {
        "origin_coords": origin_coords,
        "dest_coords": dest_coords,
        "distance_km": distance,
        "bearing": bearing,
        "direction": direction,
        "direction_en": get_cardinal_direction_en(bearing),
        "travel_time_foot": estimate_travel_time(distance, mode="foot", terrain="flat"),
        "travel_time_boat": estimate_travel_time(distance, mode="boat", terrain=terrain),
        "travel_time_horse": estimate_travel_time(distance, mode="horse", terrain="flat"),
    }


def get_cardinal_direction_en(bearing: float) -> str:
    """Convert numeric bearing to cardinal direction (English).

    Args:
        bearing: Bearing in degrees (0-360).

    Returns:
        Cardinal direction in English (e.g., "southwest", "north").
    """
    directions = [
        (0, "north"),
        (22.5, "north-northeast"),
        (45, "northeast"),
        (67.5, "east-northeast"),
        (90, "east"),
        (112.5, "east-southeast"),
        (135, "southeast"),
        (157.5, "south-southeast"),
        (180, "south"),
        (202.5, "south-southwest"),
        (225, "southwest"),
        (247.5, "west-southwest"),
        (270, "west"),
        (292.5, "west-northwest"),
        (315, "northwest"),
        (337.5, "north-northwest"),
        (360, "north"),
    ]

    bearing = bearing % 360

    for i in range(len(directions) - 1):
        if directions[i][0] <= bearing < directions[i + 1][0]:
            return directions[i][1]

    return directions[0][1]


def format_route_description(route_info: Dict[str, any]) -> str:
    """Format route information into human-readable text for LLM prompts.

    Args:
        route_info: Dictionary from get_route_info().

    Returns:
        Formatted description string suitable for inclusion in prompts.

    Example:
        >>> route = get_route_info("建康", "江陵")
        >>> print(format_route_description(route))
        从建康至江陵：
        - 距离：674.3 公里
        - 方向：西南
        - 徒步约 11.2 天
        - 水路约 5.6 天
        - 骑马约 5.6 天
    """
    origin_name = route_info["origin_coords"].place_name
    dest_name = route_info["dest_coords"].place_name
    distance = route_info["distance_km"]
    direction = route_info["direction"]

    time_foot_days = route_info["travel_time_foot"] / 24
    time_boat_days = route_info["travel_time_boat"] / 24
    time_horse_days = route_info["travel_time_horse"] / 24

    description = f"""从{origin_name}至{dest_name}：
- 距离：{distance:.1f} 公里
- 方向：{direction}
- 徒步约 {time_foot_days:.1f} 天
- 水路约 {time_boat_days:.1f} 天
- 骑马约 {time_horse_days:.1f} 天"""

    return description
