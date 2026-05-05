import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
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

def plot_spectral_shift_vs_voltage(
    df: pd.DataFrame,
    figure_name: str = 'spectral_shift_vs_voltage',
    show: bool = True,
    v_col: str = "Voltage (V)",
    wl_col: str = "Wavelength (nm)",
    p_col: str = "Power (dBm)",
) -> str:
    """
    Plots overlaid transmission spectra at each voltage from a
    spectral-shift-vs-voltage sweep. Resonance (min power) is marked
    on each trace; a legend maps trace color to bias voltage.

    Args:
        df: DataFrame from measure_spectral_shift_vs_voltage().
        figure_name: Name for the saved plot file (without extension).
        show: Whether to display the plot interactively.
        v_col, wl_col, p_col: Column names to read from the DataFrame.

    Returns:
        The path to the saved plot file.
    """
    if df.empty:
        print("No results to plot.")
        return ""

    voltages = np.sort(df[v_col].unique())

    fig, ax = plt.subplots(figsize=(8, 5))
    norm = plt.Normalize(vmin=voltages.min(), vmax=voltages.max())
    cmap = plt.cm.viridis

    for v in voltages:
        sub = df[np.isclose(df[v_col], v)].sort_values(wl_col)
        color = cmap(norm(v))
        ax.plot(sub[wl_col], sub[p_col], color=color, lw=1.2,
                label=f"{v:g} V")
        k = sub[p_col].idxmin()
        ax.plot(sub.loc[k, wl_col], sub.loc[k, p_col],
                "o", color=color, markersize=5, mec="k", mew=0.5)

    ax.set_xlabel(wl_col)
    ax.set_ylabel(p_col)
    ax.set_title(figure_name)
    ax.grid(True)
    ax.legend(title=v_col, loc="best", fontsize=9)
    fig.tight_layout()

    plots_dir = os.path.join(os.getcwd(), 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    plot_path = os.path.join(plots_dir, f"{figure_name}.png")
    fig.savefig(plot_path)
    if show:
        plt.show()
    else:
        plt.close(fig)

    print(f"Plot saved as {plot_path}")
    return plot_path