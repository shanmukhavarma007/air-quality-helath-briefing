from dataclasses import dataclass
from typing import Optional


@dataclass
class AQIBreakpoint:
    c_low: float
    c_high: float
    i_low: int
    i_high: int
    category: str
    hex_color: str


PM25_BREAKPOINTS = [
    AQIBreakpoint(0.0,    12.0,   0,   50,  "Good",                   "#00E400"),
    AQIBreakpoint(12.1,   35.4,  51,  100, "Moderate",               "#FFFF00"),
    AQIBreakpoint(35.5,   55.4,  101, 150, "Unhealthy for Sensitive", "#FF7E00"),
    AQIBreakpoint(55.5,   150.4,  151, 200, "Unhealthy",              "#FF0000"),
    AQIBreakpoint(150.5,  250.4,  201, 300, "Very Unhealthy",         "#8F3F97"),
    AQIBreakpoint(250.5,  500.4,  301, 500, "Hazardous",              "#7E0023"),
]

PM10_BREAKPOINTS = [
    AQIBreakpoint(0,      54,     0,   50,  "Good",                   "#00E400"),
    AQIBreakpoint(55,     154,    51,  100, "Moderate",               "#FFFF00"),
    AQIBreakpoint(155,    254,    101, 150, "Unhealthy for Sensitive", "#FF7E00"),
    AQIBreakpoint(255,    354,    151, 200, "Unhealthy",              "#FF0000"),
    AQIBreakpoint(355,    424,    201, 300, "Very Unhealthy",         "#8F3F97"),
    AQIBreakpoint(425,    604,    301, 500, "Hazardous",              "#7E0023"),
]


def calculate_aqi(concentration: float, breakpoints: list[AQIBreakpoint]) -> Optional[int]:
    for bp in breakpoints:
        if bp.c_low <= concentration <= bp.c_high:
            aqi = ((bp.i_high - bp.i_low) / (bp.c_high - bp.c_low)) * (concentration - bp.c_low) + bp.i_low
            return round(aqi)
    return None


def get_aqi_category(aqi_value: int) -> tuple[str, str]:
    if aqi_value <= 50:
        return "Good", "#00E400"
    elif aqi_value <= 100:
        return "Moderate", "#FFFF00"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive", "#FF7E00"
    elif aqi_value <= 200:
        return "Unhealthy", "#FF0000"
    elif aqi_value <= 300:
        return "Very Unhealthy", "#8F3F97"
    else:
        return "Hazardous", "#7E0023"
