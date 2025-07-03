import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from city_generator.city_builder import CityBuilder

def visualize_city(city_data, title="City Layout"):
    fig, ax = plt.subplots(figsize=(12, 12))
    
    grid_size = city_data["grid_size"]
    zones = city_data["zones"]
    stations = city_data["stations"]
    connections = city_data["connections"]
    
    # Zone colors from existing city module
    zone_colors = {
        "residential": "#90EE90",    # Light green
        "commercial": "#FFB6C1",     # Light pink
        "industrial": "#D3D3D3",     # Light gray
    }
    
    # Mode colors from existing city module
    mode_colors = {
        "bus": "#FF4500",      # Orange red
        "metro": "#4169E1",    # Royal blue
        "tram": "#32CD32"      # Lime green
    }
    
    # Draw zones with styling
    for zone in zones:
        color = zone_colors.get(zone["type"], "#FFFFFF")
        rect = plt.Rectangle((zone["x"]-0.4, zone["y"]-0.4), 0.8, 0.8, 
                           facecolor=color, alpha=0.3, edgecolor="none")
        ax.add_patch(rect)
    
    # Draw connections
    for conn in connections:
        s1 = next(s for s in stations if s["id"] == conn["from"])
        s2 = next(s for s in stations if s["id"] == conn["to"])
        
        x1, y1 = s1["x"], s1["y"]
        x2, y2 = s2["x"], s2["y"]
        
        ax.plot([x1, x2], [y1, y2], color="gray", linewidth=1, 
               alpha=0.3, linestyle=":", zorder=1)
    
    # Draw stations
    for station in stations:
        x, y = station["x"], station["y"]
        mode = station["type"]
        color = mode_colors.get(mode, "#000000")
        
        # Different shapes for different modes
        if mode == "bus":
            marker = "o"
            size = 80
        elif mode == "metro":
            marker = "s"
            size = 100
        else:  # tram
            marker = "^"
            size = 120
        
        # Larger size for transfer stations
        if station.get("is_transfer", False):
            size = size * 1.3
        
        ax.scatter(x, y, c=color, marker=marker, s=size, 
                  edgecolors="black", linewidth=1, zorder=5)
        
        # Add station labels
        ax.annotate(station["id"].split("_")[1], (x, y), xytext=(5, 5), 
                   textcoords="offset points", fontsize=6, alpha=0.7)
    
    # Add legends
    zone_handles = []
    for zone_type, color in zone_colors.items():
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
                          markerfacecolor=color, markersize=10, 
                          label=mode.title(), markeredgecolor="black")
        mode_handles.append(handle)
    
    zone_legend = ax.legend(handles=zone_handles, loc="upper left", 
                           bbox_to_anchor=(1.02, 1), title="Zones")
    mode_legend = ax.legend(handles=mode_handles, loc="upper left", 
                           bbox_to_anchor=(1.02, 0.7), title="Transit Modes")
    ax.add_artist(zone_legend)
    
    ax.set_xlim(-0.5, grid_size - 0.5)
    ax.set_ylim(-0.5, grid_size - 0.5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=16, fontweight="bold")
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    print("City Generator Visualizer")
    print("------------------------")
    
    while True:
        print("\nOptions:")
        print("1. Generate new random city")
        print("2. Load existing city from file")
        print("3. Generate batch of cities")
        print("4. Exit")
        
        choice = input("\nChoice (1-4): ")
        
        if choice == "1":
            # Get grid size
            try:
                grid_size = int(input("Enter grid size (4-20): "))
                grid_size = max(4, min(20, grid_size))
            except:
                grid_size = 8
                print(f"Using default grid size: {grid_size}")
            
            # Generate city
            builder = CityBuilder(grid_size=grid_size)
            city = builder.generate_random_city()
            
            # Save city
            filename = input("Enter filename to save (e.g. my_city.json): ")
            if not filename:
                filename = "new_city.json"
            if not filename.endswith(".json"):
                filename += ".json"
                
            builder.save_city(city, filename)
            print(f"City saved as data/{filename}")
            
            # Visualize
            visualize_city(city)
            
        elif choice == "2":
            # List available city files
            print("\nAvailable city files:")
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            city_files = [f for f in os.listdir(data_path) if f.endswith(".json")]
            
            for i, file in enumerate(city_files):
                print(f"{i+1}. {file}")
            
            try:
                file_idx = int(input("\nEnter file number to load: ")) - 1
                if 0 <= file_idx < len(city_files):
                    filename = city_files[file_idx]
                    
                    # Load city
                    builder = CityBuilder()
                    city = builder.load_city(filename)
                    print(f"Loaded {filename}")
                    
                    # Visualize
                    visualize_city(city)
                else:
                    print("Invalid file number")
            except Exception as e:
                print(f"Error loading file: {e}")
            
        elif choice == "3":
            # Generate batch
            try:
                count = int(input("How many cities to generate (1-100): "))
                count = max(1, min(100, count))
            except:
                count = 5
                print(f"Using default count: {count}")
                
            print(f"Generating {count} cities...")
            builder = CityBuilder()
            builder.generate_batch_cities(count=count)
            print(f"Generated {count} cities in the data/ folder")
            
        elif choice == "4":
            print("Exiting...")
            sys.exit(0)
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    # Make sure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    main()
