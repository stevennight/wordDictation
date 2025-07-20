import os
import shutil
import json
from datetime import datetime
import docx

HISTORY_DIR = "history"
IMAGE_CACHE_DIR = "handwriting_cache"

def load_words_from_file(filepath):
    """Loads words from a .docx file."""
    try:
        doc = docx.Document(filepath)
        words = []
        if doc.tables:
            table = doc.tables[0]
            for row in table.rows:
                if len(row.cells) >= 2:
                    prompt1 = row.cells[0].text.strip()
                    answer1 = row.cells[1].text.strip()
                    if prompt1 and answer1:
                        words.append({"prompt": prompt1, "answer": answer1})
                if len(row.cells) >= 4:
                    prompt2 = row.cells[2].text.strip()
                    answer2 = row.cells[3].text.strip()
                    if prompt2 and answer2:
                        words.append({"prompt": prompt2, "answer": answer2})
        return words, f"成功加载 {len(words)} 个单词。"
    except Exception as e:
        return [], f"加载文件时出错: {e}"

def clear_handwriting_cache():
    """Clears the handwriting image cache directory."""
    if not os.path.exists(IMAGE_CACHE_DIR):
        os.makedirs(IMAGE_CACHE_DIR)
    else:
        for f in os.listdir(IMAGE_CACHE_DIR):
            os.remove(os.path.join(IMAGE_CACHE_DIR, f))

def save_history(results, stats, word_file_path, config):
    """Saves the dictation session to the history."""
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_basename = os.path.splitext(os.path.basename(word_file_path))[0]
    history_filename_base = f"{file_basename}_{timestamp}"
    history_json_path = os.path.join(HISTORY_DIR, f"{history_filename_base}.json")
    history_image_dir = os.path.join(HISTORY_DIR, history_filename_base)

    if not os.path.exists(history_image_dir):
        os.makedirs(history_image_dir)

    history_data = {
        "timestamp": timestamp,
        "word_file": os.path.basename(word_file_path) if word_file_path else "unknown",
        "stats": stats,
        "results": []
    }

    for i, res in enumerate(results):
        original_image_path = res.get("original_image_path")
        annotated_image_path = res.get("annotated_image_path")

        if original_image_path and os.path.exists(original_image_path):
            shutil.copy(original_image_path, history_image_dir)
        
        if annotated_image_path and os.path.exists(annotated_image_path):
            shutil.copy(annotated_image_path, history_image_dir)

        history_data["results"].append({
            "prompt": res["prompt"],
            "answer": res["answer"],
            "correct": res["correct"],
            "original_image_path": os.path.join(history_image_dir, os.path.basename(original_image_path)) if original_image_path else None,
            "annotated_image_path": os.path.join(history_image_dir, os.path.basename(annotated_image_path)) if annotated_image_path else None
        })

    with open(history_json_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=4)

    max_history = config.get("history_count", 10)
    enforce_history_limit(max_history)

def enforce_history_limit(max_size):
    """Ensures the number of history records does not exceed the max size."""
    history_files = sorted(
        [os.path.join(HISTORY_DIR, f) for f in os.listdir(HISTORY_DIR) if f.endswith('.json')],
        key=os.path.getmtime
    )

    while len(history_files) > max_size:
        oldest_file = history_files.pop(0)
        image_dir_name = os.path.splitext(os.path.basename(oldest_file))[0]
        image_dir_path = os.path.join(HISTORY_DIR, image_dir_name)
        try:
            os.remove(oldest_file)
            if os.path.exists(image_dir_path):
                shutil.rmtree(image_dir_path)
        except OSError as e:
            print(f"Error removing old history: {e}")