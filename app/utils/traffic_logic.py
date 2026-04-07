ALPHA                 = 0.3    # Smoothing weight — higher = faster response
MIN_GREEN_EMPTY       = 1.0    # Minimum green time when no cars detected (seconds)
MIN_GREEN_ACTIVE      = 10.0   # Minimum green time when cars are present (seconds)
MIN_GREEN_BONUS       = 15.0   # Extra bonus seconds allowed above default max
SMOOTH_JUMP_THRESHOLD = 8.0    # Gap size that skips smoothing and jumps directly


def _compute_proportional_targets(car_counts, default_max_green):
    """
    Distribute the total green time budget across cameras
    based on how many cars each camera has detected.
    Camera with more cars gets a bigger share of the total time.
    """
    total_cars   = sum(car_counts)
    total_budget = sum(default_max_green)
    targets      = []

    # No cars anywhere — return zero targets, boundaries will handle the rest
    if total_cars == 0:
        return [0.0] * len(car_counts)

    for cars in car_counts:
        share  = cars / total_cars        # This camera's fraction of total traffic
        target = share * total_budget     # Its proportional share of total green time
        targets.append(target)

    return targets


def _applied_boundaries(target, car, default_max):
    """
    Clamp the proportional target within safe operating limits.
    Ensures no camera gets too little or too much green time.
    """
    # Empty lane — give 1 second minimum so the cycle doesn't stall
    if car == 0:
        return MIN_GREEN_EMPTY

    target = max(target, MIN_GREEN_ACTIVE)          # Floor — never below 10s if active
    target = min(target, default_max + MIN_GREEN_BONUS)  # Ceiling — never above max + 15s bonus

    return target


def _smooth(current, target, alpha=ALPHA):
    """
    Gradually ease the current green time toward the new target.
    Prevents abrupt jumps when car counts change slightly.
    If the gap is too large, skip smoothing and jump directly.
    """
    # Large gap — apply immediately instead of lagging behind
    if abs(target - current) > SMOOTH_JUMP_THRESHOLD:
        return target

    # Exponential smoothing: 30% new value, 70% old value
    return (alpha * target) + ((1.0 - alpha) * current)


def recalculate_green_durations(current_green_times, car_counts, default_max_green):
    """
    Main entry point — called every 2 seconds by the traffic controller.
    Returns updated green durations for all cameras based on live car counts.
    """
    # Nothing to process — return current times unchanged
    if not car_counts or not default_max_green:
        return current_green_times

    # All three lists must match in length — one entry per camera
    if len(car_counts) != len(default_max_green) or len(car_counts) != len(current_green_times):
        raise ValueError(
            f"Length mismatch: car_counts={len(car_counts)}, "
            f"default_max_green={len(default_max_green)}, "
            f"current_green_times={len(current_green_times)}"
        )

    num_cameras = len(car_counts)
    raw_targets = _compute_proportional_targets(car_counts, default_max_green)
    new_items   = []

    for i in range(num_cameras):
        # Step 1: Clamp proportional target within safe limits
        target = _applied_boundaries(raw_targets[i], car_counts[i], default_max_green[i])

        # Step 2: Smooth toward the new target to avoid flickering
        result = _smooth(current_green_times[i], target)

        new_items.append(round(result, 2))

    return new_items