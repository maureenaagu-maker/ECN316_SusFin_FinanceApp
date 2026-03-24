import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sustainable Portfolio Optimiser", layout="wide")

st.title("🌱 Sustainable Portfolio Optimiser")
st.caption("Build a personalised two-asset portfolio using return, risk and sustainability preferences.")

# -----------------------------
# Questionnaire mapping
# -----------------------------
def get_profile_from_answers(return_goal, risk_feeling, sustainability_priority, cash_need, strict_sustainability):
    score_balanced = 0
    score_sustainability = 0
    score_return = 0
    score_lowrisk = 0

    if return_goal == "Steady growth":
        score_balanced += 2
        score_lowrisk += 1
    elif return_goal == "Strong growth":
        score_return += 2
        score_balanced += 1
    elif return_goal == "Highest growth possible":
        score_return += 3
    elif return_goal == "Capital preservation":
        score_lowrisk += 3

    if risk_feeling == "I am comfortable with some ups and downs":
        score_balanced += 2
    elif risk_feeling == "I can tolerate large swings for higher returns":
        score_return += 3
    elif risk_feeling == "I prefer stable outcomes, even if returns are lower":
        score_lowrisk += 3
    elif risk_feeling == "I want a balance between stability and growth":
        score_balanced += 3

    if sustainability_priority == "It matters a little":
        score_balanced += 1
    elif sustainability_priority == "It matters a lot":
        score_sustainability += 2
        score_balanced += 1
    elif sustainability_priority == "It is essential":
        score_sustainability += 4
    elif sustainability_priority == "Returns matter more to me":
        score_return += 2

    if cash_need == "I may need this money soon":
        score_lowrisk += 3
    elif cash_need == "I can leave it invested for a few years":
        score_balanced += 2
    elif cash_need == "I can leave it invested for a long time":
        score_return += 2
        score_sustainability += 1

    if strict_sustainability == "Yes, avoid lower-ESG portfolios":
        score_sustainability += 3
    else:
        score_balanced += 1
        score_return += 1

    scores = {
        "Balanced Investor": score_balanced,
        "Sustainability-Focused Investor": score_sustainability,
        "Return-Seeking Investor": score_return,
        "Low-Risk Investor": score_lowrisk,
    }

    return max(scores, key=scores.get)


persona_defaults = {
    "Balanced Investor": {"risk_aversion": 4.0, "esg_preference": 0.03},
    "Sustainability-Focused Investor": {"risk_aversion": 5.5, "esg_preference": 0.07},
    "Return-Seeking Investor": {"risk_aversion": 2.0, "esg_preference": 0.01},
    "Low-Risk Investor": {"risk_aversion": 8.0, "esg_preference": 0.02},
}

# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.header("Investor Profile")
st.sidebar.caption("Answer a few quick questions so a suitable investor profile can be suggested.")

return_goal = st.sidebar.selectbox(
    "1) What sort of return are you hoping for?",
    [
        "Steady growth",
        "Strong growth",
        "Highest growth possible",
        "Capital preservation",
    ],
)

risk_feeling = st.sidebar.selectbox(
    "2) How do you feel about investment ups and downs?",
    [
        "I want a balance between stability and growth",
        "I am comfortable with some ups and downs",
        "I can tolerate large swings for higher returns",
        "I prefer stable outcomes, even if returns are lower",
    ],
)

sustainability_priority = st.sidebar.selectbox(
    "3) How important is sustainability when choosing investments?",
    [
        "Returns matter more to me",
        "It matters a little",
        "It matters a lot",
        "It is essential",
    ],
)

cash_need = st.sidebar.selectbox(
    "4) When might you need this money back?",
    [
        "I may need this money soon",
        "I can leave it invested for a few years",
        "I can leave it invested for a long time",
    ],
)

strict_sustainability = st.sidebar.selectbox(
    "5) Would you want to avoid lower-ESG portfolios?",
    [
        "No, I am open to all portfolios",
        "Yes, avoid lower-ESG portfolios",
    ],
)

