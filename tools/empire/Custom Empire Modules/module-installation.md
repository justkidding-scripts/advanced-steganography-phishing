# Custom Module Installation Commands

## Quick Installation Process

### 1. Install Your Custom Module
```bash
# Navigate to custom modules directory
cd /home/kali/empire-custom-modules

# Install module using helper script
./install_module.sh <category> <module_name>

# Example:
./install_module.sh collection custom_data_collector
```

### 2. Restart Empire Server
```bash
# Kill existing Empire server
sudo pkill -f empire

# Start Empire server
sudo powershell-empire server
```

### 3. Verify Module Installation
- Access Starkiller UI via ngrok URL
- Navigate to Modules section
- Look for your module in the appropriate category

## Module Development Workflow

### Step 1: Create Module Files
```bash
# Create in appropriate category folder
# Example for collection module:
vim /home/kali/empire-custom-modules/collection/my_module.yaml
vim /home/kali/empire-custom-modules/collection/my_module.py  # Optional
```

### Step 2: Test Module Syntax
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('/home/kali/empire-custom-modules/collection/my_module.yaml'))"
```

### Step 3: Install and Test
```bash
# Install module
./install_module.sh collection my_module

# Restart Empire
sudo pkill -f empire && sudo powershell-empire server

# Test in Starkiller UI
```

## File Locations Summary
- **Custom Modules**: `/home/kali/empire-custom-modules/`
- **Empire Modules**: `/usr/share/powershell-empire/empire/server/modules/python/`
- **Installer Script**: `/home/kali/empire-custom-modules/install_module.sh`
- **Templates**: Available in each category folder

## Module Categories Available
- **collection**: Data gathering
- **privesc**: Privilege escalation  
- **persistence**: Maintaining access
- **lateral_movement**: Network propagation
- **situational_awareness**: Reconnaissance
- **code_execution**: Command execution
- **discovery**: System/network discovery

## Common Module Parameters
```yaml
options:
  - name: Agent          # Required for all modules
  - name: target_path    # File/directory targets
  - name: command        # Commands to execute
  - name: output_format  # json, csv, raw
  - name: timeout        # Execution timeout
  - name: stealth_mode   # OPSEC considerations
```