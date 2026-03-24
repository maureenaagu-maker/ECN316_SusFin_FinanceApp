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

    if strict_sustainability == "Yes, avoid lower-sustainability portfolios":
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
    "Balanced Investor": {"risk_level": 4.0, "sustainability_weight": 0.03},
    "Sustainability-Focused Investor": {"risk_level": 5.5, "sustainability_weight": 0.07},
    "Return-Seeking Investor": {"risk_level": 2.0, "sustainability_weight": 0.01},
    "Low-Risk Investor": {"risk_level": 8.0, "sustainability_weight": 0.02},
}

# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.header("Investor Profile")
st.sidebar.caption("Answer a few quick questions so the app can suggest a suitable investor profile.")

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
    "5) Would you want the app to avoid lower-sustainability portfolios?",
    [
        "No, I am open to all portfolios",
        "Yes, avoid lower-sustainability portfolios",
    ],
)

persona = get_profile_from_answers(
    return_goal,
    risk_feeling,
    sustainability_priority,
    cash_need,
    strict_sustainability,
)

default_risk_level = persona_defaults[persona]["risk_level"]
default_sustainability_weight = persona_defaults[persona]["sustainability_weight"]

st.sidebar.success(f"Suggested investor type: {persona}")

use_manual_preferences = st.sidebar.checkbox("Adjust profile settings manually", value=False)

if use_manual_preferences:
    risk_level = st.sidebar.slider(
        "How cautious or adventurous are you?",
        min_value=0.1,
        max_value=10.0,
        value=float(default_risk_level),
        step=0.1,
        help="Higher values make the app favour lower-risk portfolios.",
    )
    sustainability_weight = st.sidebar.slider(
        "How strongly should sustainability influence the recommendation?",
        min_value=0.0,
        max_value=0.10,
        value=float(default_sustainability_weight),
        step=0.005,
        help="Higher values make the app place more weight on stronger sustainability scores.",
    )
else:
    risk_level = default_risk_level
    sustainability_weight = default_sustainability_weight
    st.sidebar.info(
        f"{persona}\n\nRisk setting: {risk_level:.1f}\n\nSustainability setting: {sustainability_weight:.3f}"
    )

st.sidebar.header("Asset Inputs")

asset1_name = st.sidebar.text_input("Asset 1 name", value="Sustainable Infrastructure Fund")
r1 = st.sidebar.number_input("Asset 1 expected return (%)", value=6.4, step=0.1) / 100
sd1 = st.sidebar.number_input("Asset 1 standard deviation (%)", value=10.0, min_value=0.01, step=0.1) / 100
esg1 = st.sidebar.slider("Asset 1 sustainability score", min_value=0, max_value=100, value=85, step=1)

asset2_name = st.sidebar.text_input("Asset 2 name", value="Traditional Energy Fund")
r2 = st.sidebar.number_input("Asset 2 expected return (%)", value=11.0, step=0.1) / 100
sd2 = st.sidebar.number_input("Asset 2 standard deviation (%)", value=18.0, min_value=0.01, step=0.1) / 100
esg2 = st.sidebar.slider("Asset 2 sustainability score", min_value=0, max_value=100, value=40, step=1)

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
    "Set a minimum sustainability score for the portfolio",
    value=(strict_sustainability == "Yes, avoid lower-sustainability portfolios"),
)

sustainability_floor = st.sidebar.slider(
    "Minimum sustainability score for your portfolio",
    min_value=0,
    max_value=100,
    value=50,
    step=1,
    help="This sets the lowest average sustainability score your combined portfolio is allowed to have.",
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

def utility(ret, sd, esg_score, risk_level, sustainability_weight):
    return ret - 0.5 * risk_level * (sd ** 2) + sustainability_weight * (esg_score / 100)

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
    [utility(ret, sd, esg, risk_level, sustainability_weight) for ret, sd, esg in zip(returns, risks, esg_scores)]
)
sharpes = np.array([sharpe_ratio(ret, sd, r_free) for ret, sd in zip(returns, risks)])

if exclude_low_esg:
    utilities = np.where(esg_scores < sustainability_floor, -np.inf, utilities)
    sharpes = np.where(esg_scores < sustainability_floor, -np.inf, sharpes)

if np.all(np.isneginf(utilities)):
    st.error("No portfolio meets your current sustainability rule. Try lowering the minimum sustainability score.")
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
    y = (ret_opt_risky - r_free) / (risk_level * sd_opt_risky**2)
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
risk_penalty_component = 0.5 * risk_level * (sd_opt_risky**2)
esg_reward_component = sustainability_weight * (esg_opt_risky / 100)

