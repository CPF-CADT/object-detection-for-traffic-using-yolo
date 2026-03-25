"""
Shared non-UI logic for light management and timing.
"""


def update_remaining_time(current_time, active_light, timers):
    """Decrease remaining time and handle phase change signals."""
    if current_time > 0:
        return current_time - 1, None

    # Logic for manual phase changes if needed (automatic is often better)
    if active_light == "green":
        return timers.get("yellow", 5), "yellow"
    elif active_light == "yellow":
        return timers.get("red", 30), "red"
    return 0, None


def get_light_timers(camera_id, traffic_light_settings, camera_green_defaults):
    """Retrieve timer durations for a camera from configuration."""
    return {
        "red": traffic_light_settings.get("default_red", 30),
        "yellow": traffic_light_settings.get("default_yellow", 5),
        "green": camera_green_defaults.get(
            camera_id, traffic_light_settings.get("default_green", 25)
        ),
    }


def calculate_new_timer_after_setting_changed(
    color, active_light, new_value, current_remaining
):
    """Calculate what the new remaining time should be if a setting is updated."""
    if color == active_light:
        return new_value
    return current_remaining
