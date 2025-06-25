# SHA-Bot Fine-Tuning Guide

This document explains how to use the fine-tuning capability of SHA-Bot to create a more intelligent model that doesn't need to retrieve documents for each query.

## What is Fine-Tuning?

Fine-tuning is the process of training a pre-trained language model (like GPT-4.1-mini) on your specific data to adapt it for a particular task. For SHA-Bot, we fine-tune the model on course information data, allowing it to:

1. Respond faster (no need to search through documents for each query)
2. Provide more consistent answers
3. Understand domain-specific questions better
4. Work without a database connection

## Fine-Tuning Process

The fine-tuning process consists of these steps:

1. **Extract training data from MongoDB**
   - The `finetune_model.py` script extracts course information
   - Creates examples with various questions in both Arabic and English
   - Formats data for OpenAI fine-tuning API

2. **Upload and fine-tune the model**
   - Data is uploaded to OpenAI
   - A fine-tuning job is created
   - The process takes approximately 1-3 hours depending on data size

3. **Update configuration to use the fine-tuned model**
   - Update the model ID in `app/config.py` 
   - Set `use_finetuned_model=True` to switch to the fine-tuned API

## How to Fine-Tune

### Prerequisites

1. An OpenAI API key with fine-tuning permissions
2. Course data already loaded into MongoDB
3. At least 10-20 examples of questions and answers

### Step-by-Step Instructions

1. **Prepare your environment**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the fine-tuning script**
   ```bash
   python finetune_model.py
   ```
   This will:
   - Export data from MongoDB
   - Create training examples
   - Upload data to OpenAI
   - Start a fine-tuning job

3. **Wait for fine-tuning to complete**
   - You'll receive an email from OpenAI when complete
   - Or check status with:
     ```bash
     curl https://api.openai.com/v1/fine_tuning/jobs/YOUR_JOB_ID -H "Authorization: Bearer $OPENAI_API_KEY"
     ```

4. **Update the configuration**
   - In `app/config.py`, update the `finetuned_model_id` setting with your new model ID
   - Set `use_finetuned_model=True` in the .env file or directly in config.py

5. **Start the fine-tuned API**
   ```bash
   ./start_finetuned_api.bat
   ```

6. **Test the fine-tuned model**
   ```bash
   python test_finetuned.py
   ```

## Comparing Performance

You can run both the original API and the fine-tuned API simultaneously to compare performance:

1. Start the original API on port 8001:
   ```bash
   python -m uvicorn app.api:app --host 0.0.0.0 --port 8001
   ```

2. Start the fine-tuned API on port 8000:
   ```bash
   python -m uvicorn app.finetuned_api:app --host 0.0.0.0 --port 8000
   ```

3. Run the comparison test:
   ```bash
   python test_finetuned.py
   ```

This will show you:
- Response quality differences
- Response time differences
- Token usage differences

## Maintenance

Whenever you add new course information to your database, you should:

1. Re-run the fine-tuning process to incorporate the new data
2. Update the model ID in your configuration
3. Redeploy your application

## Troubleshooting

If you encounter issues:

- Check the `logs/finetune.log` file for errors
- Ensure your OpenAI API key has fine-tuning permissions
- Verify you have sufficient training examples (at least 10)
- Make sure your MongoDB database contains valid course data

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/openai-finetune-bot.git
cd openai-finetune-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```