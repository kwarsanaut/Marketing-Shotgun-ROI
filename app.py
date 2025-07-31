import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="Marketing ROI Dashboard - ERP POS System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .segment-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

class MarketingROIDashboard:
    def __init__(self):
        # Market data for Indonesian F&B segments
        self.market_data = {
            "Coffee Shops": {
                "market_size": 45000,
                "avg_deal_value": 15000000,  # Rp 15jt
                "channels": {
                    "Word of Mouth": {"conversion_rate": 0.25, "cost_per_lead": 50000},
                    "Instagram Ads": {"conversion_rate": 0.12, "cost_per_lead": 75000},
                    "Google Ads": {"conversion_rate": 0.08, "cost_per_lead": 125000},
                    "Partnership": {"conversion_rate": 0.22, "cost_per_lead": 85000}
                }
            },
            "Casual Dining": {
                "market_size": 25000,
                "avg_deal_value": 35000000,  # Rp 35jt
                "channels": {
                    "Word of Mouth": {"conversion_rate": 0.20, "cost_per_lead": 75000},
                    "Instagram Ads": {"conversion_rate": 0.10, "cost_per_lead": 100000},
                    "Google Ads": {"conversion_rate": 0.15, "cost_per_lead": 150000},
                    "Partnership": {"conversion_rate": 0.25, "cost_per_lead": 120000}
                }
            },
            "Warung/Street Food": {
                "market_size": 180000,
                "avg_deal_value": 8000000,  # Rp 8jt
                "channels": {
                    "Word of Mouth": {"conversion_rate": 0.30, "cost_per_lead": 25000},
                    "Instagram Ads": {"conversion_rate": 0.08, "cost_per_lead": 40000},
                    "Google Ads": {"conversion_rate": 0.05, "cost_per_lead": 60000},
                    "Partnership": {"conversion_rate": 0.18, "cost_per_lead": 45000}
                }
            },
            "Food Courts": {
                "market_size": 8000,
                "avg_deal_value": 75000000,  # Rp 75jt
                "channels": {
                    "Word of Mouth": {"conversion_rate": 0.15, "cost_per_lead": 150000},
                    "Instagram Ads": {"conversion_rate": 0.08, "cost_per_lead": 200000},
                    "Google Ads": {"conversion_rate": 0.12, "cost_per_lead": 250000},
                    "Partnership": {"conversion_rate": 0.28, "cost_per_lead": 180000}
                }
            },
            "Cloud Kitchen": {
                "market_size": 12000,
                "avg_deal_value": 25000000,  # Rp 25jt
                "channels": {
                    "Word of Mouth": {"conversion_rate": 0.18, "cost_per_lead": 80000},
                    "Instagram Ads": {"conversion_rate": 0.15, "cost_per_lead": 90000},
                    "Google Ads": {"conversion_rate": 0.20, "cost_per_lead": 110000},
                    "Partnership": {"conversion_rate": 0.22, "cost_per_lead": 100000}
                }
            }
        }
    
    def calculate_channel_efficiency(self, segment, channel):
        """Calculate channel efficiency (conversion rate / cost per lead)"""
        channel_data = self.market_data[segment]["channels"][channel]
        return channel_data["conversion_rate"] / (channel_data["cost_per_lead"] / 1000000)
    
    def simulate_diminishing_returns(self, base_conversion, budget_allocated, optimal_budget):
        """Simulate diminishing returns effect"""
        if budget_allocated <= optimal_budget:
            return base_conversion
        else:
            excess_factor = (budget_allocated - optimal_budget) / optimal_budget
            diminishing_factor = 1 / (1 + 0.5 * excess_factor)
            return base_conversion * diminishing_factor
    
    def optimize_budget_allocation(self, total_budget, selected_segments):
        """Smart budget allocation based on channel efficiency"""
        allocations = {}
        
        # Calculate efficiency scores for all channels in selected segments
        efficiency_scores = []
        for segment in selected_segments:
            for channel in self.market_data[segment]["channels"]:
                efficiency = self.calculate_channel_efficiency(segment, channel)
                efficiency_scores.append({
                    'segment': segment,
                    'channel': channel,
                    'efficiency': efficiency,
                    'market_size': self.market_data[segment]["market_size"],
                    'avg_deal': self.market_data[segment]["avg_deal_value"]
                })
        
        # Sort by efficiency and allocate budget
        efficiency_scores.sort(key=lambda x: x['efficiency'], reverse=True)
        
        remaining_budget = total_budget
        for item in efficiency_scores:
            if remaining_budget <= 0:
                break
            
            # Allocate budget based on efficiency and market potential
            market_weight = min(item['market_size'] / 50000, 1.0)  # Normalize market size
            suggested_allocation = min(
                remaining_budget * 0.3,  # Max 30% per channel
                total_budget * market_weight * 0.15  # Market-weighted allocation
            )
            
            key = f"{item['segment']} - {item['channel']}"
            allocations[key] = {
                'budget': suggested_allocation,
                'efficiency': item['efficiency'],
                'segment': item['segment'],
                'channel': item['channel']
            }
            remaining_budget -= suggested_allocation
        
        return allocations
    
    def calculate_roi_metrics(self, budget_allocation, timeline_months=12):
        """Calculate comprehensive ROI metrics"""
        total_leads = 0
        total_conversions = 0
        total_revenue = 0
        total_cost = sum(allocation['budget'] for allocation in budget_allocation.values())
        
        channel_performance = []
        
        for key, allocation in budget_allocation.items():
            segment = allocation['segment']
            channel = allocation['channel']
            budget = allocation['budget']
            
            if budget > 0:
                # Get channel data
                channel_data = self.market_data[segment]["channels"][channel]
                cost_per_lead = channel_data["cost_per_lead"]
                base_conversion_rate = channel_data["conversion_rate"]
                avg_deal_value = self.market_data[segment]["avg_deal_value"]
                
                # Calculate leads and conversions
                leads = budget / cost_per_lead
                
                # Apply diminishing returns
                optimal_budget = self.market_data[segment]["market_size"] * cost_per_lead * 0.05
                adjusted_conversion_rate = self.simulate_diminishing_returns(
                    base_conversion_rate, budget, optimal_budget
                )
                
                conversions = leads * adjusted_conversion_rate
                revenue = conversions * avg_deal_value * timeline_months
                
                total_leads += leads
                total_conversions += conversions
                total_revenue += revenue
                
                channel_performance.append({
                    'segment': segment,
                    'channel': channel,
                    'budget': budget,
                    'leads': leads,
                    'conversions': conversions,
                    'revenue': revenue,
                    'roi': (revenue - budget) / budget * 100 if budget > 0 else 0,
                    'efficiency': allocation['efficiency']
                })
        
        # Calculate overall metrics
        overall_roi = (total_revenue - total_cost) / total_cost * 100 if total_cost > 0 else 0
        market_penetration = (total_conversions / sum(data["market_size"] for data in self.market_data.values())) * 100
        
        return {
            'total_leads': total_leads,
            'total_conversions': total_conversions,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'overall_roi': overall_roi,
            'market_penetration': market_penetration,
            'channel_performance': channel_performance
        }

