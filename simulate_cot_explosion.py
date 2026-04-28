import sys

# Set encoding to avoid Windows console errors
sys.stdout.reconfigure(encoding='utf-8')

print("=== 🧪 Experiment: Long Chain of Thought + Short Tool Call ===")
print("Target: Prove why 'Logic Fix' > 'Config Tweak' for preserving reasoning memory.")
print()

# --- Scenario Setup ---
# Simulating a 128k Model Context with 80% Reserve (Standard Config)
# Or a 32k Model with high usage.
RESERVE_LIMIT = 25_000  # Tokens

# Message Components
HISTORY = 5_000     # Previous turns
CoT = 22_100        # Long thinking process (Complex Task!) - Slightly increased to breach limit
TOOL_USE = 1_000    # Short tool call (e.g., edit_file)
TOOL_RESULT = 2_000 # Short result

print(f"📊 Setup:")
print(f"   Reserve Limit : {RESERVE_LIMIT} tokens")
print(f"   History       : {HISTORY} tokens")
print(f"   CoT (Thinking): {CoT} tokens (Deep Reasoning)")
print(f"   Tool Call     : {TOOL_USE} tokens")
print(f"   Tool Result   : {TOOL_RESULT} tokens")

TOTAL_TOKENS = HISTORY + CoT + TOOL_USE + TOOL_RESULT
print(f"   Total Context : {TOTAL_TOKENS} tokens (EXCEEDS Reserve!)")
print()

# --- Logic Simulation ---

# Messages Order: [History, CoT, ToolUse, Result]
# Loop iterates backwards:
# 1. [Result]
# 2. [ToolUse, Result] -> Valid Pair
# 3. [CoT, ToolUse, Result] -> Includes CoT
# 4. [History, CoT, ToolUse, Result]

def run_simulation(logic_name, swap_order):
    """
    swap_order=True  -> Fixed Logic (Validate then Check Limit)
    swap_order=False -> Buggy Logic (Check Limit then Validate)
    """
    print(f"🔄 Running: {logic_name}")
    
    # The loop in context manager effectively builds slices from back to front.
    # Let's simulate the accumulation.
    
    # Slice 1: Result
    slice_1 = TOOL_RESULT
    is_valid_1 = False # No Tool Use yet
    
    # Slice 2: ToolUse, Result
    slice_2 = TOOL_USE + TOOL_RESULT
    is_valid_2 = True  # Atomic Pair Found!
    
    # Slice 3: CoT, ToolUse, Result
    slice_3 = CoT + TOOL_USE + TOOL_RESULT
    is_valid_3 = True  # Still Valid (Tool Pair is intact)
    
    # Slice 4: History...
    slice_4 = HISTORY + CoT + TOOL_USE + TOOL_RESULT
    is_valid_4 = True

    # The Logic
    best_keep = 0
    saved_tokens = 0

    # We process from smallest slice (2) to largest (4)
    # Slice 1 is invalid, ignore.
    
    # Check Slice 2
    if not swap_order: # Buggy: Limit Check FIRST
        if slice_2 > RESERVE_LIMIT:
            print(f"   [Limit Check] Slice 2 ({slice_2}) > Reserve. BREAK.")
        else:
            # Validate
            if is_valid_2:
                best_keep = 2
                saved_tokens = slice_2
    else: # Fixed: Validate FIRST
        if is_valid_2:
            best_keep = 2
            saved_tokens = slice_2
        
        if slice_2 > RESERVE_LIMIT:
            pass # Break logic applies here, but slice 2 is small
    
    # Check Slice 3 (Adding CoT)
    # Current best is 2 (Tool Pair). Now we try to add CoT.
    # In the real loop, if Slice 2 was valid, we try to expand to Slice 3.
    
    # Buggy Logic
    if not swap_order:
        if slice_3 > RESERVE_LIMIT:
            print(f"   [Limit Check] Slice 3 ({slice_3}) > Reserve. BREAK.")
            print(f"   -> Loop terminates. Best remains: Slice 2 ({saved_tokens} tokens).")
            print(f"   -> RESULT: CoT LOST! Agent forgets reasoning.")
        else:
             if is_valid_3:
                best_keep = 3
                saved_tokens = slice_3
                
    # Fixed Logic
    else:
        # Validate
        if is_valid_3:
            print(f"   [Validate] Slice 3 is Valid (Tool alignment OK). UPDATE Best.")
            best_keep = 3
            saved_tokens = slice_3
        
        # Limit Check
        if slice_3 > RESERVE_LIMIT:
            print(f"   [Limit Check] Slice 3 ({slice_3}) > Reserve. BREAK.")
            print(f"   -> Loop terminates. But Best was updated!")
            print(f"   -> RESULT: CoT SAVED! Agent keeps reasoning logic.")
        else:
            pass

    print(f"   Final Memory: {saved_tokens} tokens kept.")
    print()

print("="*50)
run_simulation("🚫 Buggy Logic (Original)", swap_order=False)
print("="*50)
run_simulation("✅ Fixed Logic (PR #3895)", swap_order=True)

print("📝 Conclusion:")
print("Even with 'Short Tool Calls', the Long Chain of Thought (CoT) pushes the context over the limit.")
print("Buggy Code breaks BEFORE saving the CoT. -> Brainwashed Agent.")
print("Fixed Code saves the CoT BEFORE breaking. -> Smart Agent.")
