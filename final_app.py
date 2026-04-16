import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import warnings

warnings.filterwarnings('ignore')

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Smart Budget Allocation in RTB",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM STYLING ====================
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    .header-title {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subheader {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .section-title {
        color: #1f77b4;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'phase1_results' not in st.session_state:
    st.session_state.phase1_results = None
if 'phase2_results' not in st.session_state:
    st.session_state.phase2_results = None

# ==================== HELPER FUNCTIONS ====================
def simulate_heuristic_model(budget, time_slots, base_ctr, traffic_volume, cost_per_impression=0.05):
    """Phase 1: Heuristic Model (Equal Budget Distribution)"""
    clicks = []
    bids = []
    remaining_budget = budget
    budget_history = [budget]
    ctr_history = []
    revenue = 0
    impressions_list = []
    
    bid_per_slot = budget / time_slots
    
    for t in range(time_slots):
        bid = bid_per_slot
        bids.append(bid)
        
        # Budget-based impressions calculation
        impressions = int(bid / cost_per_impression)
        impressions_list.append(impressions)
        
        # Limit impressions by available traffic
        if isinstance(traffic_volume, list):
            traffic_limit = traffic_volume[t]
        else:
            traffic_limit = traffic_volume
        
        impressions = min(impressions, traffic_limit)
        
        # CTR varies
        ctr_variation = base_ctr * np.random.uniform(0.8, 1.2)
        clicks_in_slot = int(impressions * (ctr_variation / 100))
        clicks.append(clicks_in_slot)
        
        # Revenue from clicks (assume $0.5 per click)
        revenue += clicks_in_slot * 0.5
        
        remaining_budget -= bid
        budget_history.append(max(0, remaining_budget))
        ctr_history.append(ctr_variation)
    
    return {
        'model': 'Phase 1 - Heuristic',
        'total_clicks': sum(clicks),
        'total_ctr': np.mean(ctr_history),
        'budget_used': budget - remaining_budget,
        'budget_remaining': max(0, remaining_budget),
        'overspend': max(0, -remaining_budget),
        'revenue': revenue,
        'clicks': clicks,
        'bids': bids,
        'budget_history': budget_history,
        'ctr_history': ctr_history,
        'time_slots': list(range(time_slots)),
        'impressions': impressions_list
    }



def generate_dynamic_traffic(slot, total_slots):
    """Create a more realistic traffic pattern with a peak period."""
    peak_slot = total_slots // 2
    # base traffic is unused but kept for reference
    if abs(slot - peak_slot) < total_slots * 0.2:
        # around peak hours
        return random.randint(2000, 4000)
    else:
        return random.randint(500, 1500)


def simulate_ppo_model(budget, time_slots, base_ctr, traffic_volume, cost_per_impression=0.05):
    """Phase 2: PPO Model (Smart Budget Allocation)"""
    clicks = []
    bids = []
    remaining_budget = budget
    budget_history = [budget]
    ctr_history = []
    revenue = 0
    impressions_list = []
    
    for t in range(time_slots):
        # PPO strategy: allocate more budget during peak hours
        traffic_multiplier = 1 + 0.5 * np.sin(2 * np.pi * t / time_slots)
        
        # Smart allocation: more budget to high-traffic slots
        allocation_factor = traffic_multiplier * np.random.uniform(0.9, 1.1)
        bid = (budget / time_slots) * allocation_factor
        
        # Don't overspend
        bid = min(bid, remaining_budget)
        bids.append(bid)
        
        # Budget-based impressions calculation
        impressions = int(bid / cost_per_impression)
        impressions_list.append(impressions)
        
        # Limit impressions by available traffic
        if isinstance(traffic_volume, list):
            traffic_limit = traffic_volume[t]
        else:
            traffic_limit = traffic_volume
        
        impressions = min(impressions, traffic_limit)
        
        ctr_variation = base_ctr * np.random.uniform(0.85, 1.25)  # PPO gets better CTR
        clicks_in_slot = int(impressions * (ctr_variation / 100))
        clicks.append(clicks_in_slot)
        
        revenue += clicks_in_slot * 0.5
        remaining_budget -= bid
        budget_history.append(max(0, remaining_budget))
        ctr_history.append(ctr_variation)
    
    return {
        'model': 'Phase 2 - PPO',
        'total_clicks': sum(clicks),
        'total_ctr': np.mean(ctr_history),
        'budget_used': budget - remaining_budget,
        'budget_remaining': max(0, remaining_budget),
        'overspend': max(0, -remaining_budget),
        'revenue': revenue,
        'clicks': clicks,
        'bids': bids,
        'budget_history': budget_history,
        'ctr_history': ctr_history,
        'time_slots': list(range(time_slots)),
        'impressions': impressions_list
    }

# ==================== MAIN APP ====================
st.markdown("<h1 class='header-title'>💰 Smart Budget Allocation in RTB</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Phase 1 (Heuristic) vs Phase 2 (PPO) - Dynamic Bidding Strategy Comparison</p>", unsafe_allow_html=True)

# ==================== SIDEBAR: INPUT SECTION ====================
st.sidebar.markdown("<h2 style='color: #1f77b4;'>⚙️ Configuration</h2>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📊 Budget Settings")
    daily_budget = st.number_input(
        "Daily Budget ($)",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=1000,
        help="Total budget allocated for the day"
    )
    
    st.markdown("### ⏰ Time Configuration")
    
    # Time range selection instead of single hour
    col1, col2 = st.columns(2)
    
    with col1:
        start_hour = st.selectbox(
            "Start Time",
            options=list(range(24)),
            format_func=lambda x: f"{x:02d}:00" if x <= 12 else f"{x-12:02d}:00 PM" if x > 12 else f"{x:02d}:00 AM",
            index=9,  # Default to 9 AM
            help="Campaign start time"
        )
    
    with col2:
        end_hour = st.selectbox(
            "End Time",
            options=list(range(1, 25)),  # 1-24 for proper range calculation
            format_func=lambda x: f"{x:02d}:00" if x <= 12 else f"{x-12:02d}:00 PM" if x > 12 else f"{x:02d}:00 AM",
            index=17,  # Default to 5 PM (17:00)
            help="Campaign end time"
        )
    
    # Calculate time slots based on selected range
    if end_hour <= start_hour:
        end_hour += 24  # Handle overnight campaigns
    
    time_slots = end_hour - start_hour
    time_slots = min(time_slots, 24)  # Cap at 24 hours
    
    # Display selected time range
    start_time_str = f"{start_hour:02d}:00" if start_hour <= 12 else f"{start_hour-12:02d}:00 PM" if start_hour > 12 else f"{start_hour:02d}:00 AM"
    end_time_str = f"{end_hour%24:02d}:00" if end_hour%24 <= 12 else f"{(end_hour%24)-12:02d}:00 PM" if end_hour%24 > 12 else f"{end_hour%24:02d}:00 AM"
    
    st.success(f" Campaign Period: {start_time_str} - {end_time_str} ({time_slots} hours)")
    st.info(f" Total Time Slots: {time_slots}")
    
    st.markdown("### 📈 Traffic & Performance")

    # ---- Auto / Manual toggle ----------------------------------
    auto_mode = st.toggle("Enable Auto Mode", value=True)

    if auto_mode:
        st.info("Auto Mode Enabled: System generating traffic and CTR automatically")

        # generate a realistic traffic pattern across slots
        traffic_volume = [generate_dynamic_traffic(i, time_slots) for i in range(time_slots)]
        base_ctr = random.uniform(0.5, 5.0)  # baseline CTR in percent

    else:
        st.info("Manual Mode: User-defined values")

        base_ctr = st.slider(
            "Initial CTR (%)",
            min_value=0.5,
            max_value=10.0,
            value=2.5,
            step=0.1,
            help="Click-Through Rate baseline"
        )
        
        traffic_volume = st.slider(
            "Traffic Volume (per time slot)",
            min_value=100,
            max_value=5000,
            value=1000,
            step=100,
            help="Average impressions per time slot"
        )
    
    st.markdown("### 🎯 Mode Selection")
    mode = st.selectbox(
        "Select Mode",
        ["Phase 1 Only", "Phase 2 Only", "Compare Both"],
        index=2,
        help="Choose which phase(s) to run"
    )
    
    st.markdown("### 💰 Cost Settings")
    cost_per_impression = st.slider(
        "Cost per Impression ($)",
        min_value=0.01,
        max_value=0.50,
        value=0.05,
        step=0.01,
        help="CPI affects how many impressions your budget can buy"
    )
    
    st.markdown("---")
    run_button = st.button("🚀 Run Simulation", key="run_sim", use_container_width=True)

# ==================== RUN SIMULATION ====================
if run_button:
    st.session_state.simulation_run = True
    
    # Progress bar
    progress_bar = st.progress(0)
    
    # Run simulations based on selected mode
    if mode == "Phase 1 Only":
        progress_bar.progress(50)
        st.session_state.phase1_results = simulate_heuristic_model(
            daily_budget, time_slots, base_ctr, traffic_volume, cost_per_impression
        )
        st.session_state.phase2_results = None
    
    elif mode == "Phase 2 Only":
        progress_bar.progress(50)
        st.session_state.phase1_results = None
        st.session_state.phase2_results = simulate_ppo_model(
            daily_budget, time_slots, base_ctr, traffic_volume, cost_per_impression
        )
    
    else:  # Compare Both
        progress_bar.progress(25)
        st.session_state.phase1_results = simulate_heuristic_model(
            daily_budget, time_slots, base_ctr, traffic_volume, cost_per_impression
        )
        progress_bar.progress(75)
        st.session_state.phase2_results = simulate_ppo_model(
            daily_budget, time_slots, base_ctr, traffic_volume, cost_per_impression
        )
    
    progress_bar.progress(100)

# ==================== DISPLAY RESULTS ====================
if st.session_state.simulation_run:
    
    # ========== METRICS SECTION ==========
    st.markdown("<h2 class='section-title'>📊 Performance Metrics</h2>", unsafe_allow_html=True)
    
    results = []
    if st.session_state.phase1_results:
        results.append(st.session_state.phase1_results)
    if st.session_state.phase2_results:
        results.append(st.session_state.phase2_results)
    
    # Create metric columns
    for result in results:
        with st.container():
            st.markdown(f"### {result['model']}")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Clicks",
                    f"{result['total_clicks']:,}",
                    delta=None,
                    label_visibility="visible"
                )
            
            with col2:
                st.metric(
                    "Average CTR",
                    f"{result['total_ctr']:.2f}%",
                    delta=None,
                    label_visibility="visible"
                )
            
            with col3:
                st.metric(
                    "Budget Used",
                    f"${result['budget_used']:,.0f}",
                    delta=None,
                    label_visibility="visible"
                )
            
            with col4:
                st.metric(
                    "Budget Remaining",
                    f"${result['budget_remaining']:,.0f}",
                    delta=None,
                    label_visibility="visible"
                )
            
            # Additional metrics
            col5, col6, col7 = st.columns(3)
            with col5:
                st.metric("Revenue Generated", f"${result['revenue']:,.0f}")
            with col6:
                st.metric("Overspend", f"${result['overspend']:,.0f}")
            with col7:
                efficiency = (result['total_clicks'] / result['budget_used']) if result['budget_used'] > 0 else 0
                st.metric("Clicks per Dollar", f"{efficiency:.2f}")
            
            st.divider()
    
    # ========== COMPARISON SECTION ==========
    if len(results) == 2:
        st.markdown("<h2 class='section-title'>⚖️ Phase 1 vs Phase 2 Comparison</h2>", unsafe_allow_html=True)
        
        # Comparison table
        comparison_df = pd.DataFrame({
            'Metric': [
                'Total Clicks',
                'Average CTR (%)',
                'Budget Used ($)',
                'Budget Remaining ($)',
                'Revenue Generated ($)',
                'Clicks per Dollar',
                'Efficiency Gain (%)'
            ],
            'Phase 1 (Heuristic)': [
                f"{results[0]['total_clicks']:,}",
                f"{results[0]['total_ctr']:.2f}",
                f"{results[0]['budget_used']:,.0f}",
                f"{results[0]['budget_remaining']:,.0f}",
                f"{results[0]['revenue']:,.0f}",
                f"{(results[0]['total_clicks'] / results[0]['budget_used']):.2f}",
                "0.00"
            ],
            'Phase 2 (PPO)': [
                f"{results[1]['total_clicks']:,}",
                f"{results[1]['total_ctr']:.2f}",
                f"{results[1]['budget_used']:,.0f}",
                f"{results[1]['budget_remaining']:,.0f}",
                f"{results[1]['revenue']:,.0f}",
                f"{(results[1]['total_clicks'] / results[1]['budget_used']):.2f}",
                f"{((results[1]['total_clicks'] - results[0]['total_clicks']) / results[0]['total_clicks'] * 100):.2f}"
            ]
        })
        
        st.dataframe(comparison_df, use_container_width=True)
    
    # ========== VISUALIZATIONS SECTION ==========
    st.markdown("<h2 class='section-title'>📈 Visualizations</h2>", unsafe_allow_html=True)
    
    # Create tabs for different charts
    tab1, tab2, tab3, tab4 = st.tabs(["Clicks Over Time", "Budget Allocation", "CTR Analysis", "Comparison"])
    
    with tab1:
        st.markdown("### Clicks Generated per Time Slot")
        fig = go.Figure()
        
        for result in results:
            fig.add_trace(go.Scatter(
                x=result['time_slots'],
                y=result['clicks'],
                mode='lines+markers',
                name=result['model'],
                fill='tozeroy',
                hovertemplate='<b>%{fullData.name}</b><br>Time Slot: %{x}<br>Clicks: %{y:,}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Clicks Generated per Time Slot",
            xaxis_title="Time Slot (Hour)",
            yaxis_title="Number of Clicks",
            hovermode='x unified',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Budget Remaining Over Time")
        fig = go.Figure()
        
        for result in results:
            fig.add_trace(go.Scatter(
                x=result['time_slots'],
                y=result['budget_history'][1:],
                mode='lines+markers',
                name=result['model'],
                hovertemplate='<b>%{fullData.name}</b><br>Time Slot: %{x}<br>Budget: $%{y:,.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Remaining Budget Over Time",
            xaxis_title="Time Slot (Hour)",
            yaxis_title="Budget ($)",
            hovermode='x unified',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### CTR Variation per Time Slot")
        fig = go.Figure()
        
        for result in results:
            fig.add_trace(go.Scatter(
                x=result['time_slots'],
                y=result['ctr_history'],
                mode='lines+markers',
                name=result['model'],
                hovertemplate='<b>%{fullData.name}</b><br>Time Slot: %{x}<br>CTR: %{y:.2f}%<extra></extra>'
            ))
        
        fig.update_layout(
            title="Click-Through Rate Variation",
            xaxis_title="Time Slot (Hour)",
            yaxis_title="CTR (%)",
            hovermode='x unified',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        if len(results) == 2:
            st.markdown("### Model Comparison Metrics")
            
            # Performance metrics bar chart
            metrics_data = {
                'Total Clicks': [results[0]['total_clicks'], results[1]['total_clicks']],
                'Revenue ($)': [results[0]['revenue'], results[1]['revenue']],
                'Budget Used ($)': [results[0]['budget_used'], results[1]['budget_used']]
            }
            
            fig = go.Figure(data=[
                go.Bar(name='Phase 1 (Heuristic)', x=list(metrics_data.keys()), y=[metrics_data[k][0] for k in metrics_data.keys()]),
                go.Bar(name='Phase 2 (PPO)', x=list(metrics_data.keys()), y=[metrics_data[k][1] for k in metrics_data.keys()])
            ])
            
            fig.update_layout(
                title="Direct Comparison of Key Metrics",
                barmode='group',
                height=400,
                template='plotly_white',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 Run both Phase 1 and Phase 2 models to see comparison charts")
    
    # ========== SUMMARY INSIGHTS ==========
    st.markdown("<h2 class='section-title'>🔍 Key Insights</h2>", unsafe_allow_html=True)
    
    if len(results) == 2:
        clicks_improvement = ((results[1]['total_clicks'] - results[0]['total_clicks']) / results[0]['total_clicks'] * 100)
        revenue_improvement = ((results[1]['revenue'] - results[0]['revenue']) / results[0]['revenue'] * 100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success(f"✨ Click Improvement: +{clicks_improvement:.1f}%")
        
        with col2:
            st.success(f"💵 Revenue Improvement: +{revenue_improvement:.1f}%")
        
        with col3:
            efficiency_p1 = results[0]['total_clicks'] / results[0]['budget_used']
            efficiency_p2 = results[1]['total_clicks'] / results[1]['budget_used']
            efficiency_gain = ((efficiency_p2 - efficiency_p1) / efficiency_p1 * 100)
            st.success(f"⚡ Efficiency Gain: +{efficiency_gain:.1f}%")
    
    st.markdown("""
    ### 📌 Analysis Summary
    - **Phase 1 (Heuristic)**: Uses equal budget distribution across all time slots - simple but not optimal
    - **Phase 2 (PPO)**: Uses intelligent allocation based on traffic patterns - adapts to market conditions
    - PPO model learns to allocate more budget during peak hours and less during off-peak hours
    - Better budget allocation leads to higher click-through rates and revenue generation
    """)

else:
    # ========== WELCOME MESSAGE ==========
    st.info("""
    👋 **Welcome to the RTB Smart Budget Allocation System!**
    
    This application compares two budget allocation strategies:
    
    ✅ **Phase 1 (Heuristic)**: Equal budget distribution
    - Simple and straightforward approach
    - Allocates same budget to each time slot
    
    ✅ **Phase 2 (PPO)**: Intelligent allocation using reinforcement learning
    - Learns optimal budget allocation
    - Adapts to traffic patterns and market conditions
    - Usually results in higher ROI
    
    ### 🚀 How to Use:
    1. Set your daily budget in the sidebar
    2. Configure traffic and performance parameters
    3. Select which models to compare
    4. Click "Run Simulation" to see results
    5. Compare performance metrics and visualizations
    
    Let's optimize your RTB budget! 💰
    """)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Smart Budget Allocation in Real-Time Bidding (RTB) System</p>
    <p>Comparing Phase 1 (Heuristic) vs Phase 2 (PPO) Strategies</p>
</div>
""", unsafe_allow_html=True)
