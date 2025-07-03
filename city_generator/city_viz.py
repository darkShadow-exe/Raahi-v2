import matplotlib.pyplot as plt
import numpy as np
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from city_generator.city_builder import CityBuilder

def visualize_city(city_data, title="City Layout"):
    fig, ax = plt.subplots(figsize=(12, 12))
    
    grid_size = city_data["grid_size"]
    zones = city_data["zones"]
    stations = city_data["stations"]
    connections = city_data.get("connections", [])
    routes = city_data.get("routes", [])
    
    # Zone colors from existing city module
    zone_colors = {
        "residential": "#90EE90",    # Light green
        "commercial": "#FFB6C1",     # Light pink
        "industrial": "#D3D3D3",     # Light gray
        "transit_hub": "#FFD700"     # Gold
    }
    
    # Mode colors from existing city module
    mode_colors = {
        "bus": "#FF4500",      # Orange red
        "metro": "#4169E1",    # Royal blue
        "tram": "#32CD32"      # Lime green
    }
    
    # Draw zones with better styling
    for zone in zones:
        color = zone_colors.get(zone["type"], "#FFFFFF")
        rect = plt.Rectangle((zone["x"]-0.4, zone["y"]-0.4), 0.8, 0.8, 
                           facecolor=color, alpha=0.3, edgecolor="none")
        ax.add_patch(rect)
    
    # Draw walking connections first (light gray dots)
    for conn in connections:
        s1 = next(s for s in stations if s["id"] == conn["from"])
        s2 = next(s for s in stations if s["id"] == conn["to"])
        
        x1, y1 = s1["x"], s1["y"]
        x2, y2 = s2["x"], s2["y"]
        
        ax.plot([x1, x2], [y1, y2], color="gray", linewidth=1, 
               alpha=0.3, linestyle=":", zorder=1)
    
    # Draw colored route lines
    for route in routes:
        route_stations = []
        for station_id in route["stations"]:
            station = next(s for s in stations if s["id"] == station_id)
            route_stations.append((station["x"], station["y"]))
        
        if len(route_stations) >= 2:
            xs, ys = zip(*route_stations)
            color = route.get("color", mode_colors.get(route["mode"], "#000000"))
            
            # Different line styles for different modes
            line_style = "-"
            if route["mode"] == "metro":
                line_style = "-"
                linewidth = 3
            elif route["mode"] == "tram":
                line_style = "--"
                linewidth = 2.5
            else:  # bus
                line_style = "-."
                linewidth = 2
                
            ax.plot(xs, ys, color=color, linewidth=linewidth, 
                   linestyle=line_style, alpha=0.8, zorder=3,
                   label=f"{route['mode'].title()} {route['id']}")
    
    # Station styling with different shapes and sizes
    for station in stations:
        x, y = station["x"], station["y"]
        mode = station["type"]
        color = mode_colors.get(mode, "#000000")
        
        # Different shapes for different modes
        if mode == "bus":
            marker = "o"
            size = 100
        elif mode == "metro":
            marker = "s"
            size = 120
        else:  # tram
            marker = "^"
            size = 110
        
        # Much larger size and special styling for transfer stations
        if station.get("is_transfer", False):
            size = size * 1.8
            # Draw transfer station with double ring
            ax.scatter(x, y, c="white", marker=marker, s=size, 
                      edgecolors="black", linewidth=3, zorder=6)
            ax.scatter(x, y, c=color, marker=marker, s=size*0.6, 
                      edgecolors="black", linewidth=1, zorder=7)
            # Add transfer label
            ax.annotate("TRANSFER", (x, y), xytext=(0, -25), 
                       textcoords="offset points", fontsize=7, 
                       ha="center", fontweight="bold", color="red")
        else:
            ax.scatter(x, y, c=color, marker=marker, s=size, 
                      edgecolors="black", linewidth=1, zorder=5)
        
        # Add station labels
        ax.annotate(station["id"].split("_")[1], (x, y), xytext=(5, 5), 
                   textcoords="offset points", fontsize=8, alpha=0.8,
                   fontweight="bold")
    
    # Add legends
    zone_handles = []
    for zone_type, color in zone_colors.items():
        if zone_type != "transit_hub":
            handle = plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.3, 
                                 label=zone_type.title())
            zone_handles.append(handle)
    
    mode_handles = []
    for mode, color in mode_colors.items():
        if mode == "bus":
            marker = "o"
        elif mode == "metro":
            marker = "s" 
        else:
            marker = "^"
        handle = plt.Line2D([0], [0], marker=marker, color="w", 
                          markerfacecolor=color, markersize=12, 
                          label=mode.title(), markeredgecolor="black")
        mode_handles.append(handle)
    
    # Add transfer station to legend
    transfer_handle = plt.Line2D([0], [0], marker="o", color="w", 
                                markerfacecolor="white", markersize=15, 
                                label="Transfer Station", markeredgecolor="black",
                                markeredgewidth=3)
    mode_handles.append(transfer_handle)
    
    zone_legend = ax.legend(handles=zone_handles, loc="upper left", 
                           bbox_to_anchor=(1.02, 1), title="Zones")
    mode_legend = ax.legend(handles=mode_handles, loc="upper left", 
                           bbox_to_anchor=(1.02, 0.6), title="Transit")
    ax.add_artist(zone_legend)
    
    ax.set_xlim(-0.5, grid_size - 0.5)
    ax.set_ylim(-0.5, grid_size - 0.5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=16, fontweight="bold")
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    print("City Generator & Visualizer")
    print("1. Generate new city")
    print("2. Load existing city") 
    print("3. Generate batch")
    print("4. Exit")
    
    choice = input("Choose option (1-4): ")
    
    # Data directory relative to project root
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    if choice == "1":
        grid_size = int(input("Grid size (4-20): ") or "8")
        builder = CityBuilder(grid_size)
        city = builder.generate_random_city()
        
        filename = input("Save as (default: new_city.json): ") or "new_city.json"
        builder.save_city(city, filename)
        
        print(f"City saved to data/{filename}")
        visualize_city(city, f"Generated City ({grid_size}x{grid_size})")
        
    elif choice == "2":
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
            if files:
                print("Available cities:")
                for i, f in enumerate(files):
                    print(f"{i+1}. {f}")
                
                try:
                    idx = int(input("Select file: ")) - 1
                    if 0 <= idx < len(files):
                        with open(f"{data_dir}/{files[idx]}", "r") as f:
                            city = json.load(f)
                        visualize_city(city, f"City: {files[idx]}")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
            else:
                print("No city files found")
        else:
            print("Data directory not found")
            
    elif choice == "3":
        count = int(input("Number of cities (default: 5): ") or "5")
        grid_size = int(input("Grid size (default: 8): ") or "8")
        
        builder = CityBuilder(grid_size)
        builder.generate_batch_cities(count)
        print(f"Generated {count} cities in data/")
        
    elif choice == "4":
        print("Exit")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    main()