persona = get_profile_from_answers(
    return_goal,
    risk_feeling,
    sustainability_priority,
    cash_need,
    strict_sustainability,
)

default_risk_aversion = persona_defaults[persona]["risk_aversion"]
default_esg_preference = persona_defaults[persona]["esg_preference"]

st.sidebar.success(f"Suggested investor type: {persona}")

use_manual_preferences = st.sidebar.checkbox("Manually adjust preferences", value=False)

if use_manual_preferences:
    risk_aversion = st.sidebar.slider(
        "Risk Aversion",
        min_value=0.1,
        max_value=10.0,
        value=float(default_risk_aversion),
        step=0.1,
        help="Higher values place more emphasis on reducing risk.",
    )
    esg_preference = st.sidebar.slider(
        "ESG Preference",
        min_value=0.0,
        max_value=0.10,
        value=float(default_esg_preference),
        step=0.005,
        help="Higher values place more emphasis on ESG score in the recommendation.",
    )
else:
    risk_aversion = default_risk_aversion
    esg_preference = default_esg_preference
    st.sidebar.info(
        f"{persona}\n\nRisk Aversion: {risk_aversion:.1f}\n\nESG Preference: {esg_preference:.3f}"
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

rho12 = st.sidebar.slider(
    "Correlation between the two assets",
    min_value=-1.0,
    max_value=1.0,
    value=-0.09,
    step=0.01,
    help="This shows how closely the two assets move together.",
)

r_free = st.sidebar.number_input("Risk-free rate (%)", value=2.0, step=0.1) / 100

st.sidebar.header("Portfolio Rules")
allow_leverage = st.sidebar.checkbox("Allow borrowing to increase investment exposure", value=False)

exclude_low_esg = st.sidebar.checkbox(
    "Set a minimum ESG score for the portfolio",
    value=(strict_sustainability == "Yes, avoid lower-ESG portfolios"),
)

esg_floor = st.sidebar.slider(
    "Minimum portfolio ESG score",
    min_value=0,
    max_value=100,
    value=50,
    step=1,
    help="This is the lowest average ESG score your combined portfolio is allowed to have.",
)

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


def utility(ret, sd, esg_score, risk_aversion, esg_preference):
    return ret - 0.5 * risk_aversion * (sd**2) + esg_preference * (esg_score / 100)


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
utilities = np.array(
    [utility(ret, sd, esg, risk_aversion, esg_preference) for ret, sd, esg in zip(returns, risks, esg_scores)]
)
sharpes = np.array([sharpe_ratio(ret, sd, r_free) for ret, sd in zip(returns, risks)])

if exclude_low_esg:
    utilities = np.where(esg_scores < esg_floor, -np.inf, utilities)
    sharpes = np.where(esg_scores < esg_floor, -np.inf, sharpes)

if np.all(np.isneginf(utilities)):
    st.error("No portfolio meets your current ESG rule. Try lowering the minimum portfolio ESG score.")
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
# Optimal risky portfolio
# -----------------------------
optimal_idx = np.argmax(utilities)
w1_opt_risky = weights[optimal_idx]
w2_opt_risky = 1 - w1_opt_risky

ret_opt_risky = returns[optimal_idx]
sd_opt_risky = risks[optimal_idx]
esg_opt_risky = esg_scores[optimal_idx]
u_opt_risky = utilities[optimal_idx]

# -----------------------------
# Final recommended portfolio
# -----------------------------
if sd_opt_risky > 0:
    y = (ret_opt_risky - r_free) / (risk_aversion * sd_opt_risky**2)
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
risk_penalty_component = 0.5 * risk_aversion * (sd_opt_risky**2)
esg_reward_component = esg_preference * (esg_opt_risky / 100)

# -----------------------------
# Explanation text
# -----------------------------
def explain_portfolio():
    lead_asset = asset1_name if w1_opt_risky >= w2_opt_risky else asset2_name
    stronger_esg_asset = asset1_name if esg1 >= esg2 else asset2_name
    higher_return_asset = asset1_name if r1 >= r2 else asset2_name

    text = (
        f"This portfolio leans most heavily toward **{lead_asset}**. "
        f"Among the two options, **{stronger_esg_asset}** has the stronger ESG profile, "
        f"while **{higher_return_asset}** offers the higher expected return. "
        f"The recommendation balances those trade-offs using your investor profile."
    )

    if exclude_low_esg:
        text += f" A minimum portfolio ESG score of **{esg_floor}** is also being applied."

    if y < 1:
        text += " Part of the allocation remains in the risk-free asset to help reduce overall volatility."
    elif np.isclose(y, 1.0):
        text += " The allocation is fully invested in the two funds."
    else:
        text += " Because borrowing is enabled, the recommendation uses more than the starting amount."

    return text


# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Results", "📈 ESG-Efficient Frontier", "🌍 ESG Trade-Off", "ℹ️ How It Works"]
)

