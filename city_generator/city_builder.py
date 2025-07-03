import json
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple
from collections import defaultdict, deque

@dataclass
class Station:
    id: str
    x: int
    y: int
    station_type: str  # bus, tram, metro
    is_transfer: bool = False

@dataclass
class Zone:
    x: int
    y: int
    zone_type: str  # residential, commercial, industrial

class CityBuilder:
    def __init__(self, grid_size: int = 8):
        self.grid_size = grid_size
        self.zone_types = ["residential", "commercial", "industrial"]
        self.station_types = ["bus", "tram", "metro"]
    
    def generate_random_city(self) -> Dict:
        zones = self._generate_zones()
        stations = self._generate_stations()
        connections = self._generate_connections(stations)
        routes = self._generate_routes(stations)
        
        return {
            "grid_size": self.grid_size,
            "zones": zones,
            "stations": stations,
            "connections": connections,
            "routes": routes
        }
    
    def _generate_zones(self) -> List[Dict]:
        zones = []
        grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Create zone clusters instead of random placement
        cluster_size = max(2, self.grid_size // 3)
        
        for zone_type in self.zone_types:
            # Pick random center for each zone type
            center_x = random.randint(cluster_size//2, self.grid_size - cluster_size//2 - 1)
            center_y = random.randint(cluster_size//2, self.grid_size - cluster_size//2 - 1)
            
            # Fill cluster around center
            for dx in range(-cluster_size//2, cluster_size//2 + 1):
                for dy in range(-cluster_size//2, cluster_size//2 + 1):
                    x, y = center_x + dx, center_y + dy
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        if grid[x][y] is None:
                            grid[x][y] = zone_type
        
        # Fill remaining cells with random zones
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if grid[x][y] is None:
                    grid[x][y] = random.choice(self.zone_types)
                zones.append({"x": x, "y": y, "type": grid[x][y]})
        
        return zones
    
    def _generate_stations(self) -> List[Dict]:
        stations = []
        station_positions = []
        
        # Calculate station counts based on grid size with better scaling
        base_density = 0.25  # Base stations per grid cell
        total_area = self.grid_size * self.grid_size
        
        station_counts = {
            "metro": max(3, int(total_area * base_density * 0.3)),
            "tram": max(4, int(total_area * base_density * 0.35)), 
            "bus": max(5, int(total_area * base_density * 0.4))
        }
        
        station_id = 0
        
        # Minimum distance between stations to prevent clustering
        min_distance = max(2, self.grid_size // 6)
        
        def is_too_close(x, y, existing_positions, min_dist):
            """Check if position is too close to existing stations."""
            for ex_x, ex_y in existing_positions:
                if abs(x - ex_x) + abs(y - ex_y) < min_dist:
                    return True
            return False
        
        def find_good_position(existing_positions, min_dist, max_attempts=50):
            """Find a position that's not too close to existing stations."""
            for _ in range(max_attempts):
                x = random.randint(0, self.grid_size - 1)
                y = random.randint(0, self.grid_size - 1)
                if not is_too_close(x, y, existing_positions, min_dist):
                    return x, y
            # If we can't find a good position, return a random one
            return random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
        
        # First place metro stations (major hubs) with good distribution
        for _ in range(station_counts["metro"]):
            x, y = find_good_position(station_positions, min_distance)
            station_positions.append((x, y))
            
            stations.append({
                "id": f"station_{station_id}",
                "x": x, "y": y,
                "type": "metro",
                "is_transfer": False  # Will be set later in connections
            })
            station_id += 1
        
        # Place tram stations (some at metro locations for transfers)
        transfer_chance = 0.4  # 40% chance of placing at existing metro location
        for i in range(station_counts["tram"]):
            if i < len(station_positions) and random.random() < transfer_chance:
                # Place at existing metro location for transfer
                x, y = station_positions[i]
            else:
                # Place at new location with smaller minimum distance
                x, y = find_good_position(station_positions, min_distance // 2)
                station_positions.append((x, y))
            
            stations.append({
                "id": f"station_{station_id}",
                "x": x, "y": y,
                "type": "tram",
                "is_transfer": False
            })
            station_id += 1
        
        # Place bus stations (more distributed, some at major hubs)
        for i in range(station_counts["bus"]):
            if i < len(station_positions) and random.random() < 0.3:
                # Place at existing location for transfer
                x, y = station_positions[i % len(station_positions)]
            else:
                # Place at new location with even smaller minimum distance
                x, y = find_good_position(station_positions, min_distance // 3)
                station_positions.append((x, y))
            
            stations.append({
                "id": f"station_{station_id}",
                "x": x, "y": y,
                "type": "bus",
                "is_transfer": False
            })
            station_id += 1
        
        return stations
    
    def _generate_connections(self, stations: List[Dict]) -> List[Dict]:
        connections = []
        
        # Create transfer connections for co-located stations
        location_groups = {}
        for station in stations:
            loc = (station["x"], station["y"])
            if loc not in location_groups:
                location_groups[loc] = []
            location_groups[loc].append(station)
        
        # Mark transfer stations and create connections
        for loc, group in location_groups.items():
            if len(group) > 1:
                # Mark all stations at this location as transfer stations
                for station in group:
                    station["is_transfer"] = True
                
                # Create connections between different modes at same location
                for i, s1 in enumerate(group):
                    for s2 in group[i+1:]:
                        if s1["type"] != s2["type"]:
                            connections.append({
                                "from": s1["id"],
                                "to": s2["id"],
                                "walk_time": 2  # Quick transfer
                            })
        
        # Ensure network connectivity with MST approach
        connected = set()
        if stations:
            connected.add(stations[0]["id"])
        
        while len(connected) < len(stations):
            min_dist = float('inf')
            best_pair = None
            
            for s1 in stations:
                if s1["id"] in connected:
                    for s2 in stations:
                        if s2["id"] not in connected:
                            dist = abs(s1["x"] - s2["x"]) + abs(s1["y"] - s2["y"])
                            if dist < min_dist:
                                min_dist = dist
                                best_pair = (s1, s2)
            
            if best_pair:
                s1, s2 = best_pair
                connections.append({
                    "from": s1["id"],
                    "to": s2["id"], 
                    "walk_time": min_dist * 120  # 2 minutes per grid unit
                })
                connected.add(s2["id"])
        
        # Add walking connections for nearby different-mode stations
        for i, s1 in enumerate(stations):
            for j, s2 in enumerate(stations[i+1:], i+1):
                if s1["type"] == s2["type"]:
                    continue
                    
                distance = abs(s1["x"] - s2["x"]) + abs(s1["y"] - s2["y"])
                if distance <= 2:
                    # Check if connection doesn't already exist
                    existing = any(
                        (c["from"] == s1["id"] and c["to"] == s2["id"]) or
                        (c["from"] == s2["id"] and c["to"] == s1["id"])
                        for c in connections
                    )
                    if not existing:
                        walk_time = max(3, int(distance * 100 / 60))  # ~100m per grid, 60m/min walking
                        connections.append({
                            "from": s1["id"],
                            "to": s2["id"],
                            "walk_time": walk_time
                        })
        
        # Ensure all stations are connected
        connections = self._ensure_connectivity(stations, connections)
        
        return connections
    
    def _generate_routes(self, stations: List[Dict]) -> List[Dict]:
        routes = []
        route_id = 0
        
        # Group stations by type for route generation
        stations_by_type = {}
        for station in stations:
            station_type = station["type"]
            if station_type not in stations_by_type:
                stations_by_type[station_type] = []
            stations_by_type[station_type].append(station)
        
        # Create routes for each mode
        for mode, mode_stations in stations_by_type.items():
            if len(mode_stations) < 2:
                continue
            
            # Create realistic routes based on geographic patterns
            routes_for_mode = self._create_realistic_routes(mode_stations, mode)
            
            for i, route_stations in enumerate(routes_for_mode):
                if len(route_stations) >= 2:
                    routes.append({
                        "id": f"route_{route_id}",
                        "mode": mode,
                        "stations": [s["id"] for s in route_stations],
                        "color": self._get_route_color(mode, i)
                    })
                    route_id += 1
        
        return routes
    
    def _create_realistic_routes(self, stations: List[Dict], mode: str) -> List[List[Dict]]:
        """Create realistic transit routes that follow geographic patterns"""
        if len(stations) < 2:
            return []
        
        routes = []
        
        # Different strategies based on mode
        if mode == "metro":
            # Metro lines often follow major axes (N-S, E-W)
            routes = self._create_axial_routes(stations)
        elif mode == "tram":
            # Trams often follow streets in loops or linear paths
            routes = self._create_linear_routes(stations)
        else:  # bus
            # Buses create more flexible, connecting routes
            routes = self._create_connecting_routes(stations)
        
        return routes
    
    def _create_axial_routes(self, stations: List[Dict]) -> List[List[Dict]]:
        """Create routes that follow major N-S and E-W axes"""
        routes = []
        
        if len(stations) < 3:
            # If not enough stations, just create one simple route
            return [self._order_stations_by_distance(stations)]
        
        # Sort by x for E-W route
        x_sorted = sorted(stations, key=lambda s: s["x"])
        # Sort by y for N-S route
        y_sorted = sorted(stations, key=lambda s: s["y"])
        
        # Create E-W route (horizontal) - take every other station to avoid overcrowding
        ew_stations = x_sorted[::2]  # Every other station
        if len(ew_stations) >= 2:
            routes.append(ew_stations)
        
        # Create N-S route (vertical) - use remaining stations
        ns_stations = y_sorted[1::2]  # Offset to get different stations
        if len(ns_stations) >= 2:
            routes.append(ns_stations)
        
        return routes
    
    def _create_linear_routes(self, stations: List[Dict]) -> List[List[Dict]]:
        """Create linear routes that follow natural paths"""
        routes = []
        
        if len(stations) < 2:
            return routes
        
        # Create 1-2 routes depending on station count
        num_routes = min(2, max(1, len(stations) // 3))
        stations_per_route = len(stations) // num_routes
        
        for i in range(num_routes):
            start_idx = i * stations_per_route
            end_idx = start_idx + stations_per_route + 2  # Small overlap
            route_stations = stations[start_idx:end_idx]
            
            if len(route_stations) >= 2:
                # Order by distance for smoother path
                ordered_route = self._order_stations_by_distance(route_stations)
                routes.append(ordered_route)
        
        return routes
    
    def _create_connecting_routes(self, stations: List[Dict]) -> List[List[Dict]]:
        """Create routes that connect different areas efficiently"""
        routes = []
        
        if len(stations) < 2:
            return routes
        
        # Create 2-3 bus routes that connect different zones
        num_routes = min(3, max(1, len(stations) // 4))
        
        for i in range(num_routes):
            # Select stations for this route, trying to spread across the city
            route_stations = []
            
            # Use simple division to create different routes
            stations_per_route = max(3, len(stations) // num_routes)
            start_idx = i * len(stations) // num_routes
            
            # Take a slice of stations for this route
            selected = stations[start_idx:start_idx + stations_per_route]
            
            if len(selected) >= 2:
                # Order them to create a sensible path
                route = self._order_stations_by_distance(selected)
                routes.append(route)
        
        return routes
    
    def _order_stations_by_distance(self, stations: List[Dict]) -> List[Dict]:
        """Order stations using nearest-neighbor for a smooth path"""
        if len(stations) <= 2:
            return stations
        
        # Start from the leftmost station
        ordered = [min(stations, key=lambda s: s["x"])]
        remaining = [s for s in stations if s != ordered[0]]
        
        # Use nearest neighbor algorithm (fast and simple)
        while remaining:
            current = ordered[-1]
            nearest = min(remaining, key=lambda s: 
                         abs(s["x"] - current["x"]) + abs(s["y"] - current["y"]))
            ordered.append(nearest)
            remaining.remove(nearest)
        
        return ordered
    
    def _get_route_color(self, mode: str, route_num: int) -> str:
        # Color schemes for different modes
        colors = {
            "metro": ["#FF0000", "#00FF00", "#0000FF"],  # Red, Green, Blue
            "tram": ["#FFA500", "#800080", "#008080"],   # Orange, Purple, Teal
            "bus": ["#FFD700", "#FF69B4", "#32CD32"]     # Gold, Pink, Lime
        }
        
        mode_colors = colors.get(mode, ["#000000"])
        return mode_colors[route_num % len(mode_colors)]
    
    def save_city(self, city_data: Dict, filename: str):
        filepath = f"data/{filename}"
        with open(filepath, 'w') as f:
            json.dump(city_data, f, indent=2)
    
    def load_city(self, filename: str) -> Dict:
        filepath = f"data/{filename}"
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def generate_batch_cities(self, count: int = 100):
        # Generate hundreds of cities for training
        for i in range(count):
            city = self.generate_random_city()
            self.save_city(city, f"city_{i:03d}.json")
    
    def _verify_connectivity(self, stations: List[Dict], connections: List[Dict]) -> bool:
        """Verify that all stations are connected in the network."""
        if not stations:
            return True
            
        # Build adjacency list
        graph = defaultdict(set)
        for conn in connections:
            graph[conn["from"]].add(conn["to"])
            graph[conn["to"]].add(conn["from"])
        
        # BFS to find all reachable stations
        start_station = stations[0]["id"]
        visited = set()
        queue = deque([start_station])
        visited.add(start_station)
        
        while queue:
            current = queue.popleft()
            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        # Check if all stations are reachable
        all_station_ids = {station["id"] for station in stations}
        return len(visited) == len(all_station_ids)
    
    def _ensure_connectivity(self, stations: List[Dict], connections: List[Dict]) -> List[Dict]:
        """Ensure all stations are connected by adding minimum necessary connections."""
        if self._verify_connectivity(stations, connections):
            return connections
        
        # Build adjacency list
        graph = defaultdict(set)
        for conn in connections:
            graph[conn["from"]].add(conn["to"])
            graph[conn["to"]].add(conn["from"])
        
        # Find connected components
        visited = set()
        components = []
        
        for station in stations:
            station_id = station["id"]
            if station_id not in visited:
                # BFS to find this component
                component = set()
                queue = deque([station_id])
                visited.add(station_id)
                component.add(station_id)
                
                while queue:
                    current = queue.popleft()
                    for neighbor in graph[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                            component.add(neighbor)
                
                components.append(component)
        
        # Connect components by adding edges between closest stations
        station_dict = {s["id"]: s for s in stations}
        
        while len(components) > 1:
            min_dist = float('inf')
            best_connection = None
            comp1_idx = 0
            comp2_idx = 1
            
            # Find closest pair between different components
            for i, comp1 in enumerate(components):
                for j, comp2 in enumerate(components[i+1:], i+1):
                    for s1_id in comp1:
                        for s2_id in comp2:
                            s1 = station_dict[s1_id]
                            s2 = station_dict[s2_id]
                            dist = abs(s1["x"] - s2["x"]) + abs(s1["y"] - s2["y"])
                            if dist < min_dist:
                                min_dist = dist
                                best_connection = (s1_id, s2_id)
                                comp1_idx = i
                                comp2_idx = j
            
            if best_connection:
                s1_id, s2_id = best_connection
                connections.append({
                    "from": s1_id,
                    "to": s2_id,
                    "walk_time": min_dist * 120  # 2 minutes per grid unit
                })
                
                # Merge the two components
                components[comp1_idx].update(components[comp2_idx])
                components.pop(comp2_idx)
        
        return connections
