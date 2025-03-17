from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import re

app = Flask(__name__)
CORS(app)

# Load environment variables or use defaults
# Replace with your fine-tuned model path
MODEL_PATH = os.environ.get("MODEL_PATH", "gpt2")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize model and tokenizer
print(f"Loading model from {MODEL_PATH}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH).to(DEVICE)
print("Model loaded successfully!")

# Common vulnerability patterns
VULNERABILITY_PATTERNS = {
    "reentrancy": r"(external\s+call.*before.*state\s+change|call\s+value.*external)",
    "arithmetic": r"(overflow|underflow|SafeMath|unchecked\s+arithmetic)",
    "access_control": r"(missing\s+modifier|onlyOwner|access\s+control)",
    "front_running": r"(front\s+run|transaction\s+ordering|commit\s+reveal)",
    "time_manipulation": r"(block\.(timestamp|number)|now\s+for\s+randomness)",
    "denial_of_service": r"(unbounded\s+loop|gas\s+limit|DoS)",
    "oracle_manipulation": r"(price\s+oracle|manipulation|flash\s+loan\s+attack)",
    "flash_loan": r"(flash\s+loan|arbitrage)",
    "signature_replay": r"(replay\s+attack|signature\s+validation|nonce)",
}


def analyze_with_llm(contract_code):
    """Analyze contract code using the loaded LLM"""
    prompt = f"""
    Analyze the following smart contract for security vulnerabilities:
    
    ```solidity
    {contract_code}
    ```
    
    Identify and explain any security issues found. Focus on:
    1. Reentrancy vulnerabilities
    2. Arithmetic issues (overflow/underflow)
    3. Access control problems
    4. Front-running possibilities
    5. Time/block manipulation risks
    6. Denial of service vectors
    7. Oracle manipulation vulnerabilities
    8. Flash loan attack vectors
    9. Signature replay attacks
    
    Format your response as JSON with the following structure:
    {{
        "vulnerabilities": [
            {{
                "type": "vulnerability_type",
                "severity": "high/medium/low",
                "description": "detailed explanation",
                "line_numbers": [line_numbers_if_identifiable],
                "recommendation": "how to fix"
            }}
        ],
        "overview": "overall security assessment"
    }}
    """

    inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)

    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=1024,
            temperature=0.2,
            top_p=0.95,
            do_sample=True
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract JSON part from response
    try:
        # Find JSON in the response
        json_match = re.search(r'({[\s\S]*})', response)
        if json_match:
            json_str = json_match.group(1)
            result = json.loads(json_str)
            return result
        else:
            # Fallback with rule-based analysis
            return rule_based_analysis(contract_code)
    except json.JSONDecodeError:
        # Fallback with rule-based analysis
        return rule_based_analysis(contract_code)


def rule_based_analysis(contract_code):
    """Analyze contract code using regex patterns for common vulnerabilities"""
    vulnerabilities = []

    # Get line numbers
    lines = contract_code.split('\n')

    for vuln_type, pattern in VULNERABILITY_PATTERNS.items():
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                description = f"Potential {vuln_type} vulnerability detected"
                severity = "medium"  # Default

                # Adjust severity based on vulnerability type
                if vuln_type in ["reentrancy", "access_control"]:
                    severity = "high"

                recommendation = f"Review the code at line {i+1} for potential {vuln_type} issues"

                vulnerabilities.append({
                    "type": vuln_type,
                    "severity": severity,
                    "description": description,
                    "line_numbers": [i + 1],
                    "recommendation": recommendation
                })

    return {
        "vulnerabilities": vulnerabilities,
        "overview": f"Found {len(vulnerabilities)} potential vulnerabilities through pattern matching."
    }


@app.route('/api/scan', methods=['POST'])
def scan_contract():
    data = request.json

    if not data or 'contract_code' not in data:
        return jsonify({"error": "No contract code provided"}), 400

    contract_code = data['contract_code']

    # Combine LLM analysis with rule-based analysis
    llm_result = analyze_with_llm(contract_code)
    rule_result = rule_based_analysis(contract_code)

    # Merge results, removing duplicates
    seen_vulns = set()
    combined_vulns = []

    for vuln in llm_result.get("vulnerabilities", []):
        key = f"{vuln['type']}-{vuln.get('line_numbers', [])}"
        if key not in seen_vulns:
            seen_vulns.add(key)
            combined_vulns.append(vuln)

    for vuln in rule_result.get("vulnerabilities", []):
        key = f"{vuln['type']}-{vuln.get('line_numbers', [])}"
        if key not in seen_vulns:
            seen_vulns.add(key)
            combined_vulns.append(vuln)

    result = {
        "vulnerabilities": combined_vulns,
        "overview": llm_result.get("overview", rule_result.get("overview", "Analysis complete")),
        "stats": {
            "total_vulnerabilities": len(combined_vulns),
            "high_severity": sum(1 for v in combined_vulns if v.get("severity") == "high"),
            "medium_severity": sum(1 for v in combined_vulns if v.get("severity") == "medium"),
            "low_severity": sum(1 for v in combined_vulns if v.get("severity") == "low")
        }
    }

    return jsonify(result)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "model": MODEL_PATH, "device": DEVICE})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
