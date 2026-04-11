import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="MyGreenPortfolio", layout="wide")

st.markdown("<h1 style='margin-bottom:0;'>🌱 MyGreenPortfolio</h1>", unsafe_allow_html=True)

st.markdown(
    "<p style='font-size:17px; margin-top:0; color:#A0A0A0;'>Sustainable Portfolio Optimiser</p>",
    unsafe_allow_html=True
)

st.caption("Build a personalised two-asset portfolio using return, risk, sustainability and climate preferences.")

# ------------------------------------------------------------
# Styling
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        color: #ff4b4b !important;
    }
    [data-testid="stMetricDelta"] {
        color: #ff4b4b !important;
    }
    .small-note {
        font-size: 0.92rem;
        opacity: 0.88;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Questionnaire mapping
# ------------------------------------------------------------
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


def get_profile_from_preferences(risk_aversion, esg_preference):
    if esg_preference >= 0.06:
        return "Sustainability-Focused Investor"
    elif risk_aversion >= 7.0:
        return "Low-Risk Investor"
    elif risk_aversion <= 2.5 and esg_preference <= 0.02:
        return "Return-Seeking Investor"
    else:
        return "Balanced Investor"


persona_defaults = {
    "Balanced Investor": {"risk_aversion": 4.0, "esg_preference": 0.03},
    "Sustainability-Focused Investor": {"risk_aversion": 5.5, "esg_preference": 0.07},
    "Return-Seeking Investor": {"risk_aversion": 2.0, "esg_preference": 0.01},
    "Low-Risk Investor": {"risk_aversion": 8.0, "esg_preference": 0.02},
}

persona_descriptions = {
    "Balanced Investor": "Prefers a measured balance between growth, risk control and sustainability.",
    "Sustainability-Focused Investor": "Places strong value on sustainable outcomes and accepts lower returns for higher ESG quality.",
    "Return-Seeking Investor": "Prioritises performance and tolerates more volatility to pursue stronger returns.",
    "Low-Risk Investor": "Prefers capital stability, lower volatility and cautious overall exposure.",
}

# ------------------------------------------------------------
# Sidebar inputs
# ------------------------------------------------------------
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
st.sidebar.caption(persona_descriptions[persona])

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
        max_value=0.12,
        value=float(default_esg_preference),
        step=0.005,
        help="Higher values place more emphasis on sustainability in the recommendation.",
    )
else:
    risk_aversion = default_risk_aversion
    esg_preference = default_esg_preference
    st.sidebar.info(
        f"{persona}\n\nRisk Aversion: {risk_aversion:.1f}\n\nESG Preference: {esg_preference:.3f}"
    )

if use_manual_preferences:
    display_persona = get_profile_from_preferences(risk_aversion, esg_preference)
else:
    display_persona = persona

st.sidebar.header("Sustainability Method")
esg_method = st.sidebar.selectbox(
    "Choose a sustainability lens",
    [
        "Broad ESG",
        "Climate-Focused",
        "Exclusions-Focused",
        "Impact-Focused",
    ],
    help="This changes how sustainability enters the optimisation.",
)

apply_controversy_penalty = st.sidebar.checkbox(
    "Penalise controversial companies", value=True
)

st.sidebar.header("Asset Inputs")

asset1_name = st.sidebar.text_input("Asset 1 name", value="Sustainable Infrastructure Fund")
r1 = st.sidebar.number_input("Asset 1 expected return (%)", value=6.4, step=0.1) / 100
sd1 = st.sidebar.number_input("Asset 1 standard deviation (%)", value=10.0, min_value=0.01, step=0.1) / 100
esg1 = st.sidebar.slider("Asset 1 ESG score", min_value=0, max_value=100, value=85, step=1)
controversy1 = st.sidebar.slider("Asset 1 controversy score", min_value=0, max_value=100, value=10, step=1)

asset1_carbon = st.sidebar.slider("Asset 1 carbon intensity", min_value=0, max_value=100, value=20, step=1)
asset1_physical = st.sidebar.slider("Asset 1 physical climate risk", min_value=0, max_value=100, value=25, step=1)
asset1_transition = st.sidebar.slider("Asset 1 transition climate risk", min_value=0, max_value=100, value=20, step=1)

asset1_fossil = st.sidebar.checkbox("Asset 1 has fossil fuel exposure", value=False)
asset1_tobacco = st.sidebar.checkbox("Asset 1 has tobacco exposure", value=False)
asset1_gambling = st.sidebar.checkbox("Asset 1 has gambling exposure", value=False)

st.sidebar.markdown("---")

