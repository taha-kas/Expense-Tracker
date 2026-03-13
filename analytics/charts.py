import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_theme(style="dark")

PALETTE = {
    "Income": "#4CAF50",
    "Spending": "#F44336",
    "Budget": "#2196F3",
    "Spent": "#F44336",
}

DARK_BG = "#1e1e1e"
DARK_FG = "#ffffff"


def _apply_dark_style(fig, ax):
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.title.set_color(DARK_FG)
    ax.xaxis.label.set_color(DARK_FG)
    ax.yaxis.label.set_color(DARK_FG)
    ax.tick_params(colors=DARK_FG)
    for spine in ax.spines.values():
        spine.set_edgecolor("#444444")
    legend = ax.get_legend()
    if legend:
        legend.get_frame().set_facecolor(DARK_BG)
        for text in legend.get_texts():
            text.set_color(DARK_FG)


def _fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    return buf.read()


def chart_spending_by_month(df_month):
    if df_month.empty:
        return None

    df_melted = df_month.melt(
        id_vars="month",
        value_vars=["total_spent"],
        var_name="type",
        value_name="amount"
    )
    df_melted["type"] = "Spending"

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(data=df_melted, x="month", y="amount", hue="type", palette=PALETTE, ax=ax)

    ax.set_title("Spending by Month", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount ($)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f"${val:,.0f}"))
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="")
    _apply_dark_style(fig, ax)
    fig.tight_layout()

    return _fig_to_bytes(fig)


def chart_income_vs_spending_by_month(df_overview):
    if df_overview.empty:
        return None

    df_melted = df_overview.melt(
        id_vars="month",
        value_vars=["total_income", "total_spent"],
        var_name="type",
        value_name="amount"
    )
    df_melted["type"] = df_melted["type"].map({
        "total_income": "Income",
        "total_spent": "Spending"
    })

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(data=df_melted, x="month", y="amount", hue="type", palette=PALETTE, ax=ax)

    ax.set_title("Income vs Spending by Month", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount ($)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f"${val:,.0f}"))
    ax.tick_params(axis="x", rotation=45)
    ax.legend(title="")
    _apply_dark_style(fig, ax)
    fig.tight_layout()

    return _fig_to_bytes(fig)


def chart_spending_by_category(df_category):
    if df_category.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, max(4, len(df_category) * 0.8)))

    sns.barplot(
        data=df_category,
        x="total_spent",
        y="category_name",
        color=PALETTE["Spending"],
        ax=ax,
        orient="h"
    )

    ax.set_title("Spending by Category", fontsize=14, fontweight="bold")
    ax.set_xlabel("Amount ($)")
    ax.set_ylabel("Category")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f"${val:,.0f}"))
    _apply_dark_style(fig, ax)
    fig.tight_layout()

    return _fig_to_bytes(fig)


def chart_budget_vs_spending(df_budget):
    if df_budget.empty:
        return None

    df_melted = df_budget.melt(
        id_vars="category_name",
        value_vars=["budget", "total_spent"],
        var_name="type",
        value_name="amount"
    )
    df_melted["type"] = df_melted["type"].map({
        "budget": "Budget",
        "total_spent": "Spent"
    })

    fig, ax = plt.subplots(figsize=(10, max(4, len(df_budget) * 0.8)))

    sns.barplot(
        data=df_melted,
        x="amount",
        y="category_name",
        hue="type",
        palette=PALETTE,
        ax=ax,
        orient="h"
    )

    ax.set_title("Budget vs Actual Spending", fontsize=14, fontweight="bold")
    ax.set_xlabel("Amount ($)")
    ax.set_ylabel("Category")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda val, _: f"${val:,.0f}"))
    ax.legend(title="")
    _apply_dark_style(fig, ax)
    fig.tight_layout()

    return _fig_to_bytes(fig)