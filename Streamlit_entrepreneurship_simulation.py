import streamlit as st
import random
import re
import json

# ----------------------------------------
# Helper and Evaluation Functions
# ----------------------------------------
STOP_WORDS = {
    'and','or','but','the','a','an','in','on','at','to','for','with','by','of','from'
}

def extract_keywords(text):
    tokens = re.findall(r"[A-Za-z]+", text.lower())
    return {t for t in tokens if t not in STOP_WORDS and len(t) > 1}


def evaluate_persona(persona):
    values_text    = persona.get('values', '').strip()
    behaviors_text = persona.get('behaviors', '').strip()
    total_words    = len(values_text.split()) + len(behaviors_text.split())
    extra          = min(total_words, 70)
    score = max(0, min(100, 30 + extra))
    st.session_state['score_persona'] = score
    return score


def evaluate_analysis(root_cols):
    primaries_filled   = sum(1 for col in root_cols if any(c.strip() for c in col))
    secondaries_filled = sum(1 for col in root_cols for c in col if c.strip())
    # Tiered scoring
    if primaries_filled >= 2 and secondaries_filled >= 2:
        score = random.randint(60, 80)
    elif primaries_filled >= 1 or secondaries_filled >= 1:
        score = random.randint(30, 59)
    else:
        score = random.randint(0, 29)
    st.session_state['score_analysis'] = score
    return score


def evaluate_ideation():
    score = max(0, min(100, 50 + random.randint(-5, 5)))
    st.session_state['score_ideation'] = score
    return score


def evaluate_sizing(people_m, willingness, sam_pct, som_pct, tam):
    # TAM score normalized 5M–20000M
    tam_score = int(min(100, max(0, (tam - 5) / (20000 - 5) * 100)))
    penalty   = max(0, sam_pct - 50) + max(0, som_pct - 50)
    score     = max(0, tam_score - int(penalty))
    st.session_state['score_sizing'] = score
    return score


def evaluate_pitch(text):
    words = len(text.split())
    base  = min(100, words * 5)
    score = max(0, min(100, base + random.randint(-10, 10)))
    st.session_state['score_pitch'] = score
    return score

# ----------------------------------------
# Streamlit App Setup
# ----------------------------------------
st.set_page_config(page_title="Entrepreneurship Business Game", layout="wide")
st.title('Entrepreneurship Business Game')

# Sidebar: Team Selection
st.sidebar.header('Team Selection')
team = st.sidebar.text_input('Team Name', 'Team A')
# Allow entry of up to 5 team members
st.sidebar.subheader('Team Members')
members = []
for i in range(5):
    m = st.sidebar.text_input(f'Member #{i+1}', key=f'member_{i}')
    members.append(m)
st.sidebar.markdown('---')

# Load previous session (import)
st.sidebar.markdown(":green[Upload Previous Session]")
uploaded = st.sidebar.file_uploader("Load session file", type="json")
if uploaded:
    data = json.load(uploaded)
    for k, v in data.items():
        st.session_state[k] = v

