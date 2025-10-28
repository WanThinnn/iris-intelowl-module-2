#!/usr/bin/env python3
"""
Safe template updater - adds playbook_suffix to all IDs without breaking Python syntax
"""

import re

# Read the config file
config_path = 'iris_intelowl_module_2/IrisIntelowlConfig.py'

with open(config_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Updating templates safely...")

# Find and replace patterns in the long template strings
# These are escaped in Python strings, so we match the escaped version

replacements = [
    # Main table IDs
    (r'id=\\"il_in_anrep\\"', r'id=\\"il_in_anrep_{{ playbook_suffix }}\\"'),
    (r'id=\\"il_in_corep\\"', r'id=\\"il_in_corep_{{ playbook_suffix }}\\"'),
    
    # Collapse IDs
    (r'id=\\"drop_anrep\\"', r'id=\\"drop_anrep_{{ playbook_suffix }}\\"'),
    (r'id=\\"drop_corep\\"', r'id=\\"drop_corep_{{ playbook_suffix }}\\"'),
    (r'id=\\"drop_an\\"', r'id=\\"drop_an_{{ playbook_suffix }}\\"'),
    (r'id=\\"drop_co\\"', r'id=\\"drop_co_{{ playbook_suffix }}\\"'),
    (r'id=\\"drop_r_intelowl\\"', r'id=\\"drop_r_intelowl_{{ playbook_suffix }}\\"'),
    (r'id=\\"drop_raw_intelowl\\"', r'id=\\"drop_raw_intelowl_{{ playbook_suffix }}\\"'),
    
    # ACE editor ID (with single quotes)
    (r"id='intelowl_raw_ace'", r"id='intelowl_raw_ace_{{ playbook_suffix }}'"),
    
    # Aria labelledby
    (r'aria-labelledby=\\"drop_an\\"', r'aria-labelledby=\\"drop_an_{{ playbook_suffix }}\\"'),
    (r'aria-labelledby=\\"drop_co\\"', r'aria-labelledby=\\"drop_co_{{ playbook_suffix }}\\"'),
    (r'aria-labelledby=\\"drop_r_intelowl\\"', r'aria-labelledby=\\"drop_r_intelowl_{{ playbook_suffix }}\\"'),
    
    # Data-target
    (r'data-target=\\"#drop_anrep\\"', r'data-target=\\"#drop_anrep_{{ playbook_suffix }}\\"'),
    (r'data-target=\\"#drop_corep\\"', r'data-target=\\"#drop_corep_{{ playbook_suffix }}\\"'),
    (r'data-target=\\"#drop_raw_intelowl\\"', r'data-target=\\"#drop_raw_intelowl_{{ playbook_suffix }}\\"'),
    
    # Aria-controls
    (r'aria-controls=\\"drop_anrep\\"', r'aria-controls=\\"drop_anrep_{{ playbook_suffix }}\\"'),
    (r'aria-controls=\\"drop_corep\\"', r'aria-controls=\\"drop_corep_{{ playbook_suffix }}\\"'),
    (r'aria-controls=\\"drop_raw_intelowl\\"', r'aria-controls=\\"drop_raw_intelowl_{{ playbook_suffix }}\\"'),
    
    # JavaScript: ace.edit() - already has suffix from previous fix, so update variable name
    (r'var intelowl_in_raw = ace\.edit\(\\"intelowl_raw_ace', r'var intelowl_in_raw_{{ playbook_suffix }} = ace.edit(\\"intelowl_raw_ace_{{ playbook_suffix }}'),
    
    # JavaScript: intelowl_in_raw. -> intelowl_in_raw_{{ playbook_suffix }}.
    (r'\\nintelowl_in_raw\.', r'\\nintelowl_in_raw_{{ playbook_suffix }}.'),
    
    # jQuery selectors in JavaScript
    (r'\$\(\\\\"#il_in_anrep\\\\"\)', r'$(\\\"#il_in_anrep_{{ playbook_suffix }}\\\")'),
    (r'\$\(\\\\"#il_in_corep\\\\"\)', r'$(\\\"#il_in_corep_{{ playbook_suffix }}\\\")'),
]

for old_pattern, new_pattern in replacements:
    matches = len(re.findall(old_pattern, content))
    if matches > 0:
        content = re.sub(old_pattern, new_pattern, content)
        print(f"  ✓ Replaced pattern ({matches} times): {old_pattern[:50]}...")

# Write back
with open(config_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Templates updated successfully!")

# Verify syntax
print("\n🔍 Verifying Python syntax...")
try:
    compile(content, config_path, 'exec')
    print("✅ Python syntax is VALID!")
except SyntaxError as e:
    print(f"❌ SYNTAX ERROR: {e}")
    print(f"   Line {e.lineno}: {e.text}")
    exit(1)

# Import and verify
print("\n🔍 Verifying module import...")
import iris_intelowl_module_2.IrisIntelowlConfig as config

all_good = True
for item in config.module_configuration:
    if 'template' in item['param_name']:
        template = item['default']
        count = template.count('{{ playbook_suffix }}')
        
        if count > 0:
            print(f"  ✅ {item['param_name']}: {count} instances")
        else:
            print(f"  ❌ {item['param_name']}: MISSING playbook_suffix!")
            all_good = False

if all_good:
    print("\n🎉 SUCCESS! All templates have playbook_suffix!")
    print("📦 Now rebuild: ./install_to_docker.sh")
else:
    print("\n⚠️ Some templates still need fixing")
