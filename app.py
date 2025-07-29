
import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    return df['multiplier'].tolist()

def normalize_input(value):
    if value > 10:
        return value / 100
    return value

def compute_improved_confidence(data, threshold=2.0, trend_window=10):
    if not data:
        return 0.5, 0.5

    data = np.array(data)
    n = len(data)

    weights = np.linspace(0.5, 1.0, n)
    base_score = np.average((data > threshold).astype(int), weights=weights)

    recent = data[-trend_window:] if n >= trend_window else data
    trend_score = np.mean(recent > threshold) if len(recent) > 0 else 0.5

    streak = 1
    for i in range(n-2, -1, -1):
        if (data[i] > threshold and data[i+1] > threshold) or (data[i] <= threshold and data[i+1] <= threshold):
            streak += 1
        else:
            break
    streak_impact = min(streak * 0.02, 0.2)
    streak_score = streak_impact if data[-1] <= threshold else -streak_impact

    combined = (0.4 * base_score) + (0.45 * trend_score) + (0.15 * (0.5 + streak_score))
    combined = max(0, min(combined, 1))
    return combined, 1 - combined

def main():
    st.title("Crash Game Predictor (More Responsive)")
    st.write("Upload a CSV or enter values manually. Supports multipliers and percentages (e.g., 187 for 1.87x).")

    if "history" not in st.session_state:
        st.session_state.history = []

    uploaded_file = st.file_uploader("Upload multipliers CSV", type=["csv"])
    if uploaded_file:
        st.session_state.history = load_csv(uploaded_file)
        st.success(f"Loaded {len(st.session_state.history)} multipliers from file.")

    st.subheader("Manual Input")
    new_val = st.text_input("Enter a new multiplier or percentage (e.g., 1.87 or 187)")
    if st.button("Add"):
        try:
            val = float(new_val)
            val = normalize_input(val)
            st.session_state.history.append(val)
            st.success(f"Added {val}x")
        except:
            st.error("Invalid number.")

    if st.button("Reset All Data"):
        st.session_state.history = []
        st.success("All data cleared.")

    if st.session_state.history:
        data = st.session_state.history
        st.write(f"Entries so far: **{len(data)}**")
        st.progress(min(len(data) / 20, 1.0))
        st.info("Confidence now reflects your data fully (no cap).")

        above_conf, under_conf = compute_improved_confidence(data)
        st.subheader("Prediction")
        if above_conf > under_conf:
            st.write(f"Prediction: **Above 200%** ({above_conf:.1%} confidence)")
        else:
            st.write(f"Prediction: **Under 200%** ({under_conf:.1%} confidence)")
    else:
        st.write("Add data to get prediction.")

if __name__ == "__main__":
    main()
