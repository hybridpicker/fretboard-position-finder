import os
from jsmin import jsmin
from cssmin import cssmin

def minify_files():
    for root, dirs, files in os.walk("."):
        for file in files:
            if (file.endswith(".js") and not file.endswith(".min.js")) or (file.endswith(".css") and not file.endswith(".min.css")):
                input_file_path = os.path.join(root, file)
                
                if file.endswith(".js"):
                    output_file_path = input_file_path.replace(".js", ".min.js")
                elif file.endswith(".css"):
                    output_file_path = input_file_path.replace(".css", ".min.css")
                
                if not os.path.exists(output_file_path):
                    with open(input_file_path, 'r', encoding='utf-8') as input_file:
                        content = input_file.read()
                    
                    if file.endswith(".js"):
                        minified_content = jsmin(content)
                    elif file.endswith(".css"):
                        minified_content = cssmin(content)
                    
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        output_file.write(minified_content)
                    
                    print(f"Minified {input_file_path} to {output_file_path}")
                else:
                    print(f"Minified file already exists: {output_file_path}")

if __name__ == "__main__":
    minify_files()