def format_currency(amount):
    """Format currency in Indonesian Rupiah"""
    return f"Rp {amount:,.0f}"

def format_number(number):
    """Format large numbers with K, M suffixes"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return f"{number:.0f}"

def main():
    dashboard = MarketingROIDashboard()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Marketing ROI Dashboard - ERP POS System</h1>', unsafe_allow_html=True)
    st.markdown("**Optimizing Marketing Investment for Indonesian F&B Market**")
    
    # Sidebar controls
    st.sidebar.header("🎯 Campaign Configuration")
    
    # Budget slider
    total_budget = st.sidebar.slider(
        "Total Marketing Budget (Rp)",
        min_value=100000,
        max_value=100000000,
        value=10000000,
        step=500000,
        format="%d"
    )
    
    # Segment selection
    st.sidebar.subheader("Target Segments")
    selected_segments = []
    for segment in dashboard.market_data.keys():
        if st.sidebar.checkbox(segment, value=True):
            selected_segments.append(segment)
    
    # Timeline selection
    timeline = st.sidebar.selectbox(
        "Projection Timeline",
        [3, 6, 12, 24],
        index=2,
        format_func=lambda x: f"{x} months"
    )
    
    if not selected_segments:
        st.error("Please select at least one target segment!")
        return
    
    # Calculate optimal budget allocation
    budget_allocation = dashboard.optimize_budget_allocation(total_budget, selected_segments)
    roi_metrics = dashboard.calculate_roi_metrics(budget_allocation, timeline)
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Performance Analysis", "🎯 Channel Optimization", "📋 Detailed Report"])
    
    with tab1:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall ROI",
                f"{roi_metrics['overall_roi']:.1f}%",
                delta=f"{roi_metrics['overall_roi'] - 150:.1f}%" if roi_metrics['overall_roi'] > 150 else None
            )
        
        with col2:
            st.metric(
                "Expected Clients",
                f"{roi_metrics['total_conversions']:.0f}",
                delta=f"{roi_metrics['total_conversions'] - 50:.0f}" if roi_metrics['total_conversions'] > 50 else None
            )
        
        with col3:
            st.metric(
                "Projected Revenue",
                format_currency(roi_metrics['total_revenue']),
                delta=format_currency(roi_metrics['total_revenue'] - total_budget)
            )
        
        with col4:
            st.metric(
                "Market Penetration",
                f"{roi_metrics['market_penetration']:.2f}%",
                delta=f"{roi_metrics['market_penetration'] - 0.1:.2f}%" if roi_metrics['market_penetration'] > 0.1 else None
            )
        
        # Budget allocation pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Budget allocation
            allocation_data = []
            for key, allocation in budget_allocation.items():
                if allocation['budget'] > 0:
                    allocation_data.append({
                        'Channel': key,
                        'Budget': allocation['budget'],
                        'Percentage': allocation['budget'] / total_budget * 100
                    })
            
            if allocation_data:
                df_allocation = pd.DataFrame(allocation_data)
                fig_pie = px.pie(
                    df_allocation, 
                    values='Budget', 
                    names='Channel',
                    title="Budget Allocation by Channel",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Channel performance bar chart
            if roi_metrics['channel_performance']:
                df_performance = pd.DataFrame(roi_metrics['channel_performance'])
                df_performance['Channel_Segment'] = df_performance['segment'] + ' - ' + df_performance['channel']
                
                fig_bar = px.bar(
                    df_performance,
                    x='Channel_Segment',
                    y='roi',
                    title="ROI by Channel",
                    color='roi',
                    color_continuous_scale='RdYlGn'
                )
                fig_bar.update_xaxes(tickangle=45)
                fig_bar.update_layout(xaxis_title="Channel", yaxis_title="ROI (%)")
                st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        st.subheader("📈 Performance Analysis")
        
        # Revenue projection timeline
        months = list(range(1, timeline + 1))
        cumulative_revenue = []
        monthly_revenue = roi_metrics['total_revenue'] / timeline
        
        for month in months:
            # Simulate growth curve
            growth_factor = 1 - np.exp(-month / (timeline * 0.3))
            cumulative_revenue.append(monthly_revenue * month * growth_factor)
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=months,
            y=cumulative_revenue,
            mode='lines+markers',
            name='Projected Revenue',
            line=dict(color='#1f77b4', width=3)
        ))
        
        # Add break-even line
        break_even = [total_budget] * len(months)
        fig_timeline.add_trace(go.Scatter(
            x=months,
            y=break_even,
            mode='lines',
            name='Break-even',
            line=dict(color='red', dash='dash')
        ))
        
        fig_timeline.update_layout(
            title=f"Revenue Projection - {timeline} Month Timeline",
            xaxis_title="Month",
            yaxis_title="Revenue (Rp)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Channel efficiency ranking
        st.subheader("🏆 Channel Efficiency Ranking")
        if roi_metrics['channel_performance']:
            df_efficiency = pd.DataFrame(roi_metrics['channel_performance'])
            df_efficiency = df_efficiency.sort_values('efficiency', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_efficiency = px.bar(
                    df_efficiency.head(10),
                    x='efficiency',
                    y=[f"{row['segment']} - {row['channel']}" for _, row in df_efficiency.head(10).iterrows()],
                    orientation='h',
                    title="Top 10 Most Efficient Channels",
                    color='efficiency',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_efficiency, use_container_width=True)
            
            with col2:
                # Performance metrics table
                st.subheader("Channel Performance Summary")
                summary_df = df_efficiency[['segment', 'channel', 'conversions', 'revenue', 'roi']].head(10)
                summary_df['revenue'] = summary_df['revenue'].apply(format_currency)
                summary_df['roi'] = summary_df['roi'].apply(lambda x: f"{x:.1f}%")
                summary_df.columns = ['Segment', 'Channel', 'Conversions', 'Revenue', 'ROI']
                st.dataframe(summary_df, use_container_width=True)
    
    with tab3:
        st.subheader("🎯 Channel Optimization")
        
        # Diminishing returns simulation
        st.subheader("Diminishing Returns Analysis")
        
        selected_segment = st.selectbox("Select Segment for Analysis", selected_segments)
        selected_channel = st.selectbox(
            "Select Channel", 
            list(dashboard.market_data[selected_segment]["channels"].keys())
        )
        
        # Simulate different budget levels
        base_budget = budget_allocation.get(f"{selected_segment} - {selected_channel}", {}).get('budget', 1000000)
        budget_range = np.linspace(base_budget * 0.1, base_budget * 3, 50)
        
        roi_curve = []
        conversion_curve = []
        
        for test_budget in budget_range:
            # Simulate single channel performance
            test_allocation = {f"{selected_segment} - {selected_channel}": {
                'budget': test_budget,
                'segment': selected_segment,
                'channel': selected_channel,
                'efficiency': dashboard.calculate_channel_efficiency(selected_segment, selected_channel)
            }}
            
            test_metrics = dashboard.calculate_roi_metrics(test_allocation, timeline)
            roi_curve.append(test_metrics['overall_roi'])
            conversion_curve.append(test_metrics['total_conversions'])
        
        # Plot diminishing returns
        fig_returns = make_subplots(
            rows=1, cols=2,
            subplot_titles=('ROI vs Budget', 'Conversions vs Budget')
        )
        
        fig_returns.add_trace(
            go.Scatter(x=budget_range, y=roi_curve, name='ROI %', line=dict(color='blue')),
            row=1, col=1
        )
        
        fig_returns.add_trace(
            go.Scatter(x=budget_range, y=conversion_curve, name='Conversions', line=dict(color='green')),
            row=1, col=2
        )
        
        # Add current budget marker
        current_budget = budget_allocation.get(f"{selected_segment} - {selected_channel}", {}).get('budget', 0)
        if current_budget > 0:
            current_idx = np.argmin(np.abs(budget_range - current_budget))
            fig_returns.add_vline(x=current_budget, line_dash="dash", line_color="red", 
                                 annotation_text="Current Budget", row=1, col=1)
            fig_returns.add_vline(x=current_budget, line_dash="dash", line_color="red", 
                                 annotation_text="Current Budget", row=1, col=2)
        
        fig_returns.update_layout(title=f"Diminishing Returns Analysis - {selected_segment} {selected_channel}")
        st.plotly_chart(fig_returns, use_container_width=True)
        
        # Optimization recommendations
        st.subheader("💡 Optimization Recommendations")
        
        optimal_idx = np.argmax(roi_curve)
        optimal_budget = budget_range[optimal_idx]
        optimal_roi = roi_curve[optimal_idx]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Budget", format_currency(current_budget))
            
        with col2:
            st.metric("Optimal Budget", format_currency(optimal_budget))
            
        with col3:
            budget_change = optimal_budget - current_budget
            st.metric("Recommended Change", format_currency(abs(budget_change)), 
                     delta=f"{'Increase' if budget_change > 0 else 'Decrease'}")
    
    with tab4:
        st.subheader("📋 Detailed Report")
        
        # Export functionality
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("📥 Export Report", type="primary"):
                # Create comprehensive report data
                report_data = {
                    'campaign_config': {
                        'total_budget': total_budget,
                        'selected_segments': selected_segments,
                        'timeline_months': timeline
                    },
                    'roi_metrics': roi_metrics,
                    'budget_allocation': budget_allocation,
                    'generated_at': datetime.now().isoformat()
                }
                
                # Convert to JSON for download
                report_json = json.dumps(report_data, indent=2, default=str)
                st.download_button(
                    label="Download JSON Report",
                    data=report_json,
                    file_name=f"marketing_roi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # Detailed performance table
        if roi_metrics['channel_performance']:
            st.subheader("Channel Performance Details")
            df_detailed = pd.DataFrame(roi_metrics['channel_performance'])
            
            # Format currency columns
            df_detailed['budget_formatted'] = df_detailed['budget'].apply(format_currency)
            df_detailed['revenue_formatted'] = df_detailed['revenue'].apply(format_currency)
            df_detailed['roi_formatted'] = df_detailed['roi'].apply(lambda x: f"{x:.1f}%")
            df_detailed['leads_formatted'] = df_detailed['leads'].apply(lambda x: f"{x:.0f}")
            df_detailed['conversions_formatted'] = df_detailed['conversions'].apply(lambda x: f"{x:.0f}")
            
            # Display formatted table
            display_df = df_detailed[['segment', 'channel', 'budget_formatted', 'leads_formatted', 
                                    'conversions_formatted', 'revenue_formatted', 'roi_formatted']]
            display_df.columns = ['Segment', 'Channel', 'Budget', 'Leads', 'Conversions', 'Revenue', 'ROI']
            
            st.dataframe(display_df, use_container_width=True)
        
        # Market insights
        st.subheader("📊 Market Insights & Recommendations")
        
        insights = []
        
        # ROI insights
        if roi_metrics['overall_roi'] > 200:
            insights.append("🎯 **Excellent ROI**: Your campaign is projected to deliver exceptional returns. Consider scaling up investment.")
        elif roi_metrics['overall_roi'] > 100:
            insights.append("✅ **Good ROI**: Solid returns expected. Look for optimization opportunities in underperforming channels.")
        else:
            insights.append("⚠️ **Low ROI**: Consider reallocating budget to higher-performing channels or segments.")
        
        # Market penetration insights
        if roi_metrics['market_penetration'] < 0.1:
            insights.append("📈 **Low Market Penetration**: Significant growth opportunity available. Consider expanding reach.")
        elif roi_metrics['market_penetration'] > 1.0:
            insights.append("🏆 **High Market Penetration**: Market saturation risk. Focus on customer retention and premium segments.")
        
        # Channel-specific insights
        if roi_metrics['channel_performance']:
            best_channel = max(roi_metrics['channel_performance'], key=lambda x: x['roi'])
            insights.append(f"🥇 **Top Performer**: {best_channel['segment']} - {best_channel['channel']} with {best_channel['roi']:.1f}% ROI")
            
            worst_channel = min(roi_metrics['channel_performance'], key=lambda x: x['roi'])
            if worst_channel['roi'] < 50:
                insights.append(f"🔴 **Underperformer**: {worst_channel['segment']} - {worst_channel['channel']} needs attention or budget reallocation")
        
        for insight in insights:
            st.markdown(insight)
        
        # Action items
        st.subheader("🎯 Recommended Actions")
        st.markdown("""
        1. **Immediate Actions** (Next 30 days):
           - Implement budget allocation as recommended above
           - Set up tracking for key performance metrics
           - Launch campaigns in top-performing channels first
        
        2. **Short-term Optimizations** (Next 90 days):
           - A/B test creative variations in high-ROI channels
           - Refine targeting based on initial performance data
           - Scale successful campaigns gradually
        
        3. **Long-term Strategy** (6+ months):
           - Develop channel-specific content strategies
           - Build partnerships with high-performing channels
           - Expand to additional market segments based on success
        """)

if __name__ == "__main__":
    main()
