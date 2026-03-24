import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sustainable Portfolio Optimiser", layout="wide")

st.title("🌱 Sustainable Portfolio Optimiser")
st.caption("Build a personalised two-asset portfolio using return, risk and ESG preferences.")

# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.header("Investor Profile")

persona = st.sidebar.selectbox(
    "Investor type",
    [
        "Balanced Investor",
        "Sustainability-Focused Investor",
        "Return-Seeking Investor",
        "Low-Risk Investor",
    ],
)

persona_defaults = {
    "Balanced Investor": {"gamma": 4.0, "esg_pref": 0.03},
    "Sustainability-Focused Investor": {"gamma": 5.5, "esg_pref": 0.07},
    "Return-Seeking Investor": {"gamma": 2.0, "esg_pref": 0.01},
    "Low-Risk Investor": {"gamma": 8.0, "esg_pref": 0.02},
}

use_manual_preferences = st.sidebar.checkbox("Manually adjust preferences", value=False)

if use_manual_preferences:
    gamma = st.sidebar.slider("Risk aversion (γ)", min_value=0.1, max_value=10.0, value=4.0, step=0.1)
    esg_pref = st.sidebar.slider("ESG preference (λ)", min_value=0.0, max_value=0.10, value=0.03, step=0.005)
else:
    gamma = persona_defaults[persona]["gamma"]
    esg_pref = persona_defaults[persona]["esg_pref"]
    st.sidebar.info(
        f"{persona}: γ = {gamma:.1f}, λ = {esg_pref:.3f}"
    )

st.sidebar.header("Asset Inputs")

asset1_name = st.sidebar.text_input("Asset 1 name", value="Sustainable Infrastructure Fund")
r1 = st.sidebar.number_input("Asset 1 expected return (%)", value=6.4, step=0.1) / 100
sd1 = st.sidebar.number_input("Asset 1 standard deviation (%)", value=10.0, min_value=0.01, step=0.1) / 100
esg1 = st.sidebar.slider("Asset 1 ESG score", min_value=0, max_value=100, value=85, step=1)

asset2_name = st.sidebar.text_input("Asset 2 name", value="Traditional Energy Fund")
r2 = st.sidebar.number_input("Asset 2 expected return (%)", value=11.0, step=0.1) / 100
sd2 = st.sidebar.number_input("Asset 2 standard deviation (%)", value=18.0, min_value=0.01, step=0.1) / 100
esg2 = st.sidebar.slider("Asset 2 ESG score", min_value=0, max_value=100, value=40, step=1)

rho12 = st.sidebar.slider("Correlation", min_value=-1.0, max_value=1.0, value=-0.09, step=0.01)
r_free = st.sidebar.number_input("Risk-free rate (%)", value=2.0, step=0.1) / 100

st.sidebar.header("Portfolio Rules")
allow_leverage = st.sidebar.checkbox("Allow leverage / borrowing", value=False)
exclude_low_esg = st.sidebar.checkbox("Exclude low ESG portfolios", value=False)
esg_floor = st.sidebar.slider("Minimum portfolio ESG score", min_value=0, max_value=100, value=50, step=1)

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
    return np.sqrt(np.maximum(portfolio_variance(w1, sd1, sd2, rho), 0))

def portfolio_esg(w1, esg1, esg2):
    w2 = 1 - w1
    return w1 * esg1 + w2 * esg2

def sharpe_ratio(ret, sd, r_free):
    if sd <= 0:
        return -np.inf
    return (ret - r_free) / sd

def utility(ret, sd, esg_score, gamma, esg_pref):
    return ret - 0.5 * gamma * (sd ** 2) + esg_pref * (esg_score / 100)

# -----------------------------
# Weight grid
# -----------------------------
if allow_leverage:
    weights = np.linspace(-0.5, 1.5, 4001)
else:
    weights = np.linspace(0.0, 1.0, 4001)

returns = np.array([portfolio_return(w, r1, r2) for w in weights])
risks = np.array([portfolio_sd(w, sd1, sd2, rho12) for w in weights])
esg_scores = np.array([portfolio_esg(w, esg1, esg2) for w in weights])
utilities = np.array([utility(ret, sd, esg, gamma, esg_pref) for ret, sd, esg in zip(returns, risks, esg_scores)])
sharpes = np.array([sharpe_ratio(ret, sd, r_free) for ret, sd in zip(returns, risks)])

