import os
import argparse
import yaml
from schema_loader import load_yaml_file
from rules import check_required_keys
from fixer import auto_fix
from deepdiff import DeepDiff
from rich.console import Console
from rich import print
from rich.table import Table

console = Console()

def run_validation(template, config, fix_output_path=None):
    missing = check_required_keys(template, config)
    diff = DeepDiff(template, config, ignore_order=True)

    if missing:
        console.print("[red]❌ Missing keys:[/red]")
        for key in missing:
            console.print(f"  - [yellow]{key}[/yellow]")
    if diff:
        console.print("[yellow]⚠️ Structural or value differences:[/yellow]")
        console.print(diff.pretty())

    if not missing and not diff:
        console.print("[green]✅ Configuration is valid.[/green]")
        return

    if fix_output_path:
        fixed_config = auto_fix(template, config)
        with open(fix_output_path, "w") as f:
            yaml.dump(fixed_config, f, default_flow_style=False)
        console.print(f"[cyan]🔧 Auto-fixed configuration written to: {fix_output_path}[/cyan]")

def validate_specific_env(template_dir, env_name, fix=False):
    template_path = os.path.join(template_dir, "template.yaml")
    env_templates_dir = os.path.join(template_dir, "env_templates")
    env_path = os.path.join(env_templates_dir, f"{env_name}.yaml")

    if not os.path.exists(env_path):
        console.print(f"[red]❌ Environment config not found: {env_path}[/red]")
        return

    template = load_yaml_file(template_path)
    config = load_yaml_file(env_path)

    console.print(f"\n[bold blue]🔍 Validating environment:[/bold blue] {env_name}")

    missing = check_required_keys(template, config)
    diff = DeepDiff(template, config, ignore_order=True)

    if missing:
        console.print("[red]❌ Missing keys:[/red]")
        for key in missing:
            console.print(f"  - [yellow]{key}[/yellow]")
    if diff:
        console.print("[yellow]⚠️ Structural or value differences:[/yellow]")
        console.print(diff.pretty())

    if not missing and not diff:
        console.print("[green]✅ Environment config is valid.[/green]")
        return

    if fix:
        fixed_config = auto_fix(template, config)
        fixed_filename = f"{env_name}_fixed.yaml"
        fixed_path = os.path.join(env_templates_dir, fixed_filename)

        with open(fixed_path, "w") as f:
            yaml.dump(fixed_config, f, default_flow_style=False)

        console.print(f"[cyan]🔧 Auto-fixed config written to: {fixed_path}[/cyan]")

def validate_envs(template_dir, fix=False):
    template_path = os.path.join(template_dir, "template.yaml")
    env_dir = os.path.join(template_dir, "env_templates")

    base_template = load_yaml_file(template_path)
    console.print(f"\n[bold blue]🔍 Validating all environments in:[/bold blue] {template_dir}")

    summary = []

    for env_file in os.listdir(env_dir):
        if not env_file.endswith(".yaml") or env_file.endswith("_fixed.yaml"):
            continue

        env_name = env_file.replace(".yaml", "")
        env_path = os.path.join(env_dir, env_file)
        env_config = load_yaml_file(env_path)

        console.print(f"\n🌍 [bold]Environment: [cyan]{env_name}[/cyan][/bold]")

        missing = check_required_keys(base_template, env_config)
        diff = DeepDiff(base_template, env_config, ignore_order=True)

        fixed_filename = ""
        status = ""

        if not missing and not diff:
            console.print("[green]✅ Environment config is valid.[/green]")
            status = "✅ Valid"
        else:
            status = "❌ Issues Found"

            if missing:
                console.print("[red]❌ Missing keys:[/red]")
                for key in missing:
                    console.print(f"  - [yellow]{key}[/yellow]")

            if diff:
                console.print("[yellow]⚠️ Structural or value differences:[/yellow]")
                console.print(diff.pretty())

            if fix:
                fixed_config = auto_fix(base_template, env_config)
                fixed_filename = env_file.replace(".yaml", "_fixed.yaml")
                fixed_path = os.path.join(env_dir, fixed_filename)

                with open(fixed_path, "w") as f:
                    yaml.dump(fixed_config, f, default_flow_style=False)

                console.print(f"[cyan]🔧 Auto-fixed config written to: {fixed_path}[/cyan]")

        summary.append((env_name, status, fixed_filename or "—"))

    # Print Summary Table
    print("\n[bold green]📊 Validation Summary[/bold green]\n")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Environment")
    table.add_column("Status")
    table.add_column("Fixed File")

    for env_name, status, fixed_file in summary:
        table.add_row(env_name, status, fixed_file)

    console.print(table)

def validate_and_fix(config_path, template_path, fix_output_path=None):
    template = load_yaml_file(template_path)
    config = load_yaml_file(config_path)

    console.print(f"\n[bold blue]Validating:[/bold blue] {config_path} against template: {template_path}")
    run_validation(template, config, fix_output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI YAML Validator")
    parser.add_argument('--template', required=True, help='Template name (e.g., dotnet, python-publish)')
    parser.add_argument('--input', help='Path to YAML file to validate')
    parser.add_argument('--fix', action='store_true', help='Enable auto-fix')
    parser.add_argument('--envs', action='store_true', help='Validate all environment-specific files')
    parser.add_argument('--env', help='Validate a specific environment config (e.g., dev, staging, prod)')

    args = parser.parse_args()
    template_dir = os.path.join("templates", args.template)
    template_path = os.path.join(template_dir, "template.yaml")

    if args.env:
        validate_specific_env(template_dir, args.env, fix=args.fix)
    elif args.envs:
        validate_envs(template_dir, fix=args.fix)
    elif args.input:
        output_path = None
        if args.fix:
            base_name = os.path.basename(args.input).replace(".yaml", "_fixed.yaml")
            output_path = os.path.join(os.path.dirname(args.input), base_name)
        validate_and_fix(args.input, template_path, fix_output_path=output_path)
    else:
        console.print("[red]❌ Please specify --env, --envs, or --input[/red]")
