import os

def convert_to_txt(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                continue  # Skip already converted files
                
            file_path = os.path.join(root, file)
            file_name, file_ext = os.path.splitext(file_path)
            
            new_file_path = file_name + '.txt'
            
            try:
                with open(file_path, 'r') as source_file:
                    content = source_file.read()
                
                with open(new_file_path, 'w') as target_file:
                    target_file.write(content)
                    
                print(f"Converted '{file}' to '{new_file_path}'")
                
                os.remove(file_path)
                print(f"Removed old file '{file_path}'")
            except Exception as e:
                print(f"Failed to convert '{file}': {str(e)}")

if __name__ == '__main__':
    convert_to_txt('PNP-ZA')