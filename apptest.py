import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sustainable Portfolio Optimizer", layout="wide")

st.title("🌱 Sustainable Portfolio Optimizer")
st.caption("Optimise a two-asset portfolio using return, risk, and ESG preferences.")

# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.header("Asset Inputs")

asset1_name = st.sidebar.text_input("Asset 1 Name", value="Sustainable Infrastructure Fund")
r1 = st.sidebar.number_input("Asset 1 Expected Return (%)", value=7.0, step=0.1) / 100
sd1 = st.sidebar.number_input("Asset 1 Standard Deviation (%)", value=10.0, min_value=0.01, step=0.1) / 100
esg1 = st.sidebar.slider("Asset 1 ESG Score", min_value=0, max_value=100, value=85, step=1)

asset2_name = st.sidebar.text_input("Asset 2 Name", value="Traditional Energy Fund")
r2 = st.sidebar.number_input("Asset 2 Expected Return (%)", value=11.0, step=0.1) / 100
sd2 = st.sidebar.number_input("Asset 2 Standard Deviation (%)", value=18.0, min_value=0.01, step=0.1) / 100
esg2 = st.sidebar.slider("Asset 2 ESG Score", min_value=0, max_value=100, value=40, step=1)

rho12 = st.sidebar.slider("Correlation", min_value=-1.0, max_value=1.0, value=0.20, step=0.01)
r_free = st.sidebar.number_input("Risk-Free Rate (%)", value=2.0, step=0.1) / 100

st.sidebar.header("Investor Preferences")
gamma = st.sidebar.slider("Risk Aversion (γ)", min_value=0.1, max_value=10.0, value=4.0, step=0.1)
esg_pref = st.sidebar.slider("ESG Preference (λ)", min_value=0.0, max_value=0.10, value=0.03, step=0.005)

allow_leverage = st.sidebar.checkbox("Allow leverage / borrowing", value=False)

# -----------------------------
# Portfolio functions
# -----------------------------
def portfolio_return(w1, r1, r2):
    w2 = 1 - w1
    return w1 * r1 + w2 * r2

def portfolio_variance(w1, sd1, sd2, rho):
    w2 = 1 - w1
    return (w1**2) * (sd1**2) + (w2**2) * (sd2**2) + 2 * w1 * w2 * rho * sd1 * sd2

def portfolio_sd(w1, sd1, sd2, rho):
    var = portfolio_variance(w1, sd1, sd2, rho)
    return np.sqrt(max(var, 0))

def portfolio_esg(w1, esg1, esg2):
    w2 = 1 - w1
    return w1 * esg1 + w2 * esg2

def sharpe_ratio(ret, sd, r_free):
    if sd <= 0:
        return -np.inf
    return (ret - r_free) / sd

def utility(ret, sd, esg_score, gamma, esg_pref):
    """
    ESG-adjusted utility:
    U = E[R] - (gamma / 2) * sigma^2 + lambda * (ESG / 100)
    ESG is scaled to 0-1 so it is comparable in magnitude.
    """
    return ret - 0.5 * gamma * (sd ** 2) + esg_pref * (esg_score / 100)

# -----------------------------
# Weight grid
# -----------------------------
if allow_leverage:
    weights = np.linspace(-0.5, 1.5, 2001)
else:
    weights = np.linspace(0.0, 1.0, 2001)

returns = np.array([portfolio_return(w, r1, r2) for w in weights])
risks = np.array([portfolio_sd(w, sd1, sd2, rho12) for w in weights])
esg_scores = np.array([portfolio_esg(w, esg1, esg2) for w in weights])
utilities = np.array([utility(ret, sd, esg, gamma, esg_pref) for ret, sd, esg in zip(returns, risks, esg_scores)])
sharpes = np.array([sharpe_ratio(ret, sd, r_free) for ret, sd in zip(returns, risks)])

# -----------------------------
# Tangency portfolio
# -----------------------------
tangency_idx = np.argmax(sharpes)
w1_tan = weights[tangency_idx]
w2_tan = 1 - w1_tan

ret_tan = returns[tangency_idx]
sd_tan = risks[tangency_idx]
esg_tan = esg_scores[tangency_idx]
sharpe_tan = sharpes[tangency_idx]

# -----------------------------
# ESG-optimal risky portfolio
# -----------------------------
optimal_idx = np.argmax(utilities)
w1_opt_risky = weights[optimal_idx]
w2_opt_risky = 1 - w1_opt_risky

ret_opt_risky = returns[optimal_idx]
sd_opt_risky = risks[optimal_idx]
esg_opt_risky = esg_scores[optimal_idx]
u_opt_risky = utilities[optimal_idx]

# -----------------------------
# Complete portfolio with risk-free asset
# -----------------------------
# Keep same educational structure as lecturer base code:
# y = share invested in the risky portfolio
if sd_opt_risky > 0:
    y = (ret_opt_risky - r_free) / (gamma * sd_opt_risky**2)
else:
    y = 0.0

if not allow_leverage:
    y = min(max(y, 0.0), 1.0)

w_rf = 1 - y
w1_complete = y * w1_opt_risky
w2_complete = y * w2_opt_risky

ret_complete = r_free + y * (ret_opt_risky - r_free)
sd_complete = abs(y) * sd_opt_risky
esg_complete = y * esg_opt_risky  # risk-free asset assumed ESG-neutral

