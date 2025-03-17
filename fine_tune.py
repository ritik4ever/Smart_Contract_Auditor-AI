import os
import argparse
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset


class SmartContractDataset(Dataset):
    def __init__(self, tokenizer, file_path, block_size=512):
        self.examples = []

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            # Format: contract code + vulnerabilities
            prompt = f"""
            Analyze the following smart contract for security vulnerabilities:
            
            ```solidity
            {item['contract_code']}
            ```
            
            Identify and explain any security issues found.
            """

            # Format the response as JSON
            vulnerabilities = []
            for vuln in item.get('vulnerabilities', []):
                vulnerabilities.append({
                    "type": vuln['type'],
                    "severity": vuln['severity'],
                    "description": vuln['description'],
                    "line_numbers": vuln.get('line_numbers', []),
                    "recommendation": vuln.get('recommendation', "Review the code and fix the issue.")
                })

            response = {
                "vulnerabilities": vulnerabilities,
                "overview": item.get('overview', f"Found {len(vulnerabilities)} potential vulnerabilities.")
            }

            response_text = json.dumps(response, indent=2)

            full_text = f"{prompt}\n\n{response_text}"

            tokenized = tokenizer(
                full_text, truncation=True, max_length=block_size)
            self.examples.append(tokenized)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        return {
            "input_ids": torch.tensor(self.examples[i]["input_ids"]),
            "attention_mask": torch.tensor(self.examples[i]["attention_mask"]),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tune a model for smart contract vulnerability detection")
    parser.add_argument("--model_name", type=str,
                        default="gpt2", help="Base model to fine-tune")
    parser.add_argument("--train_file", type=str, required=True,
                        help="Path to training data JSON file")
    parser.add_argument("--val_file", type=str,
                        help="Path to validation data JSON file")
    parser.add_argument("--output_dir", type=str,
                        default="./fine_tuned_model", help="Output directory")
    parser.add_argument("--epochs", type=int, default=3,
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4,
                        help="Batch size for training")
    parser.add_argument("--learning_rate", type=float,
                        default=5e-5, help="Learning rate")
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize tokenizer and model
    print(f"Loading model: {args.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model_name)

    # Load datasets
    print("Loading datasets")
    train_dataset = SmartContractDataset(tokenizer, args.train_file)

    if args.val_file:
        eval_dataset = SmartContractDataset(tokenizer, args.val_file)
    else:
        eval_dataset = None

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        overwrite_output_dir=True,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        evaluation_strategy="epoch" if eval_dataset else "no",
        save_strategy="epoch",
        save_total_limit=2,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        fp16=torch.cuda.is_available(),
        logging_dir=os.path.join(args.output_dir, "logs"),
        logging_steps=10,
        report_to=["tensorboard"],
    )

    # Create data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False)

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator
    )

    # Start training
    print("Starting training")
    trainer.train()

    # Save the model
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Model saved to {args.output_dir}")


if __name__ == "__main__":
    main()
