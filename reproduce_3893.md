# Reproduction Guide: Issue #3893 (Context Sync Race Condition)

This document outlines the reproduction steps and analysis for the Context Loss bug in QwenPaw, covering both the "Chain of Thought" preservation (our PR fix) and the "Giant Result" fallback (Reviewer suggestion).

## 🧪 Scenario A: The "CoT Trap" (Complex Tasks)

**Context:** Agent accumulates a long Chain of Thought (CoT) but the tool output is small.
**Problem:** In original code, when `CoT + ToolResult` exceeds `reserve`, the loop breaks *before* validating the full slice, discarding the CoT.
**Verification:** Our PR "Swap Order" fixes this.

### Reproduction Steps (Simulation)
1. Run the simulation script:
   ```powershell
   uv run python desk/debug/qwenpaw/simulate_cot_explosion.py
   ```
2. **Expected Output:**
   - **Original Logic:** Fails to keep CoT. Agent loses reasoning memory.
   - **Fixed Logic (Swap Order):** Successfully keeps the CoT slice before breaking.

---

## 🧪 Scenario B: The "Giant Result" (Heavy I/O)

**Context:** A single tool output (e.g., `cat huge.log`) is larger than `context_compact_reserve`.
**Problem:** No matter the order, a single oversized message cannot pass validation (it's isolated) and breaks the loop immediately. `best_keep_count` remains 0.
**Verification:** We need the "Fallback" logic to survive this.

### Reproduction Steps (Simulation)
1. Run the simulation script:
   ```powershell
   uv run python desk/debug/qwenpaw/verify_giant_tool_result.py
   ```
2. **Expected Output:**
   - **Original Logic:** Breaks at k=1. Context wiped.
   - **Swap Order Only:** Breaks at k=1 (validation fails for isolated result). Context still wiped.
   - **Swap + Fallback:** Detects `best=0` after loop. Force keeps the latest message. Context survived.

---

## 🛠️ Real-World Payload Generation

To test these behaviors with actual files (not just simulations):

### 1. Generate a "Giant Result" Bomb
Use this to simulate Scenario B.
```powershell
# Creates a file just large enough to trigger the break
uv run python desk/debug/qwenpaw/dynamic_bomb.py
```
*Note:* Ensure your `reserve` is lower than the generated file size.
*Prompt:* "Please analyze `temp/bomb_payload.txt`."

### 2. Generate a "Complex Context" (CoT Simulation)
To simulate Scenario A, you need a long session history.
1. Start a fresh session.
2. Engage in a long, complex reasoning task (or paste a large block of text repeatedly to fill history).
3. Once the context is ~75% full, ask the agent to perform a small tool call.
4. If the combined history + tool result exceeds the reserve, the original logic will likely discard the history (amnesia).

## 💡 Conclusion for Reviewers
- **PR #3895 (Swap Order)** is essential to prevent **CoT Amnesia** (Scenario A).
- **Reviewer Suggestion (Fallback)** is essential to prevent **Total Wipe** in extreme cases (Scenario B).
- **Recommendation:** Combine both strategies for a robust fix.
