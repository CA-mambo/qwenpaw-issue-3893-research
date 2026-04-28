import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=== 🧪 Simulation: Can 'Swap Order' save a 'Giant Tool Result'? ===")
print("Target: Verify if swapping logic fixes the case where a single tool output > Reserve.")
print()

# --- Scenario Setup ---
# Reserve Limit = 20,000 tokens
# ToolResult = 25,000 tokens (Single message exceeds Reserve!)
RESERVE_LIMIT = 20_000
TOOL_RESULT_SIZE = 25_000
CO_T_SIZE = 10_000
TOOL_USE_SIZE = 1_000

# Messages Sequence: [CoT, ToolUse, ToolResult]
# Index 0: CoT (Text)
# Index 1: ToolUse (Validates with Result)
# Index 2: ToolResult (Validates with Use)

messages = [
    {"id": "msg_0", "type": "text", "tokens": CO_T_SIZE},           # CoT
    {"id": "msg_1", "type": "tool_use", "tokens": TOOL_USE_SIZE, "tid": "abc"}, # Use
    {"id": "msg_2", "type": "tool_result", "tokens": TOOL_RESULT_SIZE, "tid": "abc"} # Result
]

print(f"📊 Setup:")
print(f"   Reserve Limit     : {RESERVE_LIMIT}")
print(f"   CoT (msg_0)       : {CO_T_SIZE}")
print(f"   ToolUse (msg_1)   : {TOOL_USE_SIZE}")
print(f"   ToolResult (msg_2): {TOOL_RESULT_SIZE} (⚠️ > Reserve!)")
print()

def validate_alignment(slice_msgs):
    """Simplified validation logic"""
    use_ids = {m["tid"] for m in slice_msgs if m["type"] == "tool_use"}
    res_ids = {m["tid"] for m in slice_msgs if m["type"] == "tool_result"}
    return use_ids == res_ids

def run_test(logic_name, check_order):
    """
    check_order: 'budget_first' (Original) or 'validate_first' (Swap)
    """
    print(f"🔄 Testing: {logic_name}")
    best_keep_count = 0
    
    for k in range(1, len(messages) + 1):
        # Slice from back: k=1 -> [Result], k=2 -> [Use, Result], k=3 -> [CoT, Use, Result]
        slice_msgs = messages[-k:]
        keep_tokens = sum(m["tokens"] for m in slice_msgs)
        
        # Log Trace
        is_valid = validate_alignment(slice_msgs)
        
        if check_order == "budget_first":
            # 1. Budget Check
            if keep_tokens > RESERVE_LIMIT:
                print(f"   [k={k}] Slice size {keep_tokens} > {RESERVE_LIMIT}. 💥 BREAK (Budget)")
                break # Die here
            # 2. Validate
            if is_valid:
                best_keep_count = k
                print(f"   [k={k}] Valid & Budget OK. Update Best -> {k}")
                
        else: # Validate First
            # 1. Validate
            if is_valid:
                best_keep_count = k
                print(f"   [k={k}] Valid. Tentatively Update Best -> {k}")
            
            # 2. Budget Check
            if keep_tokens > RESERVE_LIMIT:
                print(f"   [k={k}] Slice size {keep_tokens} > {RESERVE_LIMIT}. 💥 BREAK (Budget)")
                break
                
        if k == 1 and keep_tokens > RESERVE_LIMIT:
            print(f"   [!] Note: Single Result exceeds limit, breaks immediately in both cases.")
            
    print(f"   Final Result: kept {best_keep_count} messages.")
    if best_keep_count == 0:
        print(f"   ❌ DEADLOCK: Context wiped. Agent amnesia.")
    else:
        print(f"   ✅ SURVIVED: Agent remembers something.")
    print()

print("="*50)
run_test("Scenario A: Original (Budget First)", "budget_first")
print("="*50)
run_test("Scenario B: Swap Order (Validate First)", "validate_first")

print("="*50)
print("🧠 Analysis:")
print("In 'Scenario B', at k=1 (just Result), validation FAILS (isolated).")
print("Budget check hits immediately because 25k > 20k.")
print("Loop breaks at k=1. It NEVER reaches k=2 where validation would pass.")
print("Result: Swap Order does NOT solve the 'Giant Tool Result' case.")
print("Conclusion: You are right. Fallback logic is strictly required.")
