# QwenPaw Issue #3893 Research Package

This repository contains deep-dive analysis, root cause verification, and reproduction scripts for **QwenPaw Issue #3893** (Context Sync Race Condition).

**🔒 Status: Archived / Mitigated in Official Release v1.1.5.**

## 📂 Overview

During the investigation of Issue #3893 and PR #3895, we identified that the root cause of the "Context Amnesia" bug was more nuanced than a simple "Swap Order" fix. This repo provides evidence that a robust solution requires **both** our proposed logic swap **and** a Fallback mechanism.

### 🛡️ Official Fix (v1.1.5)
The official team has released a "Physical Defense" mitigation in v1.1.5:
1.  **Source Truncation**: `read_file` and other tools now enforce a `DEFAULT_MAX_BYTES` (50KB) limit.
2.  **Post-Acting Hook**: A new `_prune_tool_result` hook runs before reasoning to strip oversized results.
3.  **Result**: The "bomb" payload is now truncated at the source, making the underlying architectural `break` logic unreachable in standard workflows.

## 🧪 Scenarios Covered

1. **Scenario A: The "CoT Accumulation" Trap** (High Complexity)
   - *Problem:* Agent loses its Chain of Thought (CoT) when the combined context (CoT + Tool Pair) exceeds the reserve limit, even if the Tool Pair fits.
   - *Fix:* **Logic Swap** (Validate before Budget Check).
2. **Scenario B: The "Giant Tool Result" Deadlock** (High Load)
   - *Problem:* A single tool output exceeds the reserve limit. The loop breaks immediately at `k=1`.
   - *Fix:* **Fallback Mechanism** (Force keep latest message).

## 📄 Contents

| File | Description |
| :--- | :--- |
| `root_cause_analysis.md` | Detailed technical analysis of both scenarios and the proposed solution. |
| `reproduce_3893.md` | Step-by-step guide to reproduce the bugs locally. |
| `simulate_cot_explosion.py` | Script to verify Scenario A (CoT Trap) and the benefit of the Logic Swap. |
| `verify_giant_tool_result.py` | Script to verify Scenario B (Giant Result) and the need for Fallback. |
| `reviewer_fallback_test.py` | Proof that the Reviewer's Fallback alone is insufficient for Scenario A. |
| `dynamic_bomb.py` | Payload generator to trigger the bug in a real agent environment. |
| `as_msg_handler.py.original` | Backup of the original source file (`v0.0.x`). |

## 🚀 How to Run

Ensure you have Python (and `uv` if preferred) installed.

```bash
# Test Scenario A (CoT Trap)
python simulate_cot_explosion.py

# Test Scenario B (Giant Result)
python verify_giant_tool_result.py

# Generate a real-world payload
python dynamic_bomb.py
```

## 🔗 References

- **Issue:** [agentscope-ai/QwenPaw#3893](https://github.com/agentscope-ai/QwenPaw/issues/3893) (Closed)
- **PR:** [agentscope-ai/QwenPaw#3895](https://github.com/agentscope-ai/QwenPaw/pull/3895) (Closed)
