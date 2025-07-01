<!-- ---
!-- Timestamp: 2025-05-29 20:33:00
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/MNGS-03-mngs-configuration.md
!-- --- -->

## Configuration Examples

### PATH.yaml

```yaml
# Time-stamp: "2025-01-18 00:00:34 (ywatanabe)"
# File: ./config/PATH.yaml

PATH:
  ECoG:
    f"./data/patient_{patient_id}/{date}/ecog_signal.npy"
```

### COLORS.yaml

```yaml
# Time-stamp: "2025-01-18 00:00:34 (ywatanabe)"
# File: ./config/COLORS.yaml

COLORS:
  SEIZURE_TYPE:
    "1": "red"
    "2": "orange"
    "3": "pink"
    "4": "gray"
```

Accessing configurations:

```python
import mngs
CONFIG = mngs.io.load_configs()

# Access config values
print(CONFIG.COLORS.SEIZURE_TYPE)  # {"1": "red", "2": "orange", "3": "pink", "4": "gray"}

# Resolve f-strings
patient_id = "001"
date = "2025_0101"
print(eval(CONFIG.PATH.ECoG))  # "./data/patient_001/2025_0101/ecog_signal.npy"
```

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->