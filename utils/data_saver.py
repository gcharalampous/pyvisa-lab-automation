import os
from typing import List, Tuple

def save_raw_measurements(
    headers: Tuple[str, ...],
    data: List[Tuple[float, ...]],
    filename: str = 'sweep_data',
) -> str:
    if not data:
        print("No results to plot.")
        return ""

    plots_dir = os.path.join(os.getcwd(), 'data/raw')
    os.makedirs(plots_dir, exist_ok=True)
    data_path = os.path.join(plots_dir, f"{filename}.csv")

    with open(data_path, 'w') as f:
        f.write(",".join(headers) + "\n")
        for row in data:
            f.write(",".join(str(value) for value in row) + "\n")

    print(f"Data saved as {data_path}")
    return data_path