asset2_name = st.sidebar.text_input("Asset 2 name", value="Traditional Energy Fund")
r2 = st.sidebar.number_input("Asset 2 expected return (%)", value=11.0, step=0.1) / 100
sd2 = st.sidebar.number_input("Asset 2 standard deviation (%)", value=18.0, min_value=0.01, step=0.1) / 100
esg2 = st.sidebar.slider("Asset 2 ESG score", min_value=0, max_value=100, value=40, step=1)
controversy2 = st.sidebar.slider("Asset 2 controversy score", min_value=0, max_value=100, value=55, step=1)

asset2_carbon = st.sidebar.slider("Asset 2 carbon intensity", min_value=0, max_value=100, value=75, step=1)
asset2_physical = st.sidebar.slider("Asset 2 physical climate risk", min_value=0, max_value=100, value=45, step=1)
asset2_transition = st.sidebar.slider("Asset 2 transition climate risk", min_value=0, max_value=100, value=70, step=1)

asset2_fossil = st.sidebar.checkbox("Asset 2 has fossil fuel exposure", value=True)
asset2_tobacco = st.sidebar.checkbox("Asset 2 has tobacco exposure", value=False)
asset2_gambling = st.sidebar.checkbox("Asset 2 has gambling exposure", value=False)

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
    help="This is the lowest weighted ESG score your combined portfolio is allowed to have.",
)

st.sidebar.header("Exclusions")
apply_exclusions = st.sidebar.checkbox("Apply exclusion screen", value=False)

exclude_fossil = st.sidebar.checkbox("Exclude fossil fuel exposure", value=False)
exclude_tobacco = st.sidebar.checkbox("Exclude tobacco exposure", value=False)
exclude_gambling = st.sidebar.checkbox("Exclude gambling exposure", value=False)
exclude_severe_controversy = st.sidebar.checkbox("Exclude severe controversies", value=False)
severe_controversy_cutoff = st.sidebar.slider("Severe controversy threshold", 0, 100, 70, 1)

st.sidebar.header("Climate Overlay")
use_climate_overlay = st.sidebar.checkbox("Use climate-adjusted expected returns", value=False)
climate_weight = st.sidebar.slider(
    "Climate risk penalty strength",
    min_value=0.0,
    max_value=0.10,
    value=0.03,
    step=0.005,
    help="Higher values apply a larger deduction to expected return for climate risk exposure.",
)

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def portfolio_return(w1, r1_used, r2_used):
    w2 = 1 - w1
    return w1 * r1_used + w2 * r2_used


def portfolio_variance(w1, sd1_used, sd2_used, rho):
    w2 = 1 - w1
    return (w1**2) * (sd1_used**2) + (w2**2) * (sd2_used**2) + 2 * w1 * w2 * rho * sd1_used * sd2_used


def portfolio_sd(w1, sd1_used, sd2_used, rho):
    return np.sqrt(np.maximum(portfolio_variance(w1, sd1_used, sd2_used, rho), 0))


def portfolio_weighted_average(w1, x1, x2):
    w2 = 1 - w1
    return w1 * x1 + w2 * x2


def sharpe_ratio(ret, sd, r_free_used):
    if sd <= 0:
        return -np.inf
    return (ret - r_free_used) / sd


def climate_penalty(physical_risk, transition_risk, carbon_intensity, strength):
    return strength * (
        0.35 * (physical_risk / 100)
        + 0.35 * (transition_risk / 100)
        + 0.30 * (carbon_intensity / 100)
    )


def climate_adjusted_return(base_return, physical_risk, transition_risk, carbon_intensity, strength):
    return base_return - climate_penalty(physical_risk, transition_risk, carbon_intensity, strength)


def adjusted_sustainability_score(base_esg, controversy_score, carbon_intensity, method, apply_penalty):
    score = float(base_esg)

    if apply_penalty:
        score -= 0.20 * controversy_score

    if method == "Climate-Focused":
        score = 0.70 * score + 0.30 * (100 - carbon_intensity)
    elif method == "Exclusions-Focused":
        score = 0.85 * score + 0.15 * (100 - controversy_score)
    elif method == "Impact-Focused":
        score = score + 10
    else:
        score = score

    return float(np.clip(score, 0, 100))


def utility(ret, sd, sustainability_score, risk_aversion_used, esg_preference_used):
    return ret - 0.5 * risk_aversion_used * (sd**2) + esg_preference_used * (sustainability_score / 100)


def portfolio_utility(ret, sd, sustainability_score, risk_aversion_used, esg_preference_used):
    return ret - 0.5 * risk_aversion_used * (sd ** 2) + esg_preference_used * (sustainability_score / 100)