with tab1:
    st.subheader("Your Recommended Portfolio")
    st.caption("Based on your return, risk and ESG preferences.")

    top1, top2, top3 = st.columns(3)
    top1.metric(asset1_name, f"{w1_complete * 100:.2f}%")
    top2.metric(asset2_name, f"{w2_complete * 100:.2f}%")
    top3.metric("Risk-free asset", f"{w_rf * 100:.2f}%")

    st.markdown("### Portfolio Snapshot")

    snap1, snap2, snap3 = st.columns(3)

    card_style = """
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 28px 20px;
        border-radius: 22px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.18);
        min-height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    """

    label_style = """
        color: white;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 10px;
    """

    value_style = """
        color: #ff4b4b;
        font-size: 34px;
        font-weight: 700;
        line-height: 1.1;
    """

    with snap1:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="{label_style}">Expected Return</div>
                <div style="{value_style}">{ret_complete * 100:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with snap2:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="{label_style}">Risk Level</div>
                <div style="{value_style}">{sd_complete * 100:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with snap3:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="{label_style}">Portfolio ESG Score</div>
                <div style="{value_style}">{esg_complete:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    lower_left, lower_right = st.columns([1, 1], gap="large")

    with lower_left:
        if allow_leverage and y > 1:
            st.warning("This recommendation uses borrowing to increase investment exposure.")
        elif np.isclose(w_rf, 0.0):
            st.info("This recommendation is FULLY invested in the two funds.")
        elif w_rf > 0:
            st.info("Part of the portfolio remains in the risk-free asset to help reduce volatility.")

        st.markdown("### Recommendation Rationale")
        st.write(explain_portfolio())

    with lower_right:
        st.markdown("### Portfolio Balance")
        bal1, bal2, bal3 = st.columns(3)
        bal1.metric("Return Contribution", f"{expected_return_component:.4f}")
        bal2.metric("Risk Adjustment", f"-{risk_penalty_component:.4f}")
        bal3.metric("ESG Contribution", f"{esg_reward_component:.4f}")

        with st.expander("See the underlying risky portfolio mix"):
            mix1, mix2 = st.columns(2)
            mix3, mix4 = st.columns(2)

            mix1.metric(asset1_name, f"{w1_opt_risky * 100:.2f}%")
            mix2.metric(asset2_name, f"{w2_opt_risky * 100:.2f}%")
            mix3.metric("Tangency portfolio Sharpe ratio", f"{sharpe_tan:.3f}")
            mix4.metric("Optimal risky portfolio ESG score", f"{esg_opt_risky:.2f}")

with tab2:
    st.subheader("ESG-Efficient Frontier Visualisation")

    fig1, ax1 = plt.subplots(figsize=(10, 6))

    scatter1 = ax1.scatter(
        risks,
        returns,
        c=esg_scores,
        cmap="YlGn",
        s=22,
        alpha=0.9,
        label="Possible risky portfolios",
    )

    ax1.scatter(
    sd1, r1,
    edgecolors="black",
    linewidths=0.8,
    s=140,
    marker="o",
    label=asset1_name,
    zorder=3
)

ax1.scatter(
    sd2, r2,
    edgecolors="black",
    linewidths=0.8,
    s=140,
    marker="o",
    label=asset2_name,
    zorder=3
)

ax1.scatter(
    sd_tan, ret_tan,
    edgecolors="black",
    linewidths=0.8,
    s=220,
    marker="*",
    label="Tangency Portfolio",
    zorder=5
)

ax1.scatter(
    sd_complete,
    ret_complete,
    color="black",
    edgecolors="red",
    linewidths=0.8,
    s=170,
    marker="X",
    label="Your optimal portfolio",
    zorder=6
)

ax1.scatter(
    0, r_free,
    s=140,
    marker="s",
    label="Risk-free asset",
    zorder=4
)

    sd_line = np.linspace(0, max(risks) * 1.2, 100)
    if sd_opt_risky > 0:
        ret_line = r_free + ((ret_opt_risky - r_free) / sd_opt_risky) * sd_line
        ax1.plot(sd_line, ret_line, linestyle="--", linewidth=2, label="Capital Market Line (CML)")

    ax1.set_xlabel("Risk (standard deviation)")
    ax1.set_ylabel("Expected return")
    ax1.set_title("Risk-Return Frontier Coloured by ESG Score")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label("Portfolio ESG score")

    st.pyplot(fig1)
    st.caption(
        "This chart shows all possible risky portfolios formed from the two funds. "
        "The final recommendation may sit away from the risky frontier because it can include the risk-free asset."
    )
    st.markdown(
        "**Marker Guide:** circles = Individual assets, "
        "star = The best risky mix before adding cash, "
        "X = Your final recommended portfolio, "
        "square = The risk-free asset, "
        "dashed line = Capital Market Line showing varying allocations of the risk-free asset and risky investin."
    )

with tab3:
    st.subheader("ESG Trade-Off")

    fig2, ax2 = plt.subplots(figsize=(10, 6))

    scatter2 = ax2.scatter(
        esg_scores,
        returns,
        c=risks,
        cmap="viridis",
        s=22,
        alpha=0.9,
        label="Possible risky portfolios",
    )

    ax2.scatter(esg1, r1, edgecolors="black", linewidths=0.8, s=140, marker="o", label=asset1_name)
    ax2.scatter(esg2, r2, edgecolors="black", linewidths=0.8, s=140, marker="o", label=asset2_name)
    ax2.scatter(
        esg_complete,
        ret_complete,
        color="black",
        edgecolors="red",
        linewidths=0.8,
        s=170,
        marker="X",
        label="Your optimal portfolio",
    )

    if exclude_low_esg:
        ax2.axvline(esg_floor, linestyle="--", linewidth=2, label=f"Minimum ESG score = {esg_floor}")

    ax2.set_xlabel("Portfolio ESG score")
    ax2.set_ylabel("Expected return")
    ax2.set_title("Expected Return vs ESG Score")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label("Portfolio risk")

    st.pyplot(fig2)
    st.caption(
        "This chart shows the trade-off between expected return and ESG score across possible risky portfolios."
    )

    if exclude_low_esg:
        st.markdown(
            "**Marker Guide:** circles = Individual assets, "
            "X = Your final recommended portfolio, "
            "vertical dashed line = The minimum ESG score rule."
        )
    else:
        st.markdown(
            "**Marker Guide:** circles = Individual assets, "
            "X = Your final recommended portfolio."
        )

with tab4:
    st.subheader("How It Works")

    st.markdown(
        f"""
This compares all possible portfolios built from two risky assets.

Each portfolio is assessed using:
- expected return
- overall risk
- ESG score

The final recommendation is based on the investor profile suggested by your questionnaire answers.

**Your current investor type:** {persona}  
**Current risk aversion:** {risk_aversion:.1f}  
**Current ESG preference:** {esg_preference:.3f}

If you turn on the minimum ESG rule, any portfolio whose average ESG score falls below your chosen threshold is removed.
        """
    )

