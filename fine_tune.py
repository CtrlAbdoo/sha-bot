import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer
from bitsandbytes.nn import Linear4bit
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def prepare_dataset(dataset_path="training_data.jsonl"):
    """
    Prepare the dataset from JSONL format for fine-tuning
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(
            f"Training data file '{dataset_path}' not found. "
            "Run the /export-documents endpoint first."
        )
    
    # Load the dataset
    dataset = load_dataset("json", data_files=dataset_path)
    
    # Print dataset information
    print(f"Loaded dataset with {len(dataset['train'])} examples")
    if len(dataset['train']) > 0:
        print("Example entry:", dataset['train'][0])
    
    return dataset

def run_fine_tuning(
    base_model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    output_dir="./fine_tuned_model",
    dataset_path="training_data.jsonl",
    epochs=3,
    learning_rate=2e-4,
    batch_size=2
):
    """
    Fine-tune a base model with custom data using LoRA
    """
    print(f"Starting fine-tuning process for {base_model}")
    
    # Check if GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with QLoRA 4-bit quantization for efficiency
    print("Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        device_map="auto",
        torch_dtype=torch.float16,
        load_in_4bit=True,
        quantization_config={
            "bnb_4bit_compute_dtype": torch.float16,
            "bnb_4bit_use_double_quant": True,
            "bnb_4bit_quant_type": "nf4"
        }
    )
    
    # Prepare model for training
    model = prepare_model_for_kbit_training(model)

# Configure LoRA
    peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
    
    model = get_peft_model(model, peft_config)

    # Load and prepare the dataset
    dataset = prepare_dataset(dataset_path)
    
    # Define training arguments
training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=batch_size,
    gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        num_train_epochs=epochs,
    logging_steps=10,
        save_strategy="epoch",
    fp16=True,
        report_to="none",
        warmup_ratio=0.05,
        lr_scheduler_type="cosine"
)

    # Initialize SFT trainer
trainer = SFTTrainer(
    model=model,
    args=training_args,
        train_dataset=dataset["train"],
        tokenizer=tokenizer,
        dataset_text_field="messages",
        max_seq_length=2048,
        packing=True
    )
    
    # Start training
    print("Starting training...")
trainer.train()

    # Save fine-tuned model
    print(f"Training completed. Saving model to {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("Fine-tuning process completed successfully!")
    return output_dir

if __name__ == "__main__":
    # Run the fine-tuning process
    run_fine_tuning()