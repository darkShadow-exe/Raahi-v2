import os
import sys
import json

def main():
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    print("Raahi-v2 Transit Optimizer")
    print("-------------------------")
    print("1. City Generator")
    print("2. RL Trainer")
    print("3. User Interface")
    print("4. Demo Mode")
    print("5. Exit")
    
    choice = input("Choose an option (1-5): ")
    
    try:
        if choice == "1":
            from city_generator.city_builder import CityBuilder
            builder = CityBuilder(grid_size=8)
            city = builder.generate_random_city()
            builder.save_city(city, "demo_city.json")
            print("City generated and saved to data/demo_city.json")
            
        elif choice == "2":
            from rl_scheduler.trainer import RLTrainer
            
            if not os.path.exists("data/demo_city.json"):
                print("No city found. Generating a new one.")
                from city_generator.city_builder import CityBuilder
                builder = CityBuilder(grid_size=8)
                city = builder.generate_random_city()
                builder.save_city(city, "demo_city.json")
            
            with open("data/demo_city.json", "r") as f:
                city_data = json.load(f)
                
            print("Training RL model (reduced episodes for prototype)...")
            trainer = RLTrainer(city_data=city_data)
            model = trainer.train(episodes=100)
            trainer.save_model(model, "demo_model.pt")
            print("Model saved to models/demo_model.pt")
            
        elif choice == "3":
            from user_interface.main_app import run_app
            run_app()
            
        elif choice == "4":
            print("Running demo script...")
            import demo
            
        elif choice == "5":
            print("Exiting...")
            sys.exit(0)
            
        else:
            print("Invalid choice")
    
    except ImportError as e:
        print(f"Module import error: {e}")
        print("Make sure you've installed all required packages:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
