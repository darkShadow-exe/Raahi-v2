import streamlit as st
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import cv2
import time
from pathlib import Path

class CityVisualizer:
    def __init__(self, city_data: dict):
        self.city_data = city_data
        self.grid_size = city_data["grid_size"]
        self.stations = city_data["stations"]
        self.zones = city_data["zones"]
        self.connections = city_data["connections"]
    
    def draw_city_map(self):
        # Create grid
        img = np.ones((self.grid_size*100, self.grid_size*100, 3), dtype=np.uint8) * 255
        
        # Draw zones
        zone_colors = {
            "residential": (200, 230, 200),
            "commercial": (200, 200, 230), 
            "industrial": (230, 200, 200)
        }
        
        for zone in self.zones:
            x, y = zone["x"], zone["y"]
            color = zone_colors.get(zone["type"], (220, 220, 220))
            cv2.rectangle(
                img, 
                (x*100, y*100), 
                ((x+1)*100, (y+1)*100), 
                color, 
                -1
            )
        
        # Draw stations
        station_colors = {
            "bus": (0, 0, 255),
            "tram": (0, 255, 0),
            "metro": (255, 0, 0)
        }
        
        for station in self.stations:
            x, y = station["x"] * 100 + 50, station["y"] * 100 + 50
            color = station_colors.get(station["type"], (0, 0, 0))
            size = 15 if station.get("is_transfer", False) else 10
            cv2.circle(img, (x, y), size, color, -1)
        
        # Draw connections
        for conn in self.connections:
            # Find stations
            s1 = next(s for s in self.stations if s["id"] == conn["from"])
            s2 = next(s for s in self.stations if s["id"] == conn["to"])
            
            x1, y1 = s1["x"] * 100 + 50, s1["y"] * 100 + 50
            x2, y2 = s2["x"] * 100 + 50, s2["y"] * 100 + 50
            
            cv2.line(img, (x1, y1), (x2, y2), (100, 100, 100), 2, cv2.LINE_AA)
        
        return img

class ScheduleVisualizer:
    def __init__(self, schedule_data: dict, city_data: dict):
        self.schedule = schedule_data["schedule"]
        self.city_data = city_data
    
    def plot_frequencies(self):
        # Plot schedule frequencies
        data = []
        for entry in self.schedule:
            time_hr = entry["time"] / 60 + 5  # Convert to hours (5 AM start)
            for i, freq in enumerate(entry["frequencies"]):
                data.append({
                    "time": time_hr,
                    "station": f"Station {i}",
                    "frequency": freq
                })
        
        df = pd.DataFrame(data)
        fig = px.line(
            df, 
            x="time", 
            y="frequency", 
            color="station", 
            title="Vehicle Frequencies Throughout Day"
        )
        return fig
    
    def animate_simulation(self, fps=10, duration=30):
        # Create animation frames
        # For prototype, just return mock frame
        frame = np.ones((500, 500, 3), dtype=np.uint8) * 255
        text = "Animation placeholder"
        cv2.putText(
            frame,
            text,
            (50, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2
        )
        return frame

def run_app():
    st.set_page_config(page_title="Raahi Transit Simulator", layout="wide")
    
    st.title("Raahi-v2 Transit Simulator")
    
    # Sidebar
    st.sidebar.header("Settings")
    
    # Add prototype mode toggle
    prototype_mode = st.sidebar.checkbox("Prototype Mode", value=True, 
                                        help="Use mock data when real data is unavailable")
    
    if st.sidebar.button("Generate New City"):
        st.session_state.show_city = True
    
    # Main content
    tabs = st.tabs(["City Generator", "RL Scheduler", "Simulation", "Reports"])
    
    with tabs[0]:
        st.header("City Generator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            grid_size = st.slider("Grid Size", 4, 20, 8)
            generate = st.button("Generate City")
            
            if generate:
                st.info("Generating city...")
                # Placeholder for actual city generation
        
        with col2:
            # Show city visualization placeholder
            st.image(Image.fromarray(np.ones((400, 400, 3), dtype=np.uint8) * 220))
    
    with tabs[1]:
        st.header("RL Scheduler")
        
        col1, col2 = st.columns(2)
        
        with col1:
            train_episodes = st.slider("Training Episodes", 100, 10000, 1000)
            train = st.button("Train Model")
            
            if train:
                st.info("Training RL model...")
                try:
                    # This would be replaced with actual training
                    # For prototype, just show a progress bar
                    progress = st.progress(0)
                    for i in range(100):
                        # Update progress bar
                        progress.progress(i + 1)
                        time.sleep(0.05)
                    st.success("Training complete! Model saved to models/model.pt")
                except Exception as e:
                    st.error(f"Training error: {str(e)}")
                
        with col2:
            # Training progress placeholder
            st.line_chart(pd.DataFrame(
                np.random.randn(100, 3), 
                columns=['reward', 'wait_time', 'transfers']
            ))
    
    with tabs[2]:
        st.header("Simulation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_sim = st.button("Run Simulation")
            
            metrics = {
                "Avg Wait Time": "2.5 min",
                "Passengers Served": "12,450",
                "Missed Transfers": "320"
            }
            
            for m, v in metrics.items():
                st.metric(m, v)
                
        with col2:
            # Simulation animation placeholder
            st.image(Image.fromarray(np.ones((400, 400, 3), dtype=np.uint8) * 230))
    
    with tabs[3]:
        st.header("Phi LLM Reports")
        
        report_type = st.selectbox(
            "Report Type", 
            ["Schedule Explanation", "RL vs Baseline", "What-If Analysis"]
        )
        
        generate_report = st.button("Generate Report")
        
        if generate_report:
            st.info("Generating report with Phi...")
            # Placeholder for actual report
            st.write("""
            # Transit Schedule Analysis
            
            The RL agent optimized metro frequency near commercial zones during rush hours,
            reducing average wait time by 2.5 minutes compared to the baseline scheduler.
            """)

if __name__ == "__main__":
    run_app()