def utility_curve_return(sd_values, utility_level, risk_aversion_used, esg_preference_used, sustainability_score_fixed):
    """
    Return values for an indifference curve in risk-return space.

    ESG is held fixed at the sustainability score of the reference risky portfolio.
    This is consistent with plotting a dynamic utility curve through one chosen point.
    """
    return (
        utility_level
        + 0.5 * risk_aversion_used * (sd_values ** 2)
        - esg_preference_used * (sustainability_score_fixed / 100)
    )


def asset_is_excluded(
    fossil_flag, tobacco_flag, gambling_flag, controversy_score,
    apply_screen, fossil_rule, tobacco_rule, gambling_rule, controversy_rule, controversy_cutoff
):
    if not apply_screen:
        return False

    if fossil_rule and fossil_flag:
        return True
    if tobacco_rule and tobacco_flag:
        return True
    if gambling_rule and gambling_flag:
        return True
    if controversy_rule and controversy_score >= controversy_cutoff:
        return True

    return False


def profile_label_from_persona(persona_name):
    if persona_name == "Balanced Investor":
        return "Balanced"
    if persona_name == "Sustainability-Focused Investor":
        return "Sustainability-led"
    if persona_name == "Return-Seeking Investor":
        return "Growth-led"
    return "Defensive"


def allocation_block(title, value):
    return f"""
    <div style="text-align:center;">
        <div style="color:white; font-size:16px; font-weight:600; margin-bottom:8px;">
            {title}
        </div>
        <div style="color:white; font-size:48px; font-weight:700; line-height:1.1;">
            {value}
        </div>
    </div>
    """


# ------------------------------------------------------------
# Adjusted asset inputs
# ------------------------------------------------------------
adj_esg1 = adjusted_sustainability_score(esg1, controversy1, asset1_carbon, esg_method, apply_controversy_penalty)
adj_esg2 = adjusted_sustainability_score(esg2, controversy2, asset2_carbon, esg_method, apply_controversy_penalty)

if use_climate_overlay:
    r1_used = climate_adjusted_return(r1, asset1_physical, asset1_transition, asset1_carbon, climate_weight)
    r2_used = climate_adjusted_return(r2, asset2_physical, asset2_transition, asset2_carbon, climate_weight)
else:
    r1_used = r1
    r2_used = r2

asset1_excluded = asset_is_excluded(
    asset1_fossil, asset1_tobacco, asset1_gambling, controversy1,
    apply_exclusions, exclude_fossil, exclude_tobacco, exclude_gambling,
    exclude_severe_controversy, severe_controversy_cutoff
)

asset2_excluded = asset_is_excluded(
    asset2_fossil, asset2_tobacco, asset2_gambling, controversy2,
    apply_exclusions, exclude_fossil, exclude_tobacco, exclude_gambling,
    exclude_severe_controversy, severe_controversy_cutoff
)

# ------------------------------------------------------------
# Weight grid
# ------------------------------------------------------------
if allow_leverage:
    weights = np.linspace(-0.5, 1.5, 4001)
else:
    weights = np.linspace(0.0, 1.0, 4001)

returns = np.array([portfolio_return(w, r1_used, r2_used) for w in weights])
risks = np.array([portfolio_sd(w, sd1, sd2, rho12) for w in weights])
sustainability_scores = np.array([portfolio_weighted_average(w, adj_esg1, adj_esg2) for w in weights])
utilities = np.array(
    [utility(ret, sd, sus, risk_aversion, esg_preference) for ret, sd, sus in zip(returns, risks, sustainability_scores)]
)
sharpes = np.array([sharpe_ratio(ret, sd, r_free) for ret, sd in zip(returns, risks)])

feasible = np.ones_like(weights, dtype=bool)

if exclude_low_esg:
    feasible &= sustainability_scores >= esg_floor

if asset1_excluded and asset2_excluded:
    feasible &= False
elif asset1_excluded:
    feasible &= weights <= 0
elif asset2_excluded:
    feasible &= weights >= 1

utilities = np.where(feasible, utilities, -np.inf)
sharpes = np.where(feasible, sharpes, -np.inf)

if np.all(~feasible):
    st.error("No feasible portfolio meets your current exclusions and sustainability rules. Relax one of the constraints.")
    st.stop()

# ------------------------------------------------------------
# Tangency portfolio
# ------------------------------------------------------------
tangency_idx = np.argmax(sharpes)
w1_tan = weights[tangency_idx]
w2_tan = 1 - w1_tan

