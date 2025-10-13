# Empire Custom Module Development Guide

## Module Structure
- **Location**: `/usr/share/powershell-empire/empire/server/modules/python/`
- **Categories**: code_execution, collection, discovery, exploit, lateral_movement, management, persistence, privesc, situational_awareness, trollsploit

## Creating Custom Python Modules

### Required Files (per module):
1. **module_name.py** - Python execution logic
2. **module_name.yaml** - Module configuration and metadata

### Template Structure:

#### YAML Template:
```yaml
name: Custom Module Name
authors:
 - name: Author Name
 handle: '@handle'
 link: https/github.com/author
description: |
 Description of what the module does
software:
techniques:
 - T1XXX # MITRE ATT&CK techniques
background: false
output_extension:
needs_admin: false
opsec_safe: true
language: python
min_language_version: '3.6'
comments:
 - 'Custom module for exercise'
options:
 - name: Agent
 description: Agent to run module on
 required: true
 value: ''
 - name: CustomParam
 description: Custom parameter description
 required: true
 value: 'default_value'
script: |
 # Your Python code here
 import base64
 # Use {{ CustomParam }} for parameter substitution
```

#### Python Template:
```python
from empire.server.common.empire import MainMenu
from empire.server.core.module_models import EmpireModule
from empire.server.utils.module_util import handle_error_message

class Module:
 @staticmethod
 def generate(
 main_menu: MainMenu,
 module: EmpireModule,
 params: dict,
 obfuscate: bool = False,
 obfuscation_command: str = "",
 ) -> tuple[str | None, str | None]:
 # Get module source code
 script, err = main_menu.modulesv2.get_module_source(
 module_name=module.script_path,
 obfuscate=obfuscate,
 obfuscate_command=obfuscation_command,
 )

 if err:
 return handle_error_message(err)

 # Parameter substitution
 for key, value in params.items():
 if key.lower() not in ["agent", "computername"]:
 script = script.replace("{{ " + key + " }}", value)
 script = script.replace("{{" + key + "}}", value)

 return script
```

## Installation Process

1. **Create module directory**: Choose appropriate category
2. **Place files**: Both .py and .yaml files in category folder
3. **Set permissions**: Ensure readable by Empire process
4. **Restart Empire server**: For module registration
5. **Verify in Starkiller**: Module appears in UI

## Custom Module Categories
- **collection/**: Data gathering modules
- **privesc/**: Privilege escalation
- **persistence/**: Maintaining access
- **lateral_movement/**: Network propagation
- **situational_awareness/**: Reconnaissance
- **code_execution/**: Command execution
- **discovery/**: System/network discovery

## Security Considerations
- All modules run with agent privileges
- OPSEC safety depends on implementation
- Admin requirements should be clearly marked
- Background execution for long-running tasks