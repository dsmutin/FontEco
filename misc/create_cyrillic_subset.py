from fonteco.font_utils import create_subset_font, subset_font_to_alphanumeric_and_cyrillic

def main():
    input_font = "fonts/TimesNewRoman.ttf"
    output_font = "fonts/TimesNewRoman_subset.ttf"  # Overwrite the existing file
    
    print(f"Re-subsetting {input_font}...")
    create_subset_font(input_font, output_font, subset_font_to_alphanumeric_and_cyrillic)
    print("Done!")

if __name__ == "__main__":
    main() 