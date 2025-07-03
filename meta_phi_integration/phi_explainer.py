from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import pandas as pd
import torch
import os

class PhiExplainer:
    def __init__(self, model_name="microsoft/phi-2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
    
    def load_model(self):
        try:
            # Check for offline mode flag
            if os.environ.get("OFFLINE_MODE", "false").lower() == "true":
                print("Running in offline mode - using mock LLM responses")
                return False
                
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def generate_response(self, prompt, max_length=500):
        if not self.model or not self.tokenizer:
            if not self.load_model():
                # Return mock response for prototype
                return f"Mock response for: {prompt[:50]}..."
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response.replace(prompt, "").strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error: {str(e)[:100]}"
    
    def explain_schedule(self, schedule_json):
        prompt = f"Explain this transit schedule:\n{json.dumps(schedule_json, indent=2)}"
        return self.generate_response(prompt)
    
    def compare_schedules(self, rl_data, naive_data):
        prompt = (
            f"Summarize differences between RL and baseline scheduler:\n"
            f"RL: {json.dumps(rl_data, indent=2)}\n"
            f"Baseline: {json.dumps(naive_data, indent=2)}"
        )
        return self.generate_response(prompt)
    
    def interpret_scenario(self, scenario_text):
        prompt = (
            f"Convert this scenario to demand modifications for a transit simulator:\n"
            f"{scenario_text}"
        )
        return self.generate_response(prompt)
    
    def generate_report(self, simulation_data):
        prompt = (
            f"Write a simulation report for this transit run:\n"
            f"{json.dumps(simulation_data, indent=2)}"
        )
        report = self.generate_response(prompt, max_length=1500)
        return report
    
    def save_report(self, report, filename):
        # Save report as markdown
        with open(f"data/{filename}.md", "w") as f:
            f.write(report)
        
        # For PDF we'd use a library like fpdf or reportlab
        # In prototype, just note it would happen
        print(f"Report would be saved as PDF to data/{filename}.pdf")
