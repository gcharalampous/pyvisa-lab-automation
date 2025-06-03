import os
import matplotlib.pyplot as plt
from typing import List, Tuple

def plot_measurements(
    headers: Tuple[str, str],
    results: List[Tuple[float, float]],
    figure_name: str = 'sweep_plot',
    show: bool = True
) -> str:
    """
    Plots the results from the laser sweep.

    Args:
        results: A list of (wavelength, power) tuples.
        figure_name: Name for the saved plot file (without extension).
        show: Whether to display the plot interactively.

    Returns:
        The path to the saved plot file.
    """
    if not results:
        print("No results to plot.")
        return ""

    xlabel, ylabel = headers
    wavelengths, powers = zip(*results)

    plt.figure(figsize=(8, 5))
    plt.plot(wavelengths, powers)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(figure_name)
    plt.grid(True)
    plt.tight_layout()

    plots_dir = os.path.join(os.getcwd(), 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    plot_path = os.path.join(plots_dir, f"{figure_name}.png")
    plt.savefig(plot_path)

    if show:
        plt.show()
    else:
        plt.close()

    print(f"Plot saved as {plot_path}")
    return plot_path