ret_tan = returns[tangency_idx]
sd_tan = risks[tangency_idx]
sus_tan = sustainability_scores[tangency_idx]
sharpe_tan = sharpes[tangency_idx]

# ------------------------------------------------------------
# Optimal risky portfolio
# ------------------------------------------------------------
optimal_idx = np.argmax(utilities)
w1_opt_risky = weights[optimal_idx]
w2_opt_risky = 1 - w1_opt_risky

ret_opt_risky = returns[optimal_idx]
sd_opt_risky = risks[optimal_idx]
sus_opt_risky = sustainability_scores[optimal_idx]
u_opt_risky = portfolio_utility(
    ret_opt_risky,
    sd_opt_risky,
    sus_opt_risky,
    risk_aversion,
    esg_preference
)

# ------------------------------------------------------------
# Final recommended portfolio with risk-free asset
# ------------------------------------------------------------
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
    sus_complete = (w1_complete * adj_esg1 + w2_complete * adj_esg2) / (w1_complete + w2_complete)
else:
    sus_complete = 0.0

# ------------------------------------------------------------
# Utility breakdown
# ------------------------------------------------------------
expected_return_component = ret_opt_risky
risk_penalty_component = 0.5 * risk_aversion * (sd_opt_risky**2)
sustainability_reward_component = esg_preference * (sus_opt_risky / 100)

# ------------------------------------------------------------
# Explanations
# ------------------------------------------------------------
def explain_portfolio():
    lead_asset = asset1_name if w1_opt_risky >= w2_opt_risky else asset2_name
    stronger_sus_asset = asset1_name if adj_esg1 >= adj_esg2 else asset2_name
    higher_return_asset = asset1_name if r1_used >= r2_used else asset2_name

    text = (
        f"The recommendation leans most heavily toward **{lead_asset}**. "
        f"Under the selected sustainability lens, **{stronger_sus_asset}** has the stronger sustainability profile, "
        f"while **{higher_return_asset}** offers the higher climate-adjusted expected return. "
        f"The optimiser combines your risk tolerance with your sustainability preference to find the most suitable risky composition."
    )

    if exclude_low_esg:
        text += f" A minimum sustainability threshold of **{esg_floor}** is also being enforced."

    if apply_exclusions:
        text += " Exclusion rules are active, so ineligible assets or portfolio mixes are removed from consideration."

    if use_climate_overlay:
        text += " Expected returns are being adjusted for physical risk, transition risk and carbon intensity."

    if y < 1:
        text += " Part of the allocation remains in the risk-free asset to reduce overall volatility."
    elif np.isclose(y, 1.0):
        text += " The allocation is fully invested across the risky assets."
    else:
        text += " Borrowing is enabled, so the final allocation uses more than the initial capital base."

    return text


def why_not_alternative():
    ret_gap = (ret_tan - ret_complete) * 100
    risk_gap = (sd_tan - sd_complete) * 100
    sus_gap = sus_tan - sus_complete

    text = (
        f"The maximum-Sharpe portfolio offers an expected return of **{ret_tan * 100:.2f}%**, "
        f"with risk of **{sd_tan * 100:.2f}%** and ESG score of **{sus_tan:.2f}**. "
        f"Your recommended portfolio instead reflects your utility preferences, so it may accept a lower return or Sharpe ratio in exchange for lower volatility, higher sustainability quality, or both."
    )

    text += (
        f" Relative to the maximum-Sharpe solution, your recommendation changes expected return by **{-ret_gap:.2f}%**, "
        f"changes risk by **{-risk_gap:.2f}%** and changes sustainability by **{-sus_gap:.2f} points**."
    )

    return text


def get_method_explanation():
    if esg_method == "Broad ESG":
        return "Uses the ESG score as a broad overall measure."
    if esg_method == "Climate-Focused":
        return "Places more emphasis on lower carbon intensity alongside the ESG score."
    if esg_method == "Exclusions-Focused":
        return "Gives slightly more weight to controversy-adjusted sustainability quality."
    return "Adds a premium to sustainability quality to reflect stronger impact preference."


