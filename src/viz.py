"""
Visualization utilities for metabolomics EDA.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def plot_group_counts_bar(meta: pd.DataFrame, col: str = "HEALTH_STATUS") -> plt.Figure:
    """
    Bar chart of sample counts per group.

    Parameters
    ----------
    meta : pd.DataFrame
        Sample metadata.
    col : str
        Column for grouping.

    Returns
    -------
    plt.Figure
        Matplotlib figure.
    """
    counts = meta[col].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    ax.bar(counts.index, counts.values, color="steelblue")
    ax.set_xlabel(col)
    ax.set_ylabel("Count")
    ax.set_title(f"Sample Count by {col}")
    plt.tight_layout()
    logger.info(f"Bar chart created for {col}.")
    return fig


def plot_group_counts_donut(meta: pd.DataFrame, col: str = "HEALTH_STATUS") -> plt.Figure:
    """
    Donut chart of sample counts per group.

    Parameters
    ----------
    meta : pd.DataFrame
        Sample metadata.
    col : str
        Column for grouping.

    Returns
    -------
    plt.Figure
        Matplotlib figure.
    """
    counts = meta[col].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    my_circle = plt.Circle((0, 0), 0.5, color="white")
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.2f%%",
        startangle=90,
        colors=sns.color_palette("Set2", len(counts)),
    )
    ax.add_artist(my_circle)
    ax.set_title(f"Sample Distribution by {col}")
    plt.tight_layout()
    logger.info(f"Donut chart created for {col}.")
    return fig


def scatter_bmi_hba1c(
    meta: pd.DataFrame,
    hue_col: str = "HEALTH_STATUS",
    figsize: tuple = (12, 8),
) -> plt.Figure:
    """
    Scatter plot of BMI vs HbA1c, colored by hue_col.

    Parameters
    ----------
    meta : pd.DataFrame
        Sample metadata.
    hue_col : str
        Column for color grouping.
    figsize : tuple
        Figure size.

    Returns
    -------
    plt.Figure
        Matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=figsize)
    sns.scatterplot(
        data=meta, x="BMI", y="hba1c", hue=hue_col, s=200, ax=ax, palette="Set1"
    )
    ax.set_title(f"BMI vs HbA1c (colored by {hue_col})")
    ax.set_xlabel("BMI")
    ax.set_ylabel("HbA1c")
    plt.legend(title=hue_col, bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    logger.info(f"Scatter plot created: BMI vs HbA1c by {hue_col}.")
    return fig


def bars_bmi_hba1c_plotly(meta: pd.DataFrame, group_col: str = "HEALTH_STATUS") -> go.Figure:
    """
    Grouped bar chart (Plotly) comparing BMI and HbA1c per group.

    Parameters
    ----------
    meta : pd.DataFrame
        Sample metadata.
    group_col : str
        Column for grouping.

    Returns
    -------
    go.Figure
        Plotly figure.
    """
    trace1 = go.Bar(
        x=meta[group_col],
        y=meta["BMI"],
        name="BMI",
        marker=dict(color="rgba(0, 40, 70, 0.6)"),
    )
    trace2 = go.Bar(
        x=meta[group_col],
        y=meta["hba1c"],
        name="HbA1c",
        marker=dict(color="rgba(255, 148, 7, 0.6)"),
    )
    fig = go.Figure(data=[trace1, trace2])
    fig.update_layout(
        barmode="group",
        title="BMI and HbA1c by Health Status",
        xaxis_title=group_col,
        yaxis_title="Value",
    )
    logger.info("Plotly grouped bar chart created.")
    return fig


def sex_by_group_catplot(meta: pd.DataFrame, col: str = "HEALTH_STATUS") -> plt.Figure:
    """
    Catplot showing sample count by sex and health status.

    Parameters
    ----------
    meta : pd.DataFrame
        Sample metadata.
    col : str
        Column for facet grouping.

    Returns
    -------
    plt.Figure
        Seaborn FacetGrid (returns the underlying figure).
    """
    g = sns.catplot(
        data=meta,
        x="sex",
        col=col,
        kind="count",
        height=4,
        aspect=1.2,
        palette="muted",
    )
    g.set_titles(col_template="{col_name}")
    g.set_axis_labels("Sex", "Count")
    g.fig.suptitle(f"Sample Count by Sex and {col}", y=1.02)
    plt.tight_layout()
    logger.info(f"Catplot created: sex by {col}.")
    return g.fig


def bar_super_pathway(data_dict: pd.DataFrame, col: str = "SUPER_PATHWAY") -> go.Figure:
    """
    Bar chart of compound counts per super pathway.

    Parameters
    ----------
    data_dict : pd.DataFrame
        Data dictionary with SUPER_PATHWAY column.
    col : str
        Column for grouping.

    Returns
    -------
    go.Figure
        Plotly bar chart.
    """
    counts = data_dict[col].value_counts().reset_index()
    counts.columns = [col, "count"]

    fig = px.bar(
        counts,
        x=col,
        y="count",
        color=col,
        title=f"Compound Count by {col}",
        labels={col: "Super Pathway", "count": "Count"},
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    logger.info(f"Bar chart created for {col}.")
    return fig
