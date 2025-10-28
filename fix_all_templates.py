#!/usr/bin/env python3
"""
Script to add playbook_suffix and playbook_name display to all default templates
"""

# Read the config file
with open('iris_intelowl_module_2/IrisIntelowlConfig.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements to make (OLD → NEW)
replacements = [
    # Table IDs
    ('id=\\"il_in_anrep\\"', 'id=\\"il_in_anrep_{{ playbook_suffix }}\\"'),
    ('id=\\"il_in_corep\\"', 'id=\\"il_in_corep_{{ playbook_suffix }}\\"'),
    ('id=\\"drop_anrep\\"', 'id=\\"drop_anrep_{{ playbook_suffix }}\\"'),
    ('id=\\"drop_corep\\"', 'id=\\"drop_corep_{{ playbook_suffix }}\\"'),
    ('id=\\"drop_an\\"', 'id=\\"drop_an_{{ playbook_suffix }}\\"'),
    ('id=\\"drop_co\\"', 'id=\\"drop_co_{{ playbook_suffix }}\\"'),
    ('id=\\"drop_r_intelowl\\"', 'id=\\"drop_r_intelowl_{{ playbook_suffix }}\\"'),
    ('id=\\"drop_raw_intelowl\\"', 'id=\\"drop_raw_intelowl_{{ playbook_suffix }}\\"'),
    ("id='intelowl_raw_ace'", "id='intelowl_raw_ace_{{ playbook_suffix }}'"),
    
    # Aria attributes
    ('aria-labelledby=\\"drop_an\\"', 'aria-labelledby=\\"drop_an_{{ playbook_suffix }}\\"'),
    ('aria-labelledby=\\"drop_co\\"', 'aria-labelledby=\\"drop_co_{{ playbook_suffix }}\\"'),
    ('aria-labelledby=\\"drop_r_intelowl\\"', 'aria-labelledby=\\"drop_r_intelowl_{{ playbook_suffix }}\\"'),
    
    # Data attributes
    ('data-target=\\"#drop_anrep\\"', 'data-target=\\"#drop_anrep_{{ playbook_suffix }}\\"'),
    ('data-target=\\"#drop_corep\\"', 'data-target=\\"#drop_corep_{{ playbook_suffix }}\\"'),
    ('data-target=\\"#drop_raw_intelowl\\"', 'data-target=\\"#drop_raw_intelowl_{{ playbook_suffix }}\\"'),
    
    # Aria controls
    ('aria-controls=\\"drop_anrep\\"', 'aria-controls=\\"drop_anrep_{{ playbook_suffix }}\\"'),
    ('aria-controls=\\"drop_corep\\"', 'aria-controls=\\"drop_corep_{{ playbook_suffix }}\\"'),
    ('aria-controls=\\"drop_raw_intelowl\\"', 'aria-controls=\\"drop_raw_intelowl_{{ playbook_suffix }}\\"'),
    
    # JavaScript variable and jQuery selectors
    ('var intelowl_in_raw = ace.edit(\\"intelowl_raw_ace\\"', 'var intelowl_in_raw_{{ playbook_suffix }} = ace.edit(\\"intelowl_raw_ace_{{ playbook_suffix }}\\"'),
    ('intelowl_in_raw.set', 'intelowl_in_raw_{{ playbook_suffix }}.set'),
    ('intelowl_in_raw.session', 'intelowl_in_raw_{{ playbook_suffix }}.session'),
    ('intelowl_in_raw.renderer', 'intelowl_in_raw_{{ playbook_suffix }}.renderer'),
    ('$(\\"#il_in_anrep\\")', '$(\\"#il_in_anrep_{{ playbook_suffix }}\\"'),
    ('$(\\"#il_in_corep\\")', '$(\\"#il_in_corep_{{ playbook_suffix }}\\"'),
    
    # Headers with playbook name display
    ('<h3>General information</h3>', '<h3>📊 IntelOwl Report: {{ playbook_name }}</h3>'),
    ('<h3>Additional information</h3>', '<h3>🔍 Analysis Results</h3>'),
    ('<h3>IntelOwl raw results</h3>', '<h3>📄 Raw JSON Response</h3>'),
]

print("Applying replacements...")
for old, new in replacements:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"✓ Replaced '{old[:50]}...' ({count} times)")

# Write back
with open('iris_intelowl_module_2/IrisIntelowlConfig.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All templates updated successfully!")
print("\nVerifying...")

# Verify
import iris_intelowl_module_2.IrisIntelowlConfig as config

all_good = True
for item in config.module_configuration:
    if 'template' in item['param_name']:
        template = item['default']
        
        has_suffix = '{{ playbook_suffix }}' in template
        has_name = '{{ playbook_name }}' in template
        
        if has_suffix and has_name:
            suffix_count = template.count('{{ playbook_suffix }}')
            print(f"✅ {item['param_name']}: {suffix_count} playbook_suffix, playbook_name display: YES")
        else:
            print(f"❌ {item['param_name']}: MISSING required variables!")
            all_good = False

if all_good:
    print("\n🎉 SUCCESS! Ready to rebuild and install!")
