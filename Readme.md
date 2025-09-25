## 📘 AI YAML Validator

This project is an **AI-powered YAML configuration validator** for enterprise environments.
It validates configuration files (like GitHub Actions workflows) against environment-specific templates such as **dev**, **staging**, and **prod**.

The validator detects:

* ❌ Missing keys
* ⚠️ Structural differences (with ability to ignore known environment-based changes)
* ✅ Optionally auto-fixes the issues by generating a `_fixed.yaml`

---

## 📁 Folder Structure

```
ai_yaml_validator/
├── validator.py
├── rules.py
├── fixer.py
├── schema_loader.py
├── requirements.txt
└── templates/
    ├── dotnet/
    │   ├── template.yaml
    │   └── env_templates/
    │       ├── dev.yaml
    │       ├── staging.yaml
    │       └── prod.yaml
    └── python-publish/
        ├── template.yaml
        └── env_templates/
            ├── dev.yaml
            ├── staging.yaml
            └── prod.yaml
```

* Each `template.yaml` defines the expected structure for a workflow.
* `env_templates/` contains actual environment-specific YAMLs (`dev.yaml`, etc.)

---

## ✅ Setup Instructions

1. **Install Python**

```bash
py --version
```

Ensure Python 3.8+ is installed.

---

2. **Create a Virtual Environment**

```bash
py -m venv .venv
```

---

3. **Activate the Virtual Environment**

* **Windows (CMD):**

  ```bash
  .venv\Scripts\activate
  ```

* **Windows (PowerShell):**

  ```bash
  .venv\Scripts\Activate.ps1
  ```

* **macOS/Linux:**

  ```bash
  source .venv/bin/activate
  ```

---

4. **Install Dependencies**

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Validator

### ✅ Validate a Single Template (e.g., `dotnet`)

```bash
python validator.py --templates dotnet
```

### ✅ Validate Multiple Templates

```bash
python validator.py --templates dotnet python-publish
```

### 🛠️ Validate and Auto-Fix Missing or Misconfigured Sections

```bash
python validator.py --templates dotnet python-publish --fix
```

This will generate new files like:

```
templates/dotnet/env_templates/dev_fixed.yaml
templates/python-publish/env_templates/staging_fixed.yaml
```

Only created if issues are found.

---

## 🧠 Notes

* Structural differences in fields like `"name"` or `"branches"` under `push` are ignored automatically as they're considered environment-specific.
* If a YAML file is valid, no `_fixed.yaml` is generated.
* Only `dev.yaml`, `staging.yaml`, and `prod.yaml` are currently scanned for each template.

---

## 📦 Sample Command Summary

| Action                         | Command                                                       |
| ------------------------------ | ------------------------------------------------------------- |
| Validate only `dotnet`         | `python validator.py --templates dotnet`                      |
| Validate only `python-publish` | `python validator.py --templates python-publish`              |
| Validate both templates        | `python validator.py --templates dotnet python-publish`       |
| Validate & auto-fix            | `python validator.py --templates dotnet python-publish --fix` |

