import os
import argparse
from schema_loader import load_yaml_file, write_yaml_file
from fixer import fix_config
from rules import check_required_keys
from deepdiff import DeepDiff
from rich.console import Console
from rich.table import Table

console = Console()

def validate_config(template, config):
    missing_keys = check_required_keys(template, config)

    diff = DeepDiff(
        template,
        config,
        ignore_order=True,
        report_repetition=True,
        view='tree'  # For better filtering
    )

    # Filter out expected value differences (e.g., name, push branches)
    filtered_diff = {}
    if diff:
        for diff_type, changes in diff.items():
            for change in changes:
                path = str(change.path()) if hasattr(change, "path") else ""

                # Skip known/allowed differences
                if (
                    "root['name']" in path
                    or "root['on']['push']['branches']" in path
                    or "root[True]['push']['branches']" in path
                ):
                    continue

                if diff_type not in filtered_diff:
                    filtered_diff[diff_type] = []
                filtered_diff[diff_type].append(str(change))

        # Remove empty groups
        filtered_diff = {k: v for k, v in filtered_diff.items() if v}

    return {
        "missing": missing_keys,
        "diff": filtered_diff
    }


def validate_and_fix(env_file, template_path, fix_output_path=None):
    template = load_yaml_file(template_path)
    config = load_yaml_file(env_file)

    if template is None or config is None:
        return None

    result = validate_config(template, config)

    if fix_output_path and (result["missing"] or result["diff"]):
        fixed_config = fix_config(template, config)
        write_yaml_file(fix_output_path, fixed_config)
        result["fixed_path"] = fix_output_path

    return result


def validate_envs_for_template(template_name, fix=False):
    console.rule(f"Validating template: {template_name}", style="bold green")

    base_path = os.path.join("templates", template_name)
    template_path = os.path.join(base_path, "template.yaml")
    env_dir = os.path.join(base_path, "env_templates")

    if not os.path.isfile(template_path):
        console.print(f"❌ Template not found: {template_path}")
        return []

    if not os.path.isdir(env_dir):
        console.print(f"⚠️ No environment directory found: {env_dir}")
        return []

    env_files = ["dev.yaml", "staging.yaml", "prod.yaml"]
    results = []

    for env_file in env_files:
        env_path = os.path.join(env_dir, env_file)
        if not os.path.isfile(env_path):
            console.print(f"⚠️ Skipping missing environment file: {env_path}")
            continue

        fix_output_path = (
            os.path.join(env_dir, env_file.replace(".yaml", "_fixed.yaml")) if fix else None
        )

        result = validate_and_fix(env_path, template_path, fix_output_path=fix_output_path)

        if result is None:
            continue

        env_name = os.path.splitext(env_file)[0]
        status = "✅ Valid" if not result["missing"] and not result["diff"] else "❌ Issues Found"

        if status == "❌ Issues Found":
            console.print(f"\n🌍 Environment: [bold yellow]{env_name}[/bold yellow]")
            if result["missing"]:
                console.print("❌ Missing keys:")
                for key in result["missing"]:
                    console.print(f"  - {key}")

            if result["diff"]:
                console.print("⚠️ Structural or value differences:")
                for diff_type, changes in result["diff"].items():
                    for change in changes:
                        console.print(f"{change}")

            if "fixed_path" in result:
                console.print(f"🔧 Auto-fixed config written to: {result['fixed_path']}")

        results.append({
            "template": template_name,
            "environment": env_name,
            "status": status,
            "fixed": result.get("fixed_path", "-")
        })

    return results


def print_summary(results):
    if not results:
        console.print("\n[bold red]No validations were performed.[/bold red]")
        return

    console.print("\n📊 [bold underline]Validation Summary[/bold underline]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Template")
    table.add_column("Environment")
    table.add_column("Status")
    table.add_column("Fixed File")

    for res in results:
        table.add_row(res["template"], res["environment"], res["status"], res["fixed"])

    console.print(table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI YAML Validator")
    parser.add_argument(
        "--templates",
        nargs="+",
        required=True,
        help="One or more templates to validate (e.g. dotnet python-publish)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix and write output files"
    )

    args = parser.parse_args()
    all_results = []

    for template in args.templates:
        results = validate_envs_for_template(template, fix=args.fix)
        all_results.extend(results)

    print_summary(all_results)