# Start Over button
if st.sidebar.button("🔄 Start Over", key="start_over"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# Tabs for each exercise
tabs = st.tabs([
    "1. Persona", "2. Analysis", "3. Ideation",
    "4. Sizing", "5. Pitch"
])

# --------- Exercise 1: Persona Development ---------
with tabs[0]:
    st.header('Exercise 1: Persona Development')
    with st.form('persona_form'):
        name      = st.text_input('Name')
        age       = st.text_input('Age')
        gender    = st.text_input('Gender')
        location  = st.text_input('Location')
        st.markdown('**Beyond demographics:**')
        values    = st.text_area('Values & Motivations')
        behaviors = st.text_area('Key Behaviors')
        # context fields
        jobs      = st.text_area('Jobs to be Done')
        pains     = st.text_area('Pains')
        gains     = st.text_area('Gains')
        motto     = st.text_input('Persona Motto / Quote')
        submit_p  = st.form_submit_button('Submit Persona')

    if submit_p:
        st.session_state['persona_name'] = name
        persona = {'values': values, 'behaviors': behaviors}
        score   = evaluate_persona(persona)
        st.markdown(f"**Persona Score:** {score}/100")
        if score < 60:
            st.warning("Your persona needs more depth—add richer values and behaviors.")
        elif score < 80:
            st.info("Good detail! Consider adding narrative context for even richer insight.")
        else:
            st.success("Excellent persona! You've provided very rich detail.")

# --------- Exercise 2: Problem Analysis (Fishbone) ---------
with tabs[1]:
    st.header('Exercise 2: Problem Analysis (Fishbone)')
    st.markdown(
        'Define the head problem, then identify up to 4 primary causes '
        'and up to 4 root causes under each.'
    )

    with st.form('analysis_form'):
        problem = st.text_input('Problem Statement')
        st.markdown('**Primary Causes (up to 4)**')
        cols = st.columns(4)
        primary_causes = []
        for i, col in enumerate(cols):
            with col:
                pc = st.text_input(f'Primary #{i+1}', key=f'pc{i}')
                primary_causes.append(pc)
        st.markdown('**Secondary (Root) Causes (up to 4 per primary)**')
        root_cols = []
        for i, pc in enumerate(primary_causes):
            col = cols[i]
            with col:
                st.markdown(f'**Roots of “{pc or "(empty)"}”**')
                secs = []
                for j in range(4):
                    sec = st.text_input(f'Root #{j+1}', key=f'sec_{i}_{j}')
                    secs.append(sec)
                root_cols.append(secs)
        submit_a = st.form_submit_button('Submit Analysis')
        if submit_a and problem.strip():
            st.session_state['problem_statement'] = problem
            st.session_state['primary_causes']      = primary_causes
            st.session_state['all_root_causes']     = [c for col in root_cols for c in col]

    if submit_a:
        score = evaluate_analysis(root_cols)
        st.markdown(f"**Analysis Score:** {score}/100")
        if score < 60:
            st.warning(
                "Your analysis needs more depth—identify additional causes to strengthen your insights."
            )
        elif score < 80:
            st.info(
                "Good progress! You've identified key causes but consider exploring further to deepen your analysis."
            )
        else:
            st.success("Excellent analysis! You've uncovered a comprehensive set of causes.")

# --------- Exercise 3: Ideation & Value Proposition ---------
with tabs[2]:
    st.header('Exercise 3: Ideation & Value Proposition')
    st.markdown('Fill in the blanks to prototype your Value Proposition.')

    primaries  = st.session_state.get('primary_causes', [])
    roots      = st.session_state.get('all_root_causes', [])
    all_causes = [c for c in primaries + roots if c.strip()]

    with st.form('ideation_form'):
        product     = st.text_input('Our',    placeholder='Products and Services')
        segment     = st.text_input('help(s)',placeholder='Customer Segment')
        job         = st.text_input('who wants to', placeholder='Jobs to be Done')
        pain_full   = st.text_input(
                         'by',
                         placeholder='Verb (e.g. reducing) + a customer pain'
                      )
        gain_full   = st.text_input(
                         'and',
                         placeholder='Verb (e.g. enabling) + a customer gain'
                      )
        alternative = st.text_input('unlike', placeholder='Competing Proposition')
        submit_i    = st.form_submit_button('Submit Value Proposition')

    if submit_i:
        st.session_state['vp_product'] = product
        vp_text = f"{pain_full} {gain_full}"
        vp_keys = extract_keywords(vp_text)
        matches = [
            cause for cause in all_causes
            if extract_keywords(cause) & vp_keys
        ]
        match_count = len(set(matches))

        if match_count >= 2:
            score = random.randint(80, 100)
        elif match_count == 1:
            score = random.randint(60, 79)
        else:
            score = random.randint(0, 59)
        st.session_state['score_ideation'] = score

        vp = (
            f"Our {product} help(s) {segment} who wants to {job} "
            f"by {pain_full} and {gain_full} unlike {alternative}."
        )
        st.markdown('**Value Proposition Prototype:**')
        st.info(vp)
        st.markdown(f"**Ideation Score:** {score}/100")
        if match_count < 2:
            st.warning(
                f"You only tied back to {match_count} cause{'s' if match_count!=1 else ''}. " +
                "Aim to reference two or more to boost alignment."
            )
        else:
            st.success("Excellent linkage to your analysis!")

# --------- Exercise 4: Market Opportunity Sizing ---------
with tabs[3]:
    st.header('Exercise 4: Market Opportunity Sizing')
    st.markdown(
        'Estimate your TAM by number of users (in millions) × willingness to pay ($), '
        'then set your SAM and SOM percentages. A random market scenario will adjust your SOM.'
    )
    with st.form('sizing_form'):
        people_m    = st.number_input('Number of people (millions)', min_value=0.0, format="%.2f")
        willingness = st.number_input('Willingness to pay per person ($/year)', min_value=0.0, format="%.2f")
        sam_pct     = st.slider('SAM (% of TAM)', 0, 100, 20)
        som_pct     = st.slider('SOM (% of SAM)', 0, 100, 10)
        submit_s    = st.form_submit_button('Submit Sizing')
    if submit_s:
        base_tam = people_m * willingness  # million-$
        noise    = random.uniform(0.8, 1.2)
        tam      = base_tam * noise
        sam      = tam * sam_pct / 100
        som      = sam * som_pct / 100

        st.markdown(f"**TAM Estimate:** {tam:.2f} M-$")
        st.markdown(f"**SAM:** {sam:.2f} M-$")
        st.markdown(f"**SOM:** {som:.2f} M-$")

        # Outlier warnings
        if base_tam < 5:
            st.warning('TAM below 5 M—market may be too small.')
        if base_tam > 20000:
            st.warning('TAM above 20 B—check assumptions.')
        if sam_pct > 50:
            st.warning('SAM above 50% may be unrealistic.')
        if som_pct > 50:
            st.warning('SOM above 50% may be unrealistic.')

        # Random market scenario
        scenarios = [
            ("Adverse regulation, too bad (-20%)", -0.2),
            ("Several competitors launched and gaining market share (-30%)", -0.3),
            ("Macro-economic shock rattling the markets (-10%)", -0.1),
            ("Macro-economic shock boosting the markets (+10%)", 0.1),
            ("Incumbent losing traction, customers seeking alternatives (+30%)", 0.3),
            ("Positive regulation alignment, lucky you (+20%)", 0.2),
        ]
        desc, factor = random.choice(scenarios)
        adjusted_som = som * (1 + factor)
        st.markdown(f"**Scenario:** {desc}")
        st.markdown(f"**Adjusted SOM:** {adjusted_som:.2f} M-$")
        st.session_state['som_value'] = adjusted_som

# --------- Exercise 5: Workshop Recap ---------
with tabs[4]:
    st.header('Exercise 5: Pitch Recap')
    st.subheader('🔍 Problem to Solve')
    st.write(st.session_state.get('problem_statement', '—'))
    st.subheader('👤 Target Customer Persona')
    st.write(st.session_state.get('persona_name', '—'))
    st.subheader('💡 Proposed Solution')
    st.write(st.session_state.get('vp_product', '—'))
    st.subheader('📈 Market Size (SOM)')
    st.write(f"{st.session_state.get('som_value', 0):.2f} M-$")
    st.markdown('---')
    st.header('📊 Individual Scores')
    scores = {
        'Persona':  st.session_state.get('score_persona', 0),
        'Analysis': st.session_state.get('score_analysis', 0),
        'Ideation': st.session_state.get('score_ideation', 0),
        'Pitch':    st.session_state.get('score_pitch', 0)
    }
    for name, val in scores.items():
        st.write(f"**{name}:** {val}/100")
    overall = sum(scores.values()) / len(scores)
    st.markdown('---')
    st.subheader(f"🎯 **Overall Score:** {overall:.1f}/100")

# Footer
state = { k: st.session_state[k] for k in st.session_state.keys() }
st.download_button(
    label="💾 Download Session",
    data=json.dumps(state),
    file_name=f"{team}_session.json",
    mime="application/json"
)

st.markdown('---')
st.write('Navigate tabs to complete the simulation. Your inputs are persisted.')
