import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=== 🧪 Final Proof: Why Reviewer's Fallback is NOT Enough ===")
print("Target: Prove that the 'best == 0 Fallback' fails to save the CoT in Scenario A.")
print()

# --- Scenario Setup ---
# Reserve = 20k
# CoT = 18k (Huge)
# Tool Pair = 6k (Small)
# Total = 24k (> Reserve)

RESERVE_LIMIT = 20_000
CO_T_SIZE = 18_000
TOOL_USE_SIZE = 1_000
TOOL_RESULT_SIZE = 5_000

messages = [
    {"id": "msg_0", "type": "text", "tokens": CO_T_SIZE},           # CoT
    {"id": "msg_1", "type": "tool_use", "tokens": TOOL_USE_SIZE, "tid": "abc"}, # Use
    {"id": "msg_2", "type": "tool_result", "tokens": TOOL_RESULT_SIZE, "tid": "abc"} # Result
]

print(f"📊 Setup:")
print(f"   Reserve Limit     : {RESERVE_LIMIT}")
print(f"   CoT (msg_0)       : {CO_T_SIZE}")
print(f"   ToolUse (msg_1)   : {TOOL_USE_SIZE}")
print(f"   ToolResult (msg_2): {TOOL_RESULT_SIZE}")
print()

def validate_alignment(slice_msgs):
    use_ids = {m["tid"] for m in slice_msgs if m["type"] == "tool_use"}
    res_ids = {m["tid"] for m in slice_msgs if m["type"] == "tool_result"}
    return use_ids == res_ids

def run_test_with_fallback(logic_name):
    """
    Simulates the code with the Reviewer's Fallback logic:
    if best_keep_count == 0: best_keep_count = 1
    """
    print(f"🔄 Testing: {logic_name} + Reviewer's Fallback")
    best_keep_count = 0
    kept_msgs = []

    for k in range(1, len(messages) + 1):
        slice_msgs = messages[-k:]
        keep_tokens = sum(m["tokens"] for m in slice_msgs)
        is_valid = validate_alignment(slice_msgs)
        
        if logic_name == "Original":
            # 1. Budget Check FIRST
            if keep_tokens > RESERVE_LIMIT:
                print(f"   [k={k}] Budget Exceeded ({keep_tokens} > {RESERVE_LIMIT}). 💥 BREAK")
                break # Die here
            # 2. Validate
            if is_valid:
                best_keep_count = k
                print(f"   [k={k}] Valid & Budget OK. Update Best -> {k}")
        else: # Fixed
            # 1. Validate FIRST
            if is_valid:
                best_keep_count = k
                print(f"   [k={k}] Valid. Update Best -> {k}")
            # 2. Budget Check SECOND
            if keep_tokens > RESERVE_LIMIT:
                print(f"   [k={k}] Budget Exceeded ({keep_tokens} > {RESERVE_LIMIT}). 💥 BREAK")
                break

    # Reviewer's Fallback Logic
    print(f"   [Fallback Check] Is best_keep_count == 0? -> {best_keep_count == 0}")
    if best_keep_count == 0 and messages:
        print(f"   [!] FALLBACK TRIGGERED! Force keeping latest 1 message.")
        best_keep_count = 1
    
    # Analyze result
    if best_keep_count > 0:
        kept_msgs = messages[-best_keep_count:]
        kept_types = [m["type"] for m in kept_msgs]
        has_cot = "text" in kept_types and any(m["tokens"] > 10000 for m in kept_msgs if m["type"] == "text")
        print(f"   Final: Kept {best_keep_count} messages. Types: {kept_types}")
        if has_cot:
            print(f"   ✅ CoT SAVED. Agent has full context.")
        else:
            print(f"   ❌ PARTIAL AMNESIA: CoT is LOST! Agent only remembers tool pair.")

print("="*60)
run_test_with_fallback("Original")
print("="*60)
run_test_with_fallback("Fixed (PR #3895)")
