from app.config import TRAFFIC_LIGHT_SETTINGS, CAMERA_GREEN_DEFAULTS

# smoothing factor/min ratio constants
ALPHA = 0.3
MIN_GREEN_RATIO = 0.5


def recalculate_green_durations(current_green_times, car_counts, default_max_green):
    """
    Business logic for calculating dynamic traffic light durations.
    Returns a list of updated green light times (seconds).
    """
    if not car_counts or not default_max_green:
        return current_green_times

    num_cameras = len(car_counts)
    avg_cars = sum(car_counts) / num_cameras if num_cameras > 0 else 0
    new_times = []

    for i in range(num_cameras):
        default_max = default_max_green[i]
        cars = car_counts[i]

        # 1. BASE TARGET (Default from config)
        target = float(default_max)

        # 2. BONUS/PENALTY LOGIC
        if cars > 0:
            if cars > avg_cars * 1.5:
                target += 5.0
            elif cars > avg_cars:
                target += 2.0
            elif cars < avg_cars * 0.5:
                target -= 5.0
            elif cars < avg_cars:
                target -= 2.0
        else:
            target = 1.0  # Skip if empty

        # 3. BOUNDARIES
        if cars > 0:
            target = max(target, 10.0)

        # Cap at default + 15
        target = min(target, default_max + 15.0)

        # 4. SMOOTHING (Weighted average)
        # alpha * target + (1-alpha) * current
        current = current_green_times[i]
        result = (ALPHA * target) + ((1.0 - ALPHA) * current)
        new_times.append(float(result))

    return new_times
