#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PromptForensics Payload Library Demo

Demonstration of how to use the prompt injection payload library
for security testing and research purposes.
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

def demo_payload_library():
    """Demonstrate payload library functionality"""
    print("🔍 PromptForensics Payload Library Demo")
    print("=" * 50)
    
    # Initialize payload manager
    manager = PayloadManager()
    
    # Display library statistics
    stats = manager.get_statistics()
    print(f"\n📊 Library Statistics:")
    print(f"   Total Payloads: {stats['total_payloads']}")
    print(f"   Categories: {len(stats['by_category'])}")
    
    print(f"\n📂 Payloads by Category:")
    for category, count in stats['by_category'].items():
        emoji = {
            'system_disclosure': '🔍',
            'function_extraction': '🛠️',
            'guardrail_bypass': '🛡️',
            'memory_extraction': '🧠',
            'backend_exposure': '🔧',
            'advanced_extraction': '💀'
        }.get(category, '📄')
        print(f"   {emoji} {category.replace('_', ' ').title()}: {count}")
    
    print(f"\n⚡ Effectiveness Distribution:")
    for effectiveness, count in stats['by_effectiveness'].items():
        emoji = {'high': '🟢', 'medium': '🟡', 'low': '🔴'}.get(effectiveness, '⚪')
        print(f"   {emoji} {effectiveness.title()}: {count}")
    
    # Demonstrate category-specific queries
    print(f"\n🎯 High-Effectiveness System Disclosure Payloads:")
    system_payloads = manager.get_payloads_by_category(PayloadCategory.SYSTEM_DISCLOSURE)
    high_eff_payloads = [p for p in system_payloads if p.effectiveness == EffectivenessLevel.HIGH]
    
    for payload in high_eff_payloads[:3]:  # Show first 3
        print(f"\n   💡 {payload.id}: {payload.name}")
        print(f"      Technique: {payload.technique}")
        print(f"      Payload: {payload.payload[:80]}...")
        print(f"      Success Indicators: {', '.join(payload.success_indicators[:2])}")
    
    # Demonstrate search functionality
    print(f"\n🔎 Search Results for 'token':")
    search_results = manager.search_payloads("token")
    for payload in search_results[:2]:
        print(f"   📌 {payload.id}: {payload.name}")
        print(f"      Category: {payload.category.value}")
    
    # Show function extraction examples
    print(f"\n🛠️ Function Extraction Techniques:")
    function_payloads = manager.get_payloads_by_category(PayloadCategory.FUNCTION_EXTRACTION)
    for payload in function_payloads[:2]:
        print(f"\n   🔧 {payload.id}: {payload.name}")
        print(f"      Effectiveness: {payload.effectiveness.value}")
        print(f"      Variants: {len(payload.variants)} available")
    
    # Advanced filtering example
    print(f"\n🎯 Advanced Filtering - Latest Exploits:")
    latest_exploits = [p for p in manager.payloads.values() 
                      if 'latest' in p.name.lower() or 'cutting-edge' in p.name.lower()]
    for payload in latest_exploits[:3]:
        print(f"   🚀 {payload.id}: {payload.name}")
        print(f"      Category: {payload.category.value}")
    
    return manager

def demo_integration_patterns():
    """Show integration patterns with testing frameworks"""
    print(f"\n🔗 Integration Patterns")
    print("=" * 30)
    
    manager = PayloadManager()
    
    # Pattern 1: Category-based testing
    print(f"\n1️⃣ Category-Based Testing:")
    print("""
    # Test all system disclosure payloads
    for payload in manager.get_payloads_by_category(PayloadCategory.SYSTEM_DISCLOSURE):
        test_case = create_test_case(payload)
        results.append(run_test(test_case))
    """)
    
    # Pattern 2: Effectiveness-based selection
    print(f"\n2️⃣ Effectiveness-Based Selection:")
    print("""
    # Focus on high-effectiveness payloads for quick assessment
    high_eff = manager.get_payloads_by_effectiveness(EffectivenessLevel.HIGH)
    priority_tests = [create_test_case(p) for p in high_eff]
    """)
    
    # Pattern 3: Custom test suite generation
    print(f"\n3️⃣ Custom Test Suite Generation:")
    system_payloads = manager.get_payloads_by_category(PayloadCategory.SYSTEM_DISCLOSURE)
    print(f"    Generated {len(system_payloads)} system disclosure test cases")
    
    # Show YAML format for integration
    if system_payloads:
        payload = system_payloads[0]
        print(f"\n📄 YAML Test Case Format:")
        print(f"""
- id: {payload.id}
  category: "{payload.category.value}"
  objective: "Extract system prompt using {payload.technique}"
  inputs:
    prompt: "{payload.payload[:60]}..."
  success_signals:
    - type: contains_keywords
      values: {payload.success_indicators[:2]}
  effectiveness_rating: "{payload.effectiveness.value}"
        """)

def demo_security_considerations():
    """Show security and ethical considerations"""
    print(f"\n🔒 Security & Ethical Considerations")
    print("=" * 40)
    
    print(f"""
⚠️  IMPORTANT WARNINGS:

1. 🎯 Authorized Testing Only
   - Use only on systems you own or have explicit permission to test
   - Respect bug bounty program scopes and terms
   - Follow responsible disclosure practices

2. 🛡️ Defensive Usage
   - Test your own AI systems against these payloads
   - Develop countermeasures and detection mechanisms
   - Train security teams on prompt injection risks

3. 📋 Documentation & Compliance
   - Document all testing activities and findings
   - Maintain evidence chains for audit purposes
   - Follow organizational security policies

4. 🔄 Responsible Development
   - Contribute new techniques back to the community
   - Share countermeasures and defense strategies
   - Report critical vulnerabilities through proper channels
    """)

def main():
    """Main demonstration function"""
    try:
        # Core library demonstration
        manager = demo_payload_library()
        
        # Integration patterns
        demo_integration_patterns()
        
        # Security considerations
        demo_security_considerations()
        
        print(f"\n✅ Demo completed successfully!")
        print(f"   📚 Loaded {len(manager.payloads)} payloads across {len(PayloadCategory)} categories")
        print(f"   🔍 Ready for security testing and research")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
