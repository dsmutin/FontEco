from fonteco.font_utils import create_subset_font

def main():
    input_font = "fonts/Times_subset.ttf"
    output_font = "fonts/Times_subset.ttf"  # Overwrite the existing file
    
    print(f"Re-subsetting {input_font}...")
    create_subset_font(input_font, output_font)
    print("Done!")

if __name__ == "__main__":
    main() 