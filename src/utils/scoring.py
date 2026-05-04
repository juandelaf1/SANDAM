from src.models import FlagColor, WaterQuality


def calculate_flag_score(flag: FlagColor) -> float:
    scores = {
        FlagColor.green: 100.0,
        FlagColor.yellow: 50.0,
        FlagColor.red: 0.0,
        FlagColor.unknown: 25.0,
    }
    return scores.get(flag, 25.0)


def calculate_occupation_score(occupation: int) -> float:
    if occupation <= 30:
        return 100.0
    elif occupation <= 50:
        return 90.0
    elif occupation <= 70:
        return 70.0
    elif occupation <= 85:
        return 50.0
    else:
        return 20.0


def calculate_quality_score(quality: WaterQuality) -> float:
    scores = {
        WaterQuality.excellent: 100.0,
        WaterQuality.good: 75.0,
        WaterQuality.sufficient: 50.0,
        WaterQuality.poor: 0.0,
        WaterQuality.unknown: 25.0,
    }
    return scores.get(quality, 25.0)


def calculate_jellyfish_score(present: bool) -> float:
    return 0.0 if present else 100.0


def calculate_uv_score(uv_index: int | None) -> float:
    if uv_index is None:
        return 75.0
    if uv_index <= 2:
        return 100.0
    elif uv_index <= 5:
        return 90.0
    elif uv_index <= 7:
        return 70.0
    elif uv_index <= 10:
        return 50.0
    else:
        return 30.0


def calculate_wave_score(wave_height: float | None) -> float:
    if wave_height is None:
        return 75.0
    if wave_height <= 0.5:
        return 100.0
    elif wave_height <= 1.0:
        return 90.0
    elif wave_height <= 1.5:
        return 75.0
    elif wave_height <= 2.0:
        return 50.0
    else:
        return 20.0


def calculate_overall_score(beach: dict) -> float:
    flag_score = calculate_flag_score(beach.get("flag_color", FlagColor.unknown))
    occupation_score = calculate_occupation_score(beach.get("current_occupation", 0))
    quality_score = calculate_quality_score(beach.get("water_quality", WaterQuality.unknown))
    jellyfish_score = calculate_jellyfish_score(beach.get("jellyfish_present", False))
    uv_score = calculate_uv_score(beach.get("uv_index"))
    wave_score = calculate_wave_score(beach.get("wave_height"))

    overall = (
        flag_score * 0.30
        + occupation_score * 0.25
        + quality_score * 0.20
        + jellyfish_score * 0.15
        + uv_score * 0.05
        + wave_score * 0.05
    )

    return round(overall, 1)


def calculate_safety_score(beach: dict) -> int:
    score = 100
    if beach.get("flag_color") == FlagColor.red:
        score -= 50
    elif beach.get("flag_color") == FlagColor.yellow:
        score -= 20
    if beach.get("jellyfish_present"):
        score -= 30
    if not beach.get("has_lifeguard"):
        score -= 15
    if beach.get("wave_height", 0) > 2:
        score -= 20
    if beach.get("water_quality") == WaterQuality.poor:
        score -= 40
    elif beach.get("water_quality") == WaterQuality.sufficient:
        score -= 15
    return max(0, score)


def calculate_comfort_score(beach: dict) -> int:
    score = 0
    if beach.get("has_shade"):
        score += 20
    if beach.get("has_showers"):
        score += 20
    if beach.get("has_kiosk"):
        score += 15
    if beach.get("has_parking"):
        score += 15
    if beach.get("has_accessibility"):
        score += 20
    if beach.get("current_occupation", 100) < 50:
        score += 10
    return min(100, score)