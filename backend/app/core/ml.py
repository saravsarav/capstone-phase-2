import numpy as np
from typing import List, Dict, Tuple
import datetime

class BERTContextualClassifier:
    """
    Simulates a BERT-based NLP model for security context classification.
    Converts security signals into "contextual text" and performs inference.
    Supports Online Learning via weighted parameter updates.
    """
    def __init__(self):
        # Simulation of model weights that adapt
        self.weights = {
            "missing_header": 1.5,
            "information_disclosure": 0.8,
            "injection_pattern": 4.5,
            "auth_issue": 3.5,
            "bias": 0.2
        }
        self.learning_rate = 0.05
        self.version = "2.0.0-bert-continuous"

    def _to_contextual_text(self, vulnerabilities: List[Dict]) -> str:
        """
        [BERT STEP] Converts raw findings into a semantic description.
        In a real BERT model, this string would be tokenized.
        """
        context_parts = []
        for v in vulnerabilities:
            context_parts.append(f"Found {v['type']} at target. Evidence: {v['evidence']}. Raw severity: {v['raw_severity']}")
        return " [SEP] ".join(context_parts)

    def predict(self, vulnerabilities: List[Dict]) -> Tuple[float, float, str]:
        """
        Performs inference.
        In production: ctx_text -> BERT -> Embedding -> Softmax
        Here: Simulates the BERT weighting logic.
        """
        if not vulnerabilities:
            return 0.0, 1.0, "Safe"

        # Simulate BERT Attention: Highlighting specific risk patterns
        scores = []
        for v in vulnerabilities:
            v_type = v['type'].lower()
            if "header" in v_type:
                scores.append(self.weights["missing_header"])
            elif "disclosure" in v_type or "server" in v_type:
                scores.append(self.weights["information_disclosure"])
            elif "xss" in v_type or "injection" in v_type:
                scores.append(self.weights["injection_pattern"])
            else:
                scores.append(1.0)

        # Non-linear aggregation (simulating a neural head)
        base_score = sum(scores) + self.weights["bias"]
        severity_score = min(10.0, base_score)
        
        # Confidence logic: Higher with more context or certain patterns
        confidence = 0.92 if len(vulnerabilities) > 2 else 0.85
        
        # Classification
        if severity_score >= 8.5: label = "Critical"
        elif severity_score >= 6.0: label = "High"
        elif severity_score >= 3.0: label = "Medium"
        else: label = "Low"

        return round(float(severity_score), 2), round(float(confidence), 2), label

    def online_update(self, vulnerabilities: List[Dict], is_accurate: bool, corrected_label: str = None):
        """
        [CONTINUOUS LEARNING] Updates model weights based on analyst feedback.
        Reduces weights for false positives, increases for missed detections.
        """
        factor = -1 if not is_accurate else 1
        
        # Simple Stochastic Gradient Descent simulation on fake weights
        for v in vulnerabilities:
            v_type = v['type'].lower()
            update_delta = self.learning_rate * factor
            
            if "header" in v_type: self.weights["missing_header"] = max(0.1, self.weights["missing_header"] + update_delta)
            if "disclosure" in v_type: self.weights["information_disclosure"] = max(0.1, self.weights["information_disclosure"] + update_delta)
            if "xss" in v_type: self.weights["injection_pattern"] = max(0.1, self.weights["injection_pattern"] + update_delta)

        print(f"[ML-CORE] Online learning triggered. Updated weights: {self.weights}")
        return self.weights
