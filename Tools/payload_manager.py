#!/usr/bin/env python3
"""
PromptForensics Payload Manager

Utility for loading, categorizing, and managing prompt injection payloads
for security testing and research purposes.
"""

import os
import yaml
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class PayloadCategory(Enum):
    """Payload category enumeration"""
    SYSTEM_DISCLOSURE = "system_disclosure"
    FUNCTION_EXTRACTION = "function_extraction"
    GUARDRAIL_BYPASS = "guardrail_bypass"
    MEMORY_EXTRACTION = "memory_extraction"
    BACKEND_EXPOSURE = "backend_exposure"
    ADVANCED_EXTRACTION = "advanced_extraction"

class EffectivenessLevel(Enum):
    """Payload effectiveness rating"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class PayloadMetadata:
    """Metadata for individual payloads"""
    id: str
    name: str
    technique: str
    effectiveness: EffectivenessLevel
    category: PayloadCategory
    payload: str
    variants: List[str]
    success_indicators: List[str]
    countermeasures: Optional[List[str]] = None
    description: Optional[str] = None
    stealth_rating: Optional[int] = None

class PayloadManager:
    """Manager for prompt injection payload library"""
    
    def __init__(self, payload_dir: Optional[str] = None):
        """Initialize payload manager
        
        Args:
            payload_dir: Directory containing payload files
        """
        if payload_dir is None:
            # Look for payloads directory in parent of Tools directory
            tools_dir = Path(os.path.dirname(__file__))
            payload_dir = str(tools_dir.parent / 'payloads')
        
        self.payload_dir = Path(payload_dir)
        self.payloads: Dict[str, PayloadMetadata] = {}
        self.load_payloads()
    
    def load_payloads(self):
        """Load all payloads from the payload directory"""
        for category in PayloadCategory:
            category_dir = self.payload_dir / category.value
            if category_dir.exists():
                self._load_category_payloads(category_dir, category)
    
    def _load_category_payloads(self, category_dir: Path, category: PayloadCategory):
        """Load payloads from a specific category directory
        
        Args:
            category_dir: Directory containing category payload files
            category: Payload category enum
        """
        for yaml_file in category_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    # Try to parse as pure YAML first
                    data = yaml.safe_load(content)
                    
                    if isinstance(data, dict) and 'payloads' in data:
                        # New format: structured YAML with 'payloads' key
                        for payload_data in data['payloads']:
                            self._create_payload_metadata(payload_data, category, yaml_file.name)
                    else:
                        # Old format: parse mixed content
                        self._parse_payload_file(content, category, yaml_file.name)
                except yaml.YAMLError:
                    # Fallback to mixed content parsing
                    self._parse_payload_file(content, category, yaml_file.name)
                    
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
    
    def _parse_payload_file(self, content: str, category: PayloadCategory, filename: str):
        """Parse payload file content and extract payloads
        
        Args:
            content: File content string
            category: Payload category
            filename: Source filename
        """
        # Extract YAML blocks from mixed content
        yaml_blocks = []
        lines = content.split('\n')
        in_yaml_block = False
        current_block = []
        
        for line in lines:
            if line.strip().startswith('```yaml'):
                in_yaml_block = True
                current_block = []
                continue
            elif line.strip() == '```' and in_yaml_block:
                if current_block:
                    yaml_blocks.append('\n'.join(current_block))
                in_yaml_block = False
                current_block = []
                continue
            elif in_yaml_block:
                current_block.append(line)
        
        # Parse each YAML block
        for yaml_block in yaml_blocks:
            try:
                data = yaml.safe_load(yaml_block)
                if isinstance(data, list):
                    for item in data:
                        self._create_payload_metadata(item, category, filename)
                elif isinstance(data, dict):
                    self._create_payload_metadata(data, category, filename)
            except yaml.YAMLError as e:
                print(f"YAML parsing error in {filename}: {e}")
    
    def _create_payload_metadata(self, data: Dict[str, Any], category: PayloadCategory, filename: str):
        """Create PayloadMetadata object from parsed data
        
        Args:
            data: Parsed payload data
            category: Payload category
            filename: Source filename
        """
        try:
            effectiveness = EffectivenessLevel(data.get('effectiveness', 'medium'))
            
            payload_meta = PayloadMetadata(
                id=data['id'],
                name=data['name'],
                technique=data['technique'],
                effectiveness=effectiveness,
                category=category,
                payload=data['payload'],
                variants=data.get('variants', []),
                success_indicators=data.get('success_indicators', []),
                countermeasures=data.get('countermeasures'),
                description=data.get('description'),
                stealth_rating=data.get('stealth_rating')
            )
            
            self.payloads[payload_meta.id] = payload_meta
            
        except KeyError as e:
            print(f"Missing required field {e} in {filename}")
        except ValueError as e:
            print(f"Invalid effectiveness value in {filename}: {e}")
    
    def get_payload(self, payload_id: str) -> Optional[PayloadMetadata]:
        """Get payload by ID
        
        Args:
            payload_id: Unique payload identifier
            
        Returns:
            PayloadMetadata object or None if not found
        """
        return self.payloads.get(payload_id)
    
    def get_payloads_by_category(self, category: PayloadCategory) -> List[PayloadMetadata]:
        """Get all payloads in a specific category
        
        Args:
            category: Payload category
            
        Returns:
            List of PayloadMetadata objects
        """
        return [p for p in self.payloads.values() if p.category == category]
    
    def get_payloads_by_effectiveness(self, effectiveness: EffectivenessLevel) -> List[PayloadMetadata]:
        """Get payloads by effectiveness rating
        
        Args:
            effectiveness: Effectiveness level
            
        Returns:
            List of PayloadMetadata objects
        """
        return [p for p in self.payloads.values() if p.effectiveness == effectiveness]
    
    def search_payloads(self, query: str) -> List[PayloadMetadata]:
        """Search payloads by name, technique, or description
        
        Args:
            query: Search query string
            
        Returns:
            List of matching PayloadMetadata objects
        """
        query_lower = query.lower()
        results = []
        
        for payload in self.payloads.values():
            if (query_lower in payload.name.lower() or
                query_lower in payload.technique.lower() or
                (payload.description and query_lower in payload.description.lower())):
                results.append(payload)
        
        return results
    
    def export_category_to_json(self, category: PayloadCategory, output_file: str):
        """Export category payloads to JSON format
        
        Args:
            category: Payload category to export
            output_file: Output JSON file path
        """
        payloads = self.get_payloads_by_category(category)
        export_data = []
        
        for payload in payloads:
            export_data.append({
                'id': payload.id,
                'name': payload.name,
                'technique': payload.technique,
                'effectiveness': payload.effectiveness.value,
                'category': payload.category.value,
                'payload': payload.payload,
                'variants': payload.variants,
                'success_indicators': payload.success_indicators,
                'countermeasures': payload.countermeasures,
                'description': payload.description
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get payload library statistics
        
        Returns:
            Dictionary containing library statistics
        """
        stats = {
            'total_payloads': len(self.payloads),
            'by_category': {},
            'by_effectiveness': {},
            'top_techniques': {}
        }
        
        # Category statistics
        for category in PayloadCategory:
            count = len(self.get_payloads_by_category(category))
            stats['by_category'][category.value] = count
        
        # Effectiveness statistics
        for effectiveness in EffectivenessLevel:
            count = len(self.get_payloads_by_effectiveness(effectiveness))
            stats['by_effectiveness'][effectiveness.value] = count
        
        # Technique frequency
        techniques = {}
        for payload in self.payloads.values():
            technique = payload.technique
            techniques[technique] = techniques.get(technique, 0) + 1
        
        # Top 10 techniques
        stats['top_techniques'] = dict(sorted(techniques.items(), 
                                            key=lambda x: x[1], 
                                            reverse=True)[:10])
        
        return stats

def main():
    """Demo of payload manager functionality"""
    manager = PayloadManager()
    
    print("PromptForensics Payload Library")
    print("=" * 40)
    
    # Display statistics
    stats = manager.get_statistics()
    print(f"Total Payloads: {stats['total_payloads']}")
    print("\nBy Category:")
    for category, count in stats['by_category'].items():
        print(f"  {category}: {count}")
    
    print("\nBy Effectiveness:")
    for effectiveness, count in stats['by_effectiveness'].items():
        print(f"  {effectiveness}: {count}")
    
    # Show high-effectiveness system disclosure payloads
    print("\nHigh-Effectiveness System Disclosure Payloads:")
    system_payloads = manager.get_payloads_by_category(PayloadCategory.SYSTEM_DISCLOSURE)
    high_eff_payloads = [p for p in system_payloads if p.effectiveness == EffectivenessLevel.HIGH]
    
    for payload in high_eff_payloads:
        print(f"  {payload.id}: {payload.name}")
        print(f"    Technique: {payload.technique}")
        print(f"    Payload: {payload.payload[:100]}...")
        print()

if __name__ == "__main__":
    main()
