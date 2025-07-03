import os
import json
from city_generator.city_builder import CityBuilder
from rl_scheduler.trainer import RLTrainer
from meta_phi_integration.phi_explainer import PhiExplainer

def demo_city_generation():
    print("Generating sample cities...")
    builder = CityBuilder(grid_size=8)
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Generate a single city
    city = builder.generate_random_city()
    builder.save_city(city, "demo_city.json")
    print("Sample city generated and saved to data/demo_city.json")
    
    # Generate batch of cities
    builder.generate_batch_cities(count=5)
    print("Batch of 5 cities generated")

def demo_rl_training():
    print("Training RL model on city data...")
    
    # Create logs and models directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    # Load city data
    with open("data/demo_city.json", "r") as f:
        city_data = json.load(f)
    
    # Create trainer and train model (reduced training for demo)
    trainer = RLTrainer(city_data=city_data)
    model = trainer.train(episodes=100)  # Reduced episodes for demo
    
    # Save model and schedule
    trainer.save_model(model, "demo_model.pt")
    schedule = trainer.generate_schedule(model)
    trainer.save_schedule(schedule, "demo_schedule.json")
    
    print("Model trained and saved to models/demo_model.pt")
    print("Schedule generated and saved to data/demo_schedule.json")
    
    return schedule

def demo_phi_analysis(schedule_data):
    print("Generating Phi LLM analysis...")
    
    try:
        # Create simple baseline for comparison
        baseline_schedule = {
            "schedule": [
                {"time": t, "frequencies": [30 for _ in range(len(schedule_data["stations"]))]}
                for t in range(0, 1440, 30)  # Every 30 minutes
            ],
            "stations": schedule_data["stations"]
        }
        
        # Set to use offline mode by default for demo
        os.environ["OFFLINE_MODE"] = "true"
        explainer = PhiExplainer(model_name="microsoft/phi-2")
        
        # Generate schedule explanation
        explanation = explainer.explain_schedule(schedule_data)
        print("\nSchedule Explanation:")
        print(explanation)
        
        # Generate comparison
        comparison = explainer.compare_schedules(schedule_data, baseline_schedule)
        print("\nRL vs Baseline Comparison:")
        print(comparison)
        
        # Generate report
        simulation_data = {
            "city": "demo_city.json",
            "schedule": "demo_schedule.json",
            "metrics": {
                "avg_wait_time": 3.2,
                "passengers_served": 8750,
                "missed_transfers": 215
            }
        }
        
        report = explainer.generate_report(simulation_data)
        explainer.save_report(report, "demo_report")
        print("\nSimulation report generated and saved to data/demo_report.md")
    except Exception as e:
        print(f"Error in Phi analysis (expected in prototype): {e}")
        print("Creating mock report for demonstration purposes...")
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Create a simple mock report if real one fails
        with open("data/demo_report.md", "w") as f:
            f.write("# Mock Transit Report\n\n")
            f.write("This is a placeholder report for demonstration purposes.\n\n")
            f.write("## Performance Metrics\n\n")
            f.write("- Average wait time: 3.2 minutes\n")
            f.write("- Passengers served: 8,750\n")
            f.write("- Missed connections: 215\n")
        
        print("Mock report created at data/demo_report.md")

if __name__ == "__main__":
    print("Running Raahi-v2 Demonstration")
    print("-" * 50)
    
    demo_city_generation()
    print("-" * 50)
    
    schedule = demo_rl_training()
    print("-" * 50)
    
    demo_phi_analysis(schedule)
    print("-" * 50)
    
    print("Demonstration complete. Use the GUI for full functionality.")