# ------------------------------------------------------------
# Cards
# ------------------------------------------------------------
card_style = """
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 14px 20px;
    border-radius: 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
    min-height: 70px;
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

# ------------------------------------------------------------
# Tabs
# ------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Results",
        "📈 Frontier",
        "🌍 Sustainability Trade-Off",
        "🎯 ESG–Sharpe Frontier",
        "🧠 Investor Dashboard",
        "ℹ️ How It Works",
    ]
)

# ------------------------------------------------------------
# TAB 1
# ------------------------------------------------------------
with tab1:
    st.markdown("## Your **Recommended** Portfolio Composition")
    st.caption("Your investment is optimally split between risky assets and a risk-free asset, based on your risk and sustainability preferences.")

    composition_left, composition_right = st.columns([2.2, 1.0], gap="large")

    with composition_left:
        top1, top2, top3 = st.columns(3)

        top1.markdown(
            allocation_block(asset1_name, f"{w1_complete * 100:.2f}%"),
            unsafe_allow_html=True
        )
        top2.markdown(
            allocation_block(asset2_name, f"{w2_complete * 100:.2f}%"),
            unsafe_allow_html=True
        )

        if w_rf >= 0:
            top3.markdown(
                allocation_block("Risk-free Asset", f"{w_rf * 100:.2f}%"),
                unsafe_allow_html=True
            )
        else:
            top3.markdown(
                allocation_block("Borrowing", f"{abs(w_rf) * 100:.2f}%"),
                unsafe_allow_html=True
            )

    with composition_right:
        st.markdown("### Composition Chart")

        fig_pie, ax_pie = plt.subplots(figsize=(4.8, 4.8), facecolor="none")
        ax_pie.set_facecolor("none")

        if w_rf >= 0:
            pie_labels = [asset1_name, asset2_name, "Risk-free Asset"]
            pie_sizes = [max(w1_complete, 0), max(w2_complete, 0), max(w_rf, 0)]
        else:
            pie_labels = [asset1_name, asset2_name]
            pie_sizes = [max(w1_complete, 0), max(w2_complete, 0)]

        pie_colors = ["#2E8B57", "#FF6B35", "#4DA3FF"]

        def autopct_format(pct):
            return f"{pct:.1f}%" if pct >= 4 else ""

        wedges, texts, autotexts = ax_pie.pie(
            pie_sizes,
            labels=None,
            colors=pie_colors[:len(pie_sizes)],
            startangle=90,
            counterclock=False,
            autopct=autopct_format,
            pctdistance=0.72,
            wedgeprops={"width": 0.42, "edgecolor": "#0E1117", "linewidth": 2},
            textprops={"color": "white", "fontsize": 10, "fontweight": "bold"},
        )

        centre_circle = plt.Circle((0, 0), 0.42, fc="#0E1117")
        ax_pie.add_artist(centre_circle)

        ax_pie.text(
            0,
            0.08,
            "Portfolio",
            ha="center",
            va="center",
            color="white",
            fontsize=12,
            fontweight="semibold",
        )
        ax_pie.text(
            0,
            -0.08,
            "Mix",
            ha="center",
            va="center",
            color="#A0A0A0",
            fontsize=11,
        )

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(11)
            autotext.set_fontweight("bold")

        ax_pie.axis("equal")
        fig_pie.patch.set_alpha(0)

        st.pyplot(fig_pie, transparent=True)

        legend_labels = [f"{label}: {size * 100:.2f}%" for label, size in zip(pie_labels, pie_sizes)]
        for i, label in enumerate(legend_labels):
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    margin-bottom:8px;
                    font-size:14px;
                    color:white;
                ">
                    <div style="
                        width:12px;
                        height:12px;
                        border-radius:50%;
                        background-color:{pie_colors[i]};
                        margin-right:10px;
                        flex-shrink:0;
                    "></div>
                    <div>{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if w_rf < 0:
            st.caption("Borrowing is not displayed in the composition chart.")

    st.markdown("### Portfolio Snapshot")

    snap1, snap2, snap3 = st.columns(3)

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
                <div style="{label_style}">ESG Score</div>
                <div style="{value_style}">{sus_complete:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("Higher scores reflect stronger sustainability performance based on your selected ESG lens.")

    st.markdown("")
    left_col, right_col = st.columns([1.05, 0.95], gap="large")

    with left_col:
        if allow_leverage and y > 1:
            st.warning("This recommendation uses BORROWING to increase risky exposure.")
        elif np.isclose(w_rf, 0.0):
            st.info("This recommendation is fully invested in the risky assets.")
        elif w_rf > 0:
            st.info("Part of the allocation remains in the risk-free asset to soften volatility.")

        if asset1_excluded:
            st.error(f"{asset1_name} is excluded under the current screening rules.")
        if asset2_excluded:
            st.error(f"{asset2_name} is excluded under the current screening rules.")

        st.markdown("### Recommendation Rationale")
        st.write(explain_portfolio())

        st.markdown("### Why Not the Maximum-Sharpe Alternative?")
        st.write(why_not_alternative())

    with right_col:
        st.markdown("### Your Utility Break Down")
        util1, util2, util3 = st.columns(3)
        util1.metric("Return term", f"{expected_return_component:.4f}")
        util2.metric("Risk penalty", f"-{risk_penalty_component:.4f}")
        util3.metric("Sustainability reward", f"{sustainability_reward_component:.4f}")

        with st.expander("See underlying risky portfolio details"):
            mix1, mix2 = st.columns(2)
            mix3, mix4 = st.columns(2)
            mix1.metric(asset1_name, f"{w1_opt_risky * 100:.2f}%")
            mix2.metric(asset2_name, f"{w2_opt_risky * 100:.2f}%")
            mix3.metric("Tangency Sharpe ratio", f"{sharpe_tan:.3f}")
            mix4.metric("Optimal risky sustainability", f"{sus_opt_risky:.2f}")

        with st.expander("Adjusted asset metrics used by the optimiser"):
            a1, a2 = st.columns(2)
            with a1:
                st.markdown(f"**{asset1_name}**")
                st.write(f"- Expected return used: {r1_used * 100:.2f}%")
                st.write(f"- ESG score used: {adj_esg1:.2f}")
            with a2:
                st.markdown(f"**{asset2_name}**")
                st.write(f"- Expected return used: {r2_used * 100:.2f}%")
                st.write(f"- ESG score used: {adj_esg2:.2f}")

# ------------------------------------------------------------
# TAB 2
# ------------------------------------------------------------
with tab2:
    st.subheader("Sustainable Frontier")
    st.caption("Risk-return space with feasible and infeasible portfolio mixes.")

    fig1, ax1 = plt.subplots(figsize=(10, 6))

    infeasible_mask = ~feasible
    feasible_mask = feasible

    if np.any(infeasible_mask):
        ax1.scatter(
            risks[infeasible_mask],
            returns[infeasible_mask],
            s=12,
            alpha=0.25,
            label="Infeasible portfolios",
        )

    scatter1 = ax1.scatter(
        risks[feasible_mask],
        returns[feasible_mask],
        c=sustainability_scores[feasible_mask],
        cmap="YlGn",
        s=16,
        alpha=0.95,
        edgecolors="black",
        linewidths=0.05,
        label="Feasible risky portfolios",
    )

    ax1.scatter(sd1, r1_used, s=140, marker="o", label=asset1_name, zorder=3)
    ax1.scatter(sd2, r2_used, s=140, marker="o", label=asset2_name, zorder=3)
    ax1.scatter(sd_tan, ret_tan, s=220, marker="*", label="Tangency portfolio", zorder=5)
    ax1.scatter(sd_complete, ret_complete, s=170, marker="X", label="Recommended portfolio", zorder=6)
    ax1.scatter(0, r_free, s=140, marker="s", label="Risk-free asset", zorder=4)

    sd_line = np.linspace(0, max(risks) * 1.15, 100)
    if sd_opt_risky > 0:
        ret_line = r_free + ((ret_opt_risky - r_free) / sd_opt_risky) * sd_line
        ax1.plot(sd_line, ret_line, linestyle="--", linewidth=1.0, label="Capital allocation line", zorder=1)

    # Dynamic investor indifference curve through the recommended risky portfolio
    sd_curve = np.linspace(0, max(risks) * 1.15, 400)
    ret_curve = utility_curve_return(
        sd_curve,
        u_opt_risky,
        risk_aversion,
        esg_preference,
        sus_opt_risky
    )

    ax1.plot(
        sd_curve,
        ret_curve,
        linestyle=":",
        linewidth=2.5,
        color="purple",
        label="Utility curve",
        zorder=2
    )

    ax1.set_xlabel("Risk (standard deviation)")
    ax1.set_ylabel("Expected return")
    ax1.set_title("Risk-Return Frontier Coloured by ESG Score")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    cbar1 = plt.colorbar(scatter1, ax=ax1)
    cbar1.set_label("Portfolio ESG score")

    st.pyplot(fig1)

    st.markdown(
        f"""
        <div class="small-note">
        Feasible portfolios satisfy all active rules. Grey points fail at least one condition.
        Current sustainability lens: <b>{esg_method}</b>. {get_method_explanation()}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# TAB 3
