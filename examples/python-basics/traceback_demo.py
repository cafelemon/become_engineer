def calculate_progress(target_hours, finished_hours):
    return finished_hours / target_hours


def build_report():
    return calculate_progress(0, 2)


build_report()
