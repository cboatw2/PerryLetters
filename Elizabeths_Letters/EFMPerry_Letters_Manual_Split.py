#To manually split Elizabeth's letters 
#edit the last line of code: 
#split_letter(30, 21, output_folder) ie: splits Letter 30 after line 21
#run in terminal
cd /Users/crboatwright/PerryLetters
sqlite3 BFPerryLetters.db "SELECT name FROM sqlite_master WHERE type='table';"
import re
from pathlib import Path
import shutil

def renumber_letters(output_folder):
    """Renumber all letters sequentially starting from 1"""
    output_folder = Path(output_folder)
    
    # Get all letter files and sort them numerically
    letter_files = []
    for f in output_folder.glob("Letter_*.txt"):
        try:
            num = int(f.stem.split('_')[1])
            letter_files.append((num, f))
        except (ValueError, IndexError):
            continue
    
    letter_files.sort(key=lambda x: x[0])
    
    # Create a temporary directory for renaming
    temp_dir = output_folder / "temp_rename"
    temp_dir.mkdir(exist_ok=True)
    
    # First, move all files to temp directory with new names
    for idx, (old_num, old_file) in enumerate(letter_files, start=1):
        # Read content
        content = old_file.read_text(encoding='utf-8')
        
        # Update the "Letter N" header
        lines = content.split('\n')
        if lines[0].startswith("Letter "):
            lines[0] = f"Letter {idx}"
        
        # Write to temp directory with new number
        temp_file = temp_dir / f"Letter_{idx}.txt"
        temp_file.write_text('\n'.join(lines), encoding='utf-8')
    
    # Delete all original letter files
    for _, old_file in letter_files:
        old_file.unlink()
    
    # Move all files from temp directory back to main directory
    for temp_file in temp_dir.glob("Letter_*.txt"):
        final_path = output_folder / temp_file.name
        shutil.move(str(temp_file), str(final_path))
    
    # Remove temp directory
    temp_dir.rmdir()
    
    print(f"Renumbered {len(letter_files)} letters")

def split_letter(letter_num, split_after_line, output_folder):
    """
    Split a letter at a specific line number.
    
    Args:
        letter_num: The letter number to split (e.g., 30)
        split_after_line: Line number after which to split (e.g., 21)
        output_folder: Path to the folder containing the letters
    """
    output_folder = Path(output_folder)
    letter_file = output_folder / f"Letter_{letter_num}.txt"
    
    if not letter_file.exists():
        print(f"Error: {letter_file} not found!")
        return
    
    # Read the letter
    with open(letter_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the header line (should be "Letter N")
    header_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("Letter "):
            header_idx = i
            break
    
    # Calculate actual split point (accounting for header and blank line)
    # Line numbers user provides are content lines, not including "Letter N" header
    actual_split = header_idx + 1 + split_after_line  # +1 for blank line after header
    
    if actual_split >= len(lines):
        print(f"Error: Line {split_after_line} exceeds letter length!")
        return
    
    # Split into two parts
    first_part = lines[:actual_split + 1]  # +1 to include the split line
    second_part = lines[actual_split + 1:]  # Everything after
    
    # Write first part (overwrite original)
    with open(letter_file, 'w', encoding='utf-8') as f:
        f.writelines(first_part)
    
    # Create a new letter file for the second part
    # Use a unique number that won't conflict
    existing_nums = [int(f.stem.split('_')[1]) for f in output_folder.glob("Letter_*.txt")]
    temp_num = max(existing_nums) + 1000 if existing_nums else 9999
    temp_file = output_folder / f"Letter_{temp_num}.txt"
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(f"Letter {temp_num}\n\n")
        # Skip any leading blank lines in second part
        content_started = False
        for line in second_part:
            if not content_started and line.strip():
                content_started = True
            if content_started:
                f.write(line)
    
    print(f"Split Letter_{letter_num} at line {split_after_line}")
    print(f"Created temporary Letter_{temp_num}.txt")
    
    # Now renumber all letters
    renumber_letters(output_folder)
    
    print(f"\nAll letters renumbered successfully!")
    print(f"Original Letter_{letter_num} is now split into Letter_{letter_num} and Letter_{letter_num + 1}")

# Example usage:
if __name__ == "__main__":
    output_folder = "/Users/crboatwright/PerryLetters/Elizabeths_Letters/EFMPerry_Letters_split"
    
    # Split Letter 30 after line 21 (counting content lines, not including header)
    split_letter(30, 21, output_folder)