# ------------------------------------------------------------
with tab3:
    st.subheader("Sustainability Trade-Off")
    st.caption("How expected return changes across different sustainability levels.")

    fig2, ax2 = plt.subplots(figsize=(10, 6))

    scatter2 = ax2.scatter(
        sustainability_scores[feasible_mask],
        returns[feasible_mask],
        c=risks[feasible_mask],
        cmap="viridis",
        s=20,
        alpha=0.95,
        edgecolors="black",
        linewidths=0.05,
        label="Feasible risky portfolios",
    )

    if np.any(infeasible_mask):
        ax2.scatter(
            sustainability_scores[infeasible_mask],
            returns[infeasible_mask],
            s=12,
            alpha=0.20,
            label="Infeasible portfolios",
        )

    ax2.scatter(adj_esg1, r1_used, s=140, marker="o", label=asset1_name)
    ax2.scatter(adj_esg2, r2_used, s=140, marker="o", label=asset2_name)
    ax2.scatter(sus_complete, ret_complete, s=170, marker="X", label="Recommended portfolio")

    if exclude_low_esg:
        ax2.axvline(esg_floor, linestyle="--", linewidth=1.8, label=f"Minimum score = {esg_floor}")

    ax2.annotate(
        "Recommended",
        xy=(sus_complete, ret_complete),
        xytext=(sus_complete + 1.5, ret_complete + 0.003),
        fontsize=9,
    )

    ax2.set_xlabel("Portfolio ESG score")
    ax2.set_ylabel("Expected return")
    ax2.set_title("Expected Return vs ESG Score")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    cbar2 = plt.colorbar(scatter2, ax=ax2)
    cbar2.set_label("Portfolio risk")

    st.pyplot(fig2)

    compare_left, compare_right = st.columns(2)
    with compare_left:
        st.markdown("### Recommended vs Maximum-Sharpe")
        st.metric("Recommended return", f"{ret_complete * 100:.2f}%")
        st.metric("Recommended risk", f"{sd_complete * 100:.2f}%")
        st.metric("Recommended sustainability", f"{sus_complete:.2f}")
    with compare_right:
        st.markdown("### Alternative Benchmark")
        st.metric("Max-Sharpe return", f"{ret_tan * 100:.2f}%")
        st.metric("Max-Sharpe risk", f"{sd_tan * 100:.2f}%")
        st.metric("Max-Sharpe sustainability", f"{sus_tan:.2f}")

