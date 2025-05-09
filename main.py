#!/usr/bin/env python
"""
Main entry point for SHA-Bot application
"""
import os
import sys
import argparse
import asyncio

def run_server(mode="finetuned", port=8000):
    """Run the API server"""
    api_module = "app.finetuned_api" if mode == "finetuned" else "app.api"
    cmd = f"python -m uvicorn {api_module}:app --host 0.0.0.0 --port {port} --reload"
    print(f"Starting SHA-Bot in {mode} mode on port {port}...")
    os.system(cmd)

def run_training():
    """Run the training process to generate simulation data"""
    script_path = os.path.join("scripts", "finetune_model.py")
    print("Starting training process to generate simulation data...")
    os.system(f"python {script_path}")
    
def show_status():
    """Display status information about the simulation data"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    simulation_file = os.path.join(data_dir, "finetuned_simulation.json")
    training_file = os.path.join(data_dir, "training_data.jsonl")
    
    print("SHA-Bot Status:")
    print("-" * 50)
    
    if os.path.exists(simulation_file):
        size_mb = os.path.getsize(simulation_file) / (1024 * 1024)
        print(f"✅ Simulation data: {simulation_file} ({size_mb:.2f} MB)")
        
        # Count entries
        import json
        try:
            with open(simulation_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"   - {len(data)} question-answer pairs")
        except:
            print("   - Error reading file")
    else:
        print(f"❌ Simulation data not found: {simulation_file}")
    
    if os.path.exists(training_file):
        size_mb = os.path.getsize(training_file) / (1024 * 1024)
        print(f"✅ Training data: {training_file} ({size_mb:.2f} MB)")
        
        # Count entries
        try:
            with open(training_file, "r", encoding="utf-8") as f:
                count = sum(1 for _ in f)
                print(f"   - {count} training examples")
        except:
            print("   - Error reading file")
    else:
        print(f"❌ Training data not found: {training_file}")
    
    print("-" * 50)
    print("To generate simulation data: python main.py --train")
    print("To start the server: python main.py --run")

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="SHA-Bot - Advanced Assistant using MongoDB data")
    
    # Create command groups
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--run", 
        action="store_true",
        help="Run the API server"
    )
    group.add_argument(
        "--train", 
        action="store_true",
        help="Run the training process to generate simulation data"
    )
    group.add_argument(
        "--status", 
        action="store_true",
        help="Show status information about the simulation data"
    )
    
    # Additional options
    parser.add_argument(
        "--mode", 
        choices=["standard", "finetuned"], 
        default="finetuned",
        help="Mode to run the application (standard or finetuned)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to run the server on"
    )
    
    args = parser.parse_args()
    
    # Determine which action to take
    if args.run:
        run_server(args.mode, args.port)
    elif args.train:
        run_training()
    elif args.status:
        show_status()

if __name__ == "__main__":
    main() 