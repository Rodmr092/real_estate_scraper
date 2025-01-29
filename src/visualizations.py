```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from typing import Optional, Tuple


def create_heatmap(
    data: pd.DataFrame,
    latitude_col: str = "latitude",
    longitude_col: str = "longitude",
    radius: int = 10,
    location: Optional[Tuple[float, float]] = None,
    zoom_start: int = 10,
) -> folium.Map:
    """
    Creates a Folium heatmap visualization for geographical coordinates.

    Args:
        data: DataFrame containing geographical coordinates
        latitude_col: Name of latitude column (default 'latitude')
        longitude_col: Name of longitude column (default 'longitude')
        radius: Heatmap point radius (default 10)
        location: Tuple (lat, lon) for map center (defaults to data mean)
        zoom_start: Initial map zoom level (default 10)

    Returns:
        folium.Map: Interactive heatmap object

    Raises:
        ValueError: If required columns are missing or data is empty
    """
    if not {latitude_col, longitude_col}.issubset(data.columns):
        raise ValueError(f"Missing required columns: {latitude_col} or {longitude_col}")
    if data.empty:
        raise ValueError("Data cannot be empty")

    loc = location or (data[latitude_col].mean(), data[longitude_col].mean())
    m = folium.Map(location=loc, zoom_start=zoom_start)
    heat_data = data[[latitude_col, longitude_col]].values.tolist()
    HeatMap(heat_data, radius=radius).add_to(m)
    return m


def plot_price_histogram(
    data: pd.Series,
    bins: int = 30,
    title: str = "Price Distribution",
    xlabel: str = "Price",
    ylabel: str = "Frequency",
) -> plt.Figure:
    """
    Creates a histogram for price distribution analysis.

    Args:
        data: Pandas Series containing price values
        bins: Number of histogram bins (default 30)
        title: Plot title (default 'Price Distribution')
        xlabel: X-axis label (default 'Price')
        ylabel: Y-axis label (default 'Frequency')

    Returns:
        plt.Figure: Matplotlib figure object

    Raises:
        ValueError: If data is empty or contains invalid values
    """
    if data.empty:
        raise ValueError("Data cannot be empty")
    if not pd.api.types.is_numeric_dtype(data):
        raise ValueError("Price data must be numeric")

    fig, ax = plt.subplots()
    sns.histplot(data, bins=bins, kde=False, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig


def plot_scatter(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "Scatter Plot",
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> plt.Figure:
    """
    Creates a scatter plot for comparing two numerical variables.

    Args:
        data: DataFrame containing the data
        x_col: Column name for x-axis values
        y_col: Column name for y-axis values
        title: Plot title (default 'Scatter Plot')
        xlabel: Custom x-axis label (defaults to x_col)
        ylabel: Custom y-axis label (defaults to y_col)

    Returns:
        plt.Figure: Matplotlib figure object

    Raises:
        ValueError: If specified columns are missing
    """
    if not {x_col, y_col}.issubset(data.columns):
        raise ValueError(f"Missing columns: {x_col} or {y_col}")

    fig, ax = plt.subplots()
    sns.scatterplot(data=data, x=x_col, y=y_col, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel or y_col)
    return fig
```