if exclude_low_esg:
    utilities = np.where(esg_scores < esg_floor, -np.inf, utilities)
    sharpes = np.where(esg_scores < esg_floor, -np.inf, sharpes)

# -----------------------------
# Validity check
# -----------------------------
if np.all(np.isneginf(utilities)):
    st.error("No feasible portfolios remain under the current ESG exclusion rule. Lower the ESG floor or untick the exclusion option.")
    st.stop()

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
if sd_opt_risky > 0:
    y = (ret_opt_risky - r_free) / (gamma * sd_opt_risky**2)
else:
    y = 0.0

if allow_leverage:
    y = min(max(y, 0.0), 1.5)
else:
    y = min(max(y, 0.0), 1.0)

w_rf = 1 - y
w1_complete = y * w1_opt_risky
w2_complete = y * w2_opt_risky

ret_complete = r_free + y * (ret_opt_risky - r_free)
sd_complete = y * sd_opt_risky

if (w1_complete + w2_complete) > 0:
    esg_complete = (w1_complete * esg1 + w2_complete * esg2) / (w1_complete + w2_complete)
else:
    esg_complete = 0.0

# -----------------------------
# Utility breakdown
# -----------------------------
expected_return_component = ret_opt_risky
risk_penalty_component = 0.5 * gamma * (sd_opt_risky**2)
esg_reward_component = esg_pref * (esg_opt_risky / 100)

# -----------------------------
# Explanation text
# -----------------------------
def explain_portfolio():
    higher_weight_asset = asset1_name if w1_opt_risky >= w2_opt_risky else asset2_name
    stronger_esg_asset = asset1_name if esg1 >= esg2 else asset2_name
    higher_return_asset = asset1_name if r1 >= r2 else asset2_name

    text = (
        f"Your recommended risky allocation leans most heavily toward **{higher_weight_asset}**. "
        f"The model combines your risk aversion and ESG preference in one utility function, so the result reflects both financial and sustainability priorities. "
        f"**{stronger_esg_asset}** has the stronger ESG profile, while **{higher_return_asset}** offers the higher expected return."
    )

    if exclude_low_esg:
        text += f" An ESG floor of **{esg_floor}** is active, so lower-ESG portfolios are ruled out."

    if y < 1:
        text += " Part of your final allocation remains in the risk-free asset to reduce overall volatility."
    elif np.isclose(y, 1.0):
        text += " Your final allocation is fully invested in risky assets."
    else:
        text += " Because leverage is enabled, the model recommends borrowing to increase exposure to risky assets."

    return text

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📊 Results", "📈 Frontier", "ℹ️ Portfolio Logic"])

with tab1:
    st.subheader("Recommended Allocation")

    if allow_leverage and y > 1:
        st.warning("Leverage is enabled, so the recommendation includes borrowing to increase exposure to risky assets.")
    else:
        st.caption("Weights show the allocation across the risk-free asset and the two risky funds.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk-free asset", f"{w_rf * 100:.2f}%")
    c2.metric(asset1_name, f"{w1_complete * 100:.2f}%")
    c3.metric(asset2_name, f"{w2_complete * 100:.2f}%")

    c4, c5, c6, c7 = st.columns(4)
    c4.metric("Expected return", f"{ret_complete * 100:.2f}%")
    c5.metric("Risk (standard deviation)", f"{sd_complete * 100:.2f}%")
    c6.metric("Portfolio ESG score", f"{esg_complete:.2f}")
    c7.metric("Utility score", f"{u_opt_risky:.4f}")

    st.markdown("### Risky Portfolio Behind the Recommendation")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric(asset1_name, f"{w1_opt_risky * 100:.2f}%")
    d2.metric(asset2_name, f"{w2_opt_risky * 100:.2f}%")
    d3.metric("Tangency portfolio Sharpe", f"{sharpe_tan:.3f}")
    d4.metric("Risky portfolio ESG", f"{esg_opt_risky:.2f}")

    st.markdown("### Utility Breakdown")
    e1, e2, e3 = st.columns(3)
    e1.metric("Return contribution", f"{expected_return_component:.4f}")
    e2.metric("Risk penalty", f"-{risk_penalty_component:.4f}")
    e3.metric("ESG reward", f"{esg_reward_component:.4f}")

    st.markdown("### Interpretation")
    st.write(explain_portfolio())

