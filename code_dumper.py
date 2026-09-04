import os

# ১. প্রজেক্টের রুট ডিরেক্টরি এবং আউটপুট ফাইল
PROJECT_ROOT = "."  # প্রজেক্টের মূল ফোল্ডারে এটি রান করবেন
OUTPUT_FILE = "clean_source_code.txt"

# ২. যেসব ফোল্ডার পুরোপুরি ইগনোর করা হবে (অটো-জেনারেটেড ও ক্যাশ ফাইল বাদ দিতে)
EXCLUDED_DIRS = {
    'venv', '.venv', 'env', 'ENV', '__pycache__', '.git', 
    'node_modules', '.idea', '.vscode', 'migrations', 
    'static', 'staticfiles', 'media', 'build', 'dist', '.pytest_cache'
}

# ৩. শুধুমাত্র যেসব এক্সটেনশনের সোর্স ফাইল প্রসেস করা হবে
ALLOWED_EXTENSIONS = {
    '.py', '.html', '.js', '.css', '.json', '.sh'
}

# ৪. নির্দিষ্ট যেসব ফাইল বাদ দিতে চান
EXCLUDED_FILES = {
    'db.sqlite3', 'package-lock.json', 'yarn.lock', OUTPUT_FILE, 'export_code.py'
}

def create_clean_code_dump():
    file_count = 0
    total_lines = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # ইগনোর করা ফোল্ডারগুলোর ভেতরে যাওয়া বন্ধ করা
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

            for file in files:
                if file in EXCLUDED_FILES:
                    continue
                
                ext = os.path.splitext(file)[1].lower()
                # শুধুমাত্র অনুমোদিত সোর্স ফাইল বা নির্দিষ্ট কিছু কনফিগ ফাইল নেওয়া
                if ext in ALLOWED_EXTENSIONS or file in ['Dockerfile', 'requirements.txt']:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, PROJECT_ROOT)

                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                            lines = infile.readlines()
                            
                        outfile.write(f"\n{'='*70}\n")
                        outfile.write(f"FILE PATH: {rel_path}\n")
                        outfile.write(f"{'='*70}\n\n")
                        outfile.writelines(lines)
                        outfile.write("\n\n")

                        file_count += 1
                        total_lines += len(lines)
                    except Exception as e:
                        print(f"Error reading {rel_path}: {e}")

    print(f"Done! Successfully extracted {file_count} core source files ({total_lines} lines total) into '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    create_clean_code_dump()