# -----------------------------
# Explanation text
# -----------------------------
def explain_portfolio():
    higher_weight_asset = asset1_name if w1_opt_risky >= w2_opt_risky else asset2_name
    stronger_esg_asset = asset1_name if esg1 >= esg2 else asset2_name
    higher_return_asset = asset1_name if r1 >= r2 else asset2_name

    text = (
        f"Your recommended risky allocation leans most heavily toward **{higher_weight_asset}**. "
        f"The app combines your comfort with risk and your sustainability priorities into one recommendation, "
        f"so the result reflects both financial and ethical preferences. "
        f"**{stronger_esg_asset}** has the stronger sustainability profile, while **{higher_return_asset}** offers the higher expected return."
    )

    if exclude_low_esg:
        text += f" A minimum sustainability score of **{sustainability_floor}** is active, so lower-scoring portfolios are excluded."

    if y < 1:
        text += " Part of your final allocation remains in the risk-free asset to help reduce overall volatility."
    elif np.isclose(y, 1.0):
        text += " Your final allocation is fully invested in risky assets."
    else:
        text += " Because borrowing is enabled, the app recommends increasing exposure beyond your starting capital."

    return text

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Results", "📈 ESG-Efficient Frontier", "🌍 Sustainability Trade-Off", "ℹ️ How the App Works"]
)

with tab1:
    st.subheader("Recommended Allocation")

    if allow_leverage and y > 1:
        st.warning("Borrowing is enabled, so the recommendation includes investing more than your starting amount.")
    else:
        st.caption("These weights show how the app splits your money between the risk-free asset and the two funds.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk-free asset", f"{w_rf * 100:.2f}%")
    c2.metric(asset1_name, f"{w1_complete * 100:.2f}%")
    c3.metric(asset2_name, f"{w2_complete * 100:.2f}%")

    c4, c5, c6, c7 = st.columns(4)
    c4.metric("Expected return", f"{ret_complete * 100:.2f}%")
    c5.metric("Risk (standard deviation)", f"{sd_complete * 100:.2f}%")
    c6.metric("Portfolio sustainability score", f"{esg_complete:.2f}")
    c7.metric("Overall portfolio score", f"{u_opt_risky:.4f}")

    st.markdown("### Recommended Risky Mix")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric(asset1_name, f"{w1_opt_risky * 100:.2f}%")
    d2.metric(asset2_name, f"{w2_opt_risky * 100:.2f}%")
    d3.metric("Tangency portfolio Sharpe ratio", f"{sharpe_tan:.3f}")
    d4.metric("Risky portfolio sustainability score", f"{esg_opt_risky:.2f}")

    st.markdown("### What is driving the recommendation?")
    e1, e2, e3 = st.columns(3)
    e1.metric("Return contribution", f"{expected_return_component:.4f}")
    e2.metric("Risk reduction term", f"-{risk_penalty_component:.4f}")
    e3.metric("Sustainability contribution", f"{esg_reward_component:.4f}")

    st.markdown("### Plain-English Interpretation")
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
        label="Possible risky portfolios"
    )

    ax1.scatter(sd1, r1, s=140, marker="o", label=asset1_name)
    ax1.scatter(sd2, r2, s=140, marker="o", label=asset2_name)
    ax1.scatter(sd_tan, ret_tan, s=200, marker="*", label="Tangency portfolio")
    ax1.scatter(sd_opt_risky, ret_opt_risky, s=160, marker="D", label="Recommended risky portfolio")
    ax1.scatter(sd_complete, ret_complete, s=150, marker="X", label="Final recommended portfolio")
    ax1.scatter(0, r_free, s=130, marker="s", label="Risk-free asset")

    sd_line = np.linspace(0, max(risks) * 1.2, 100)
    if sd_opt_risky > 0:
        ret_line = r_free + ((ret_opt_risky - r_free) / sd_opt_risky) * sd_line
        ax1.plot(sd_line, ret_line, linestyle="--", linewidth=2, label="Allocation line")

    ax1.set_xlabel("Risk (standard deviation)")
    ax1.set_ylabel("Expected return")
    ax1.set_title("Risk-Return Frontier Coloured by Sustainability Score")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label("Portfolio sustainability score")

    st.pyplot(fig1)

with tab3:
    st.subheader("Sustainability Trade-Off")

    fig2, ax2 = plt.subplots(figsize=(10, 6))

    scatter2 = ax2.scatter(
        esg_scores,
        returns,
        c=risks,
        cmap="viridis",
        s=22,
        alpha=0.9,
        label="Possible risky portfolios"
    )

    ax2.scatter(esg1, r1, s=140, marker="o", label=asset1_name)
    ax2.scatter(esg2, r2, s=140, marker="o", label=asset2_name)
    ax2.scatter(esg_opt_risky, ret_opt_risky, s=160, marker="D", label="Recommended risky portfolio")

    if exclude_low_esg:
        ax2.axvline(sustainability_floor, linestyle="--", linewidth=2, label=f"Minimum sustainability score = {sustainability_floor}")

    ax2.set_xlabel("Portfolio sustainability score")
    ax2.set_ylabel("Expected return")
    ax2.set_title("Expected Return vs Sustainability")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label("Portfolio risk")

    st.pyplot(fig2)

with tab4:
    st.subheader("How the App Works")

    st.markdown(
        f"""
This app compares possible portfolios built from two risky assets.

It then scores each portfolio using three things:

- expected return
- overall risk
- sustainability score

The recommendation is based on the investor profile suggested by your questionnaire answers.

**Your current investor type:** {persona}  
**Current risk setting:** {risk_level:.1f}  
**Current sustainability setting:** {sustainability_weight:.3f}

If you turn on the minimum sustainability rule, the app removes any portfolio whose average sustainability score falls below your chosen threshold.
        """
    )