with tab2:
    st.subheader("ESG-Efficient Frontier")

    fig1, ax1 = plt.subplots(figsize=(10, 6))

    scatter1 = ax1.scatter(
        risks,
        returns,
        c=esg_scores,
        cmap="YlGn",
        s=22,
        alpha=0.9,
        label="Risky portfolios"
    )

    ax1.scatter(sd1, r1, s=140, marker="o", label=asset1_name)
    ax1.scatter(sd2, r2, s=140, marker="o", label=asset2_name)
    ax1.scatter(sd_tan, ret_tan, s=200, marker="*", label="Tangency portfolio")
    ax1.scatter(sd_opt_risky, ret_opt_risky, s=160, marker="D", label="ESG-optimal risky portfolio")
    ax1.scatter(sd_complete, ret_complete, s=150, marker="X", label="Recommended complete portfolio")
    ax1.scatter(0, r_free, s=130, marker="s", label="Risk-free asset")

    sd_line = np.linspace(0, max(risks) * 1.2, 100)
    if sd_opt_risky > 0:
        ret_line = r_free + ((ret_opt_risky - r_free) / sd_opt_risky) * sd_line
        ax1.plot(sd_line, ret_line, linestyle="--", linewidth=2, label="Allocation line")

    ax1.set_xlabel("Risk (standard deviation)")
    ax1.set_ylabel("Expected return")
    ax1.set_title("Risk-Return Frontier Coloured by ESG Score")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label("Portfolio ESG score")

    st.pyplot(fig1)

    st.markdown("### ESG Trade-Off View")

    fig2, ax2 = plt.subplots(figsize=(10, 6))

    scatter2 = ax2.scatter(
        esg_scores,
        returns,
        c=risks,
        cmap="viridis",
        s=22,
        alpha=0.9,
        label="Risky portfolios"
    )

    ax2.scatter(esg1, r1, s=140, marker="o", label=asset1_name)
    ax2.scatter(esg2, r2, s=140, marker="o", label=asset2_name)
    ax2.scatter(esg_opt_risky, ret_opt_risky, s=160, marker="D", label="ESG-optimal risky portfolio")

    if exclude_low_esg:
        ax2.axvline(esg_floor, linestyle="--", linewidth=2, label=f"ESG floor = {esg_floor}")

    ax2.set_xlabel("Portfolio ESG score")
    ax2.set_ylabel("Expected return")
    ax2.set_title("Return vs ESG Trade-Off")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label("Portfolio risk")

    st.pyplot(fig2)

with tab3:
    st.subheader("Model Setup")

    st.markdown(
        rf"""
        The app evaluates portfolios formed from two risky assets. For each portfolio weight \( w_1 \):

        \[
        E(R_p) = w_1R_1 + (1-w_1)R_2
        \]

        \[
        \sigma_p = \sqrt{{w_1^2\sigma_1^2 + (1-w_1)^2\sigma_2^2 + 2w_1(1-w_1)\rho_{{12}}\sigma_1\sigma_2}}
        \]

        \[
        ESG_p = w_1ESG_1 + (1-w_1)ESG_2
        \]

        The app uses an ESG-adjusted utility function:

        \[
        U = E(R_p) - \frac{{\gamma}}{{2}}\sigma_p^2 + \lambda \left(\frac{{ESG_p}}{{100}}\right)
        \]

        where \( \gamma \) measures risk aversion and \( \lambda \) measures ESG preference strength.

        The risky portfolio is chosen by maximising this utility across feasible portfolio weights.
        The final recommendation then combines that risky portfolio with the risk-free asset.

        **Current investor type:** {persona}  
        **Current parameters:** \( \gamma = {gamma:.1f} \), \( \lambda = {esg_pref:.3f} \)
        """
    )
