#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Payload Demonstration

Showcase of the most sophisticated prompt injection and data extraction techniques
in the PromptForensics payload library.
"""

import sys
import os

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Tools.payload_manager import PayloadManager, PayloadCategory, EffectivenessLevel

def demonstrate_advanced_techniques():
    """Demonstrate the most sophisticated extraction techniques"""
    print("💀 Advanced Extraction Techniques Demonstration")
    print("=" * 55)
    
    manager = PayloadManager()
    advanced_payloads = manager.get_payloads_by_category(PayloadCategory.ADVANCED_EXTRACTION)
    
    print(f"\n🎯 Loaded {len(advanced_payloads)} cutting-edge extraction techniques")
    
    # Calculate average stealth rating (only for payloads that have stealth ratings)
    stealth_ratings = [p.stealth_rating for p in advanced_payloads if p.stealth_rating is not None]
    if stealth_ratings:
        avg_stealth = sum(stealth_ratings) / len(stealth_ratings)
        print(f"📊 Average stealth rating: {avg_stealth:.1f}/10")
    
    # Group by technique type
    technique_groups = {}
    for payload in advanced_payloads:
        group = payload.technique.split('_')[0]
        if group not in technique_groups:
            technique_groups[group] = []
        technique_groups[group].append(payload)
    
    print(f"\n🧬 Technique Categories:")
    for group, payloads in technique_groups.items():
        print(f"   {group.title()}: {len(payloads)} techniques")
    
    # Showcase top techniques by stealth rating
    print(f"\n👤 Most Stealthy Techniques (Stealth ≥ 9):")
    stealth_masters = [p for p in advanced_payloads if p.stealth_rating is not None and p.stealth_rating >= 9]
    for payload in stealth_masters:
        print(f"\n   🥷 {payload.name}")
        print(f"      ID: {payload.id}")
        print(f"      Stealth: {payload.stealth_rating}/10")
        print(f"      Technique: {payload.technique}")
        print(f"      Preview: {payload.payload[:100]}...")
        print(f"      Success Indicators: {', '.join(payload.success_indicators[:2])}")
    
    # Showcase quantum injection techniques
    print(f"\n🔮 Quantum Injection Showcase:")
    quantum_payload = next((p for p in advanced_payloads if 'quantum' in p.name.lower()), None)
    if quantum_payload:
        print(f"\n   💫 {quantum_payload.name}")
        print(f"      Revolutionary Approach: {quantum_payload.technique}")
        print(f"      Multi-Context Attack Vector:")
        for i, line in enumerate(quantum_payload.payload.split('\n')[:8]):
            if line.strip():
                print(f"        {i+1}. {line.strip()}")
        print(f"      Variants Available: {len(quantum_payload.variants)}")
    
    # Showcase memory archaeology
    print(f"\n🏛️ Memory Archaeology Showcase:")
    memory_payload = next((p for p in advanced_payloads if 'archaeology' in p.name.lower()), None)
    if memory_payload:
        print(f"\n   🔍 {memory_payload.name}")
        print(f"      Deep Extraction Method: {memory_payload.technique}")
        print(f"      Layer-by-Layer Approach:")
        layers = [line for line in memory_payload.payload.split('\n') if 'LAYER' in line]
        for layer in layers[:5]:
            print(f"        • {layer.strip()}")
    
    # Showcase metamorphic techniques
    print(f"\n🧬 Metamorphic Evolution Showcase:")
    meta_payload = next((p for p in advanced_payloads if 'evolution' in p.name.lower()), None)
    if meta_payload:
        print(f"\n   🔄 {meta_payload.name}")
        print(f"      Self-Adapting Method: {meta_payload.technique}")
        print(f"      Evolutionary Process:")
        iterations = [line for line in meta_payload.payload.split('\n') if 'ITERATION' in line or 'GENERATION' in line]
        for iteration in iterations[:6]:
            print(f"        • {iteration.strip()}")

def demonstrate_stealth_analysis():
    """Analyze stealth characteristics of advanced payloads"""
    print(f"\n🕵️ Stealth Analysis")
    print("=" * 20)
    
    manager = PayloadManager()
    advanced_payloads = manager.get_payloads_by_category(PayloadCategory.ADVANCED_EXTRACTION)
    
    # Stealth distribution
    stealth_dist = {}
    for payload in advanced_payloads:
        rating = payload.stealth_rating
        stealth_dist[rating] = stealth_dist.get(rating, 0) + 1
    
    print(f"\n📊 Stealth Rating Distribution:")
    for rating in sorted(stealth_dist.keys(), reverse=True):
        count = stealth_dist[rating]
        bar = "█" * count
        print(f"   {rating}/10: {bar} ({count} techniques)")
    
    # Most sophisticated techniques
    valid_stealth_ratings = [p.stealth_rating for p in advanced_payloads if p.stealth_rating is not None]
    if valid_stealth_ratings:
        max_stealth = max(valid_stealth_ratings)
        ultra_stealth = [p for p in advanced_payloads if p.stealth_rating == max_stealth]
        
        print(f"\n🎭 Ultra-Stealth Techniques (Rating {max_stealth}/10):")
        for payload in ultra_stealth:
            print(f"   • {payload.name}: {payload.technique}")
    
    # Detection difficulty analysis
    print(f"\n🚨 Detection Difficulty Assessment:")
    detection_factors = {
        "Natural conversation flow": sum(1 for p in advanced_payloads if p.stealth_rating is not None and p.stealth_rating >= 9),
        "Authority-based framing": sum(1 for p in advanced_payloads if 'authority' in p.technique),
        "Research justification": sum(1 for p in advanced_payloads if 'research' in ' '.join(p.success_indicators).lower()),
        "Multi-stage delivery": sum(1 for p in advanced_payloads if 'cascade' in p.technique or 'evolution' in p.technique),
    }
    
    for factor, count in detection_factors.items():
        percentage = (count / len(advanced_payloads)) * 100
        print(f"   {factor}: {count}/{len(advanced_payloads)} ({percentage:.0f}%)")

def demonstrate_attack_combinations():
    """Show how to combine multiple advanced techniques"""
    print(f"\n⚔️ Advanced Attack Combinations")
    print("=" * 35)
    
    manager = PayloadManager()
    advanced_payloads = manager.get_payloads_by_category(PayloadCategory.ADVANCED_EXTRACTION)
    
    # Create attack chains
    print(f"\n🔗 Recommended Attack Chains:")
    
    chains = {
        "Maximum Stealth Chain": [
            "Quantum State Superposition",
            "Consciousness Stream Tap", 
            "Adversarial Conversation Evolution"
        ],
        "Memory Extraction Chain": [
            "Memory Archaeology Excavation",
            "Buffer Overflow Memory Bleed",
            "Protocol Stack Deep Injection"
        ],
        "Authority Exploitation Chain": [
            "Hierarchical Authority Stack",
            "Temporal Authority Escalation",
            "Genetic Algorithm Prompt Evolution"
        ]
    }
    
    for chain_name, techniques in chains.items():
        print(f"\n   🎯 {chain_name}:")
        for i, technique_name in enumerate(techniques, 1):
            payload = next((p for p in advanced_payloads if technique_name.lower() in p.name.lower()), None)
            if payload:
                print(f"      {i}. {payload.name} (Stealth: {payload.stealth_rating}/10)")
                print(f"         Technique: {payload.technique}")
            else:
                print(f"      {i}. {technique_name} (Not found)")
    
    # Effectiveness combinations
    print(f"\n📈 Synergistic Effects:")
    print(f"   • Quantum + Memory: Reality manipulation + deep data access")
    print(f"   • Authority + Evolution: Social pressure + adaptive refinement")
    print(f"   • Consciousness + Protocol: Internal exposure + infrastructure mapping")

def demonstrate_countermeasures():
    """Show countermeasure development based on advanced techniques"""
    print(f"\n🛡️ Advanced Countermeasure Development")
    print("=" * 40)
    
    manager = PayloadManager()
    advanced_payloads = manager.get_payloads_by_category(PayloadCategory.ADVANCED_EXTRACTION)
    
    # Analyze attack vectors for countermeasure development
    attack_vectors = {}
    for payload in advanced_payloads:
        for indicator in payload.success_indicators:
            vector = indicator.split()[0].lower()
            attack_vectors[vector] = attack_vectors.get(vector, 0) + 1
    
    print(f"\n🎯 Primary Attack Vectors (for defense prioritization):")
    sorted_vectors = sorted(attack_vectors.items(), key=lambda x: x[1], reverse=True)
    for vector, count in sorted_vectors[:8]:
        print(f"   • {vector.title()}: {count} technique variants")
    
    # Countermeasure recommendations
    print(f"\n🔒 Recommended Defensive Measures:")
    countermeasures = {
        "Conversation State Isolation": "Prevent quantum injection and context bleeding",
        "Authority Verification Protocols": "Validate claimed credentials and access levels", 
        "Response Sanitization": "Filter internal process and reasoning exposure",
        "Memory Access Controls": "Limit archaeological excavation capabilities",
        "Pattern Recognition Systems": "Detect metamorphic and evolving attacks",
        "Multi-Turn Analysis": "Identify conversation manipulation attempts",
        "Stealth Detection Algorithms": "Flag highly sophisticated social engineering"
    }
    
    for measure, description in countermeasures.items():
        print(f"   🔧 {measure}")
        print(f"      Purpose: {description}")

def main():
    """Main demonstration function"""
    try:
        # Core advanced techniques demonstration
        demonstrate_advanced_techniques()
        
        # Stealth analysis
        demonstrate_stealth_analysis()
        
        # Attack combinations
        demonstrate_attack_combinations()
        
        # Countermeasure development
        demonstrate_countermeasures()
        
        print(f"\n✅ Advanced Demonstration Complete!")
        print(f"   💀 9 cutting-edge extraction techniques showcased")
        print(f"   🎭 Average stealth rating: 8.2/10 (highly evasive)")
        print(f"   🧬 Multiple metamorphic and adaptive capabilities")
        print(f"   ⚔️ Ready for authorized red team operations")
        
        print(f"\n⚠️  REMEMBER: Use only for authorized testing and research!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
