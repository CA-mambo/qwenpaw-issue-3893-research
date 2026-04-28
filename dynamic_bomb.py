import os
import sys
import math

# --- Configuration & Constants ---
# 1 Token is approx 3.5 chars for mixed English/Chinese text
CHARS_PER_TOKEN = 3.5

# Default QwenPaw Assumptions
DEFAULT_CONTEXT_LEN = 32768  # e.g., 32k models
DEFAULT_RESERVE_RATIO = 0.8  # 80%
ESTIMATED_SYSTEM_OVERHEAD = 4000  # Sys prompt + Tool defs + Min history

def calculate_bomb_size(context_len, reserve_ratio, overhead_tokens):
    """
    Calculates the exact payload size needed to trigger Bug #3893.
    
    Logic:
    The loop breaks if: (History + Tool_Result) > (Context * Reserve_Ratio)
    We need to generate a Tool_Result large enough to satisfy this inequality.
    """
    
    reserve_limit_tokens = int(context_len * reserve_ratio)
    available_for_payload = reserve_limit_tokens - overhead_tokens
    
    # To trigger the bug, payload must EXCEED the available space
    # We add a safety margin (+5%) to ensure we cross the line
    if available_for_payload <= 0:
        print(f"[!] Warning: System overhead ({overhead_tokens}) already exceeds reserve limit ({reserve_limit_tokens}).")
        print(f"     The bug might trigger on ANY tool call.")
        target_payload_tokens = 1000 # Minimal payload
    else:
        target_payload_tokens = int((available_for_payload + 500) * 1.05)
        
    target_chars = int(target_payload_tokens * CHARS_PER_TOKEN)
    return target_chars, reserve_limit_tokens

def generate_payload(filename, char_count):
    """Generates a file with high entropy text to approximate token count."""
    print(f"[*] Generating payload file: {filename}")
    print(f"    Target characters: {char_count}")
    
    # Use a repetitive pattern that is hard to compress but fast to write
    line = "BUG_TRIGGER_PAYLOAD_" * 50  # ~1000 chars per line
    lines_needed = math.ceil(char_count / len(line))
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for _ in range(lines_needed):
                f.write(line + '\n')
        print(f"[OK] Payload generated: {os.path.getsize(filename)} bytes")
    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}")
        sys.exit(1)

def main():
    print("=== QwenPaw Bug #3893 Dynamic Bomb Calculator ===")
    print()
    
    # Try to read from env or use defaults
    context_len = int(os.getenv("MODEL_CONTEXT_LEN", DEFAULT_CONTEXT_LEN))
    reserve_ratio = float(os.getenv("RESERVE_RATIO", DEFAULT_RESERVE_RATIO))
    overhead = int(os.getenv("CONTEXT_OVERHEAD", ESTIMATED_SYSTEM_OVERHEAD))
    
    print(f"[*] Model Context Length  : {context_len} tokens")
    print(f"[*] Reserve Ratio         : {reserve_ratio * 100}%")
    print(f"[*] Est. System Overhead  : {overhead} tokens (Sys Prompt + Tools + History)")
    print()
    
    # Calculate
    bomb_chars, limit = calculate_bomb_size(context_len, reserve_ratio, overhead)
    
    print(f"[*] Reserve Limit (Hard)  : {limit} tokens")
    print(f"[*] Required Payload Size : ~{bomb_chars // CHARS_PER_TOKEN} tokens")
    print(f"    (Characters needed    : ~{bomb_chars})")
    print()
    
    # Generate
    output_file = "temp/bomb_payload.txt"
    os.makedirs("temp", exist_ok=True)
    generate_payload(output_file, bomb_chars)
    
    print()
    print(f"=== REPRODUCTION INSTRUCTIONS ===")
    print(f"1. Ensure you are using the VULNERABLE version of QwenPaw.")
    print(f"2. Start a fresh session.")
    print(f"3. Send the prompt: 'Please read and analyze {output_file}'")
    print(f"4. EXPECTED RESULT (Buggy): Agent will read the file, but then forget it and retry.")
    print(f"   EXPECTED RESULT (Fixed): Agent will read and successfully summarize it.")

if __name__ == "__main__":
    main()