# ------------------------------------------------------------
# TAB 4
# ------------------------------------------------------------
with tab4:
    st.subheader("ESG–Sharpe Frontier")
    st.caption("How stronger ESG scores relate to reward-to-risk performance across feasible portfolios.")

    fig_esg_sharpe, ax_esg_sharpe = plt.subplots(figsize=(10, 6))

    infeasible_mask = ~feasible
    feasible_mask = feasible

    if np.any(infeasible_mask):
        ax_esg_sharpe.scatter(
            sustainability_scores[infeasible_mask],
            sharpes[infeasible_mask],
            s=12,
            alpha=0.20,
            label="Infeasible portfolios",
        )

    scatter_esg_sharpe = ax_esg_sharpe.scatter(
        sustainability_scores[feasible_mask],
        sharpes[feasible_mask],
        c=risks[feasible_mask],
        cmap="viridis",
        s=22,
        alpha=0.95,
        edgecolors="black",
        linewidths=0.05,
        label="Feasible portfolios",
    )

    ax_esg_sharpe.scatter(
        adj_esg1,
        sharpe_ratio(r1_used, sd1, r_free),
        s=140,
        marker="o",
        label=asset1_name,
        zorder=3,
    )
    ax_esg_sharpe.scatter(
        adj_esg2,
        sharpe_ratio(r2_used, sd2, r_free),
        s=140,
        marker="o",
        label=asset2_name,
        zorder=3,
    )
    ax_esg_sharpe.scatter(
        sus_tan,
        sharpe_tan,
        s=220,
        marker="*",
        label="Maximum-Sharpe portfolio",
        zorder=5,
    )
    ax_esg_sharpe.scatter(
        sus_complete,
        sharpe_ratio(ret_complete, sd_complete, r_free),
        s=170,
        marker="X",
        label="Recommended portfolio",
        zorder=6,
    )

    ax_esg_sharpe.annotate(
        "Max-Sharpe",
        xy=(sus_tan, sharpe_tan),
        xytext=(sus_tan + 1.0, sharpe_tan + 0.01),
        fontsize=9,
    )

    ax_esg_sharpe.annotate(
        "Recommended",
        xy=(sus_complete, sharpe_ratio(ret_complete, sd_complete, r_free)),
        xytext=(sus_complete + 1.0, sharpe_ratio(ret_complete, sd_complete, r_free) - 0.04),
        fontsize=9,
    )

    ax_esg_sharpe.set_xlabel("Portfolio ESG score")
    ax_esg_sharpe.set_ylabel("Sharpe ratio")
    ax_esg_sharpe.set_title("Sharpe Ratio vs ESG Score")
    ax_esg_sharpe.grid(True, alpha=0.3)
    ax_esg_sharpe.legend()

    cbar_esg_sharpe = plt.colorbar(scatter_esg_sharpe, ax=ax_esg_sharpe)
    cbar_esg_sharpe.set_label("Portfolio risk")

    st.pyplot(fig_esg_sharpe)

    sharpe_complete = sharpe_ratio(ret_complete, sd_complete, r_free)
    sharpe_cost = sharpe_tan - sharpe_complete
    esg_gain = sus_complete - sus_tan

    left_compare, right_compare = st.columns(2)

    with left_compare:
        st.markdown("### Recommended vs Maximum-Sharpe")
        st.metric("Recommended Sharpe", f"{sharpe_complete:.3f}")
        st.metric("Recommended ESG score", f"{sus_complete:.2f}")

    with right_compare:
        st.markdown("### ESG Preference Trade-Off")
        st.metric("Sharpe ratio cost", f"-{sharpe_cost:.3f}")
        st.metric("ESG score gain", f"{esg_gain:+.2f}")

    st.markdown(
        f"""
        <div class="small-note">
        This chart makes the ESG trade-off explicit. The maximum-Sharpe portfolio delivers the highest reward-to-risk ratio,
        while the recommended portfolio may move toward a higher ESG score when investor utility places additional
        weight on ESG preference.

            Higher ESG scores are achievable, but at a cost to Sharpe ratio relative to the maximum-Sharpe portfolio.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# TAB 5
# ------------------------------------------------------------
with tab5:
    st.subheader("Investor Dashboard")
    st.caption("A summary of how the app interprets your preferences.")

    dash1, dash2, dash3 = st.columns(3)

    with dash1:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="{label_style}">Investor Style</div>
                <div style="{value_style}; font-size:28px;">{display_persona}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with dash2:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="{label_style}">Risk Aversion</div>
                <div style="{value_style}">{risk_aversion:.1f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with dash3:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="{label_style}">Sustainability Preference</div>
                <div style="{value_style}">{esg_preference:.3f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Profile Interpretation")
    st.write(persona_descriptions[display_persona])
    st.write(f"Current sustainability lens: **{esg_method}**. {get_method_explanation()}")

    lens1, lens2 = st.columns(2)
    with lens1:
        st.markdown("### Asset Sustainability View")
        st.write(f"**{asset1_name}** adjusted ESG score: **{adj_esg1:.2f}**")
        st.write(f"**{asset2_name}** adjusted ESG score: **{adj_esg2:.2f}**")
    with lens2:
        st.markdown("### Climate View")
        st.write(f"**{asset1_name}** climate-adjusted return used: **{r1_used * 100:.2f}%**")
        st.write(f"**{asset2_name}** climate-adjusted return used: **{r2_used * 100:.2f}%**")

# ------------------------------------------------------------
# TAB 6
# ------------------------------------------------------------
with tab6:
    st.subheader("How It Works")

    st.markdown("The starting point is the standard mean-variance framework. Portfolio utility is extended so sustainability (ESG) enters the decision rule directly:")

    st.latex(r"U = E(R_p) - 0.5 \gamma \sigma_p^2 + \lambda s")

    st.markdown(
        f"""
Where:

- **E(Rp)** is the expected portfolio return  
- **γ** is the risk aversion parameter 
- **σp²** is the portfolio variance  
- **λ** is the strength/intensity of ESG preference  
    - λ = 0: ESG does not matter  
    - λ > 0: ESG gives positive utility (investor accepts lower financial return for higher ESG score)  
- **s** is the weighted average ESG score of the portfolio  

The app then layers in additional sustainable-finance features:

- **Sustainability methodology mode** changes how sustainability is interpreted  
- **Controversy penalty** reduces scores for assets with weaker controversy profiles  
- **Climate overlay** can reduce expected return for assets with higher physical risk, transition risk and carbon intensity  
- **Exclusion screen** removes assets that fail ethical or controversy rules  
- **Minimum ESG rule** removes portfolio mixes below your chosen threshold  

**Your current investor type:** {display_persona}  
**Current risk aversion:** {risk_aversion:.1f}  
**Current sustainability preference:** {esg_preference:.3f}  
**Current sustainability lens:** {esg_method}  

The final recommendation is the portfolio that gives the highest utility after all selected rules are applied.

The ESG–Sharpe frontier and benchmark comparison make the trade-off between sustainability and reward-to-risk performance explicit.
        """
    )