# -----------------------------
# Helper text
# -----------------------------
def explain_portfolio():
    higher_weight_asset = asset1_name if w1_complete >= w2_complete else asset2_name
    stronger_esg_asset = asset1_name if esg1 >= esg2 else asset2_name
    higher_return_asset = asset1_name if r1 >= r2 else asset2_name

    explanation = (
        f"The recommended allocation leans most heavily toward **{higher_weight_asset}**. "
        f"Your chosen risk aversion (γ = {gamma:.1f}) shapes how much risk is acceptable, "
        f"while your ESG preference (λ = {esg_pref:.3f}) rewards portfolios with stronger sustainability characteristics. "
        f"In this case, **{stronger_esg_asset}** contributes more positively on ESG grounds, "
        f"while **{higher_return_asset}** offers the stronger expected return profile."
    )

    if w_rf > 0:
        explanation += (
            f" A share of the portfolio remains in the risk-free asset, which reduces overall volatility."
        )
    elif w_rf < 0:
        explanation += (
            f" The negative weight in the risk-free asset indicates borrowing to lever the risky portfolio."
        )

    return explanation

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📊 Results", "📈 Frontier", "ℹ️ Portfolio Logic"])

with tab1:
    st.subheader("Recommended Portfolio")

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk-Free Asset", f"{w_rf * 100:.2f}%")
    c2.metric(asset1_name, f"{w1_complete * 100:.2f}%")
    c3.metric(asset2_name, f"{w2_complete * 100:.2f}%")

    c4, c5, c6, c7 = st.columns(4)
    c4.metric("Expected Return", f"{ret_complete * 100:.2f}%")
    c5.metric("Risk (Std Dev)", f"{sd_complete * 100:.2f}%")
    c6.metric("Portfolio ESG Score", f"{esg_complete:.2f}")
    c7.metric("Utility Score", f"{u_opt_risky:.4f}")

    st.markdown("### Risky Portfolio Behind the Recommendation")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric(asset1_name, f"{w1_opt_risky * 100:.2f}%")
    d2.metric(asset2_name, f"{w2_opt_risky * 100:.2f}%")
    d3.metric("Tangency Portfolio Sharpe", f"{sharpe_tan:.3f}")
    d4.metric("Risky Portfolio ESG", f"{esg_opt_risky:.2f}")

    st.markdown("### Interpretation")
    st.write(explain_portfolio())

    if not allow_leverage and (y == 0 or y == 1):
        st.info(
            "Leverage is turned off, so the share invested in the risky portfolio is capped between 0% and 100%."
        )

with tab2:
    st.subheader("Efficient Frontier and ESG Profile")

    fig, ax = plt.subplots(figsize=(10, 6))

    scatter = ax.scatter(
        risks,
        returns,
        c=esg_scores,
        cmap="YlGn",
        s=20,
        alpha=0.85,
        label="Risky Portfolios"
    )

    # Highlight the two assets
    ax.scatter(sd1, r1, color="blue", s=120, marker="o", label=asset1_name)
    ax.scatter(sd2, r2, color="purple", s=120, marker="o", label=asset2_name)

    # Tangency portfolio
    ax.scatter(sd_tan, ret_tan, color="red", s=180, marker="*", label="Tangency Portfolio")

    # ESG-optimal risky portfolio
    ax.scatter(sd_opt_risky, ret_opt_risky, color="orange", s=160, marker="D", label="ESG-Optimal Risky Portfolio")

    # Complete portfolio
    ax.scatter(sd_complete, ret_complete, color="black", s=150, marker="X", label="Recommended Complete Portfolio")

    # Capital allocation line based on ESG-optimal risky portfolio
    sd_line = np.linspace(0, max(risks) * 1.2, 100)
    if sd_opt_risky > 0:
        ret_line = r_free + ((ret_opt_risky - r_free) / sd_opt_risky) * sd_line
        ax.plot(sd_line, ret_line, linestyle="--", linewidth=2, label="Allocation Line")
    ax.scatter(0, r_free, color="green", s=120, marker="s", label="Risk-Free Asset")

    ax.set_xlabel("Risk (Standard Deviation)")
    ax.set_ylabel("Expected Return")
    ax.set_title("Risk-Return Frontier Coloured by ESG Score")
    ax.grid(True, alpha=0.3)
    ax.legend()

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Portfolio ESG Score")

    st.pyplot(fig)

with tab3:
    st.subheader("Model Setup")

    st.markdown(
        r"""
        The app evaluates portfolios formed from the two risky assets. For each portfolio weight \(w_1\):

        \[
        E(R_p) = w_1R_1 + (1-w_1)R_2
        \]

        \[
        \sigma_p = \sqrt{w_1^2\sigma_1^2 + (1-w_1)^2\sigma_2^2 + 2w_1(1-w_1)\rho_{12}\sigma_1\sigma_2}
        \]

        \[
        ESG_p = w_1 ESG_1 + (1-w_1) ESG_2
        \]

        The ESG-adjusted utility is:

        \[
        U = E(R_p) - \frac{\gamma}{2}\sigma_p^2 + \lambda \cdot \left(\frac{ESG_p}{100}\right)
        \]

        where:

        - \( \gamma \) is risk aversion
        - \( \lambda \) is ESG preference strength

        The recommended risky portfolio is the one that maximises this utility.
        """
    )
