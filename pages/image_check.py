import streamlit as st
import os
from PIL import Image

# 画像サイズチェック関数
def check_image_sizes(base_folder):
    has_issue = False
    subfolders = [f.path for f in os.scandir(base_folder) if f.is_dir() and not f.name.startswith('.') and f.name != "画像解析用素材"]

    issue_messages = []

    for subfolder in subfolders:
        try:
            expected_width, expected_height = map(int, os.path.basename(subfolder).split('x'))
        except ValueError:
            issue_messages.append(f"⚠️ フォルダ名が適切ではありません: {os.path.basename(subfolder)}（例: '960x640'）")
            continue

        for filename in os.listdir(subfolder):
            if filename.endswith(".png"):
                file_path = os.path.join(subfolder, filename)
                with Image.open(file_path) as img:
                    width, height = img.size

                    if width != expected_width or height != expected_height:
                        message = f"❌ サイズ不一致: {filename} (フォルダ: {os.path.basename(subfolder)}) → {width}x{height}"
                        issue_messages.append(message)
                        has_issue = True

    return issue_messages if has_issue else ["✅ ファイルサイズ確認：問題なし"]

# 960フォルダのIDチェック
def check_files(base_folder, pasted_text):
    has_issue = False
    image_folder = os.path.join(base_folder, "960x640")

    if not os.path.isdir(image_folder):
        return ["❌ '960x640' フォルダが見つかりません。"]

    filenames = {f for f in os.listdir(image_folder) if f.endswith(".png")}
    ids_from_text = {line.split()[0] + ".png" for line in pasted_text.strip().split("\n") if line}

    extra_files = sorted(list(filenames - ids_from_text))
    missing_files = sorted(list(ids_from_text - filenames))

    results = []
    if extra_files:
        for file in extra_files:
            results.append(f"⚠️ 余分なファイル: {file}")
        has_issue = True

    if missing_files:
        for file in missing_files:
            results.append(f"❗ ファイルがありません: {file}")
        has_issue = True

    return results if has_issue else ["✅ 960のIDチェック：問題なし"]

# 画像の左右判定
def determine_image_side(image_path):
    with Image.open(image_path) as img:
        img = img.convert('RGBA')

        left_box = (0, 0, 480, 640)
        right_box = (480, 0, 960, 640)

        left_img = img.crop(left_box)
        right_img = img.crop(right_box)

        left_data = left_img.getdata()
        right_data = right_img.getdata()

        left_has_image = any(pixel[3] != 0 for pixel in left_data)
        right_has_image = any(pixel[3] != 0 for pixel in right_data)

        if left_has_image:
            return "右"
        elif right_has_image:
            return "左"
        else:
            return "どちらにも絵がありません"

# 左右情報チェック関数
def check_image_sides(base_folder, pasted_text):
    image_folder = os.path.join(base_folder, "960x640")
    if not os.path.isdir(image_folder):
        return ["❌ '960x640' フォルダが見つかりません。"]

    results = []
    has_issue = False

    for line in pasted_text.strip().split("\n"):
        parts = line.split()
        if len(parts) < 2:
            continue  # 「ID タグ」の形式になっていない場合はスキップ

        file_id, tag_info = parts[0], " ".join(parts[1:])

        if "ペット" in tag_info and ("左" in tag_info or "右" in tag_info):
            img_file_path = os.path.join(image_folder, file_id + ".png")

            if os.path.exists(img_file_path):
                image_side = determine_image_side(img_file_path)
                expected_side = "左" if "左" in tag_info else "右"

                if image_side != expected_side:
                    results.append(f"❌ 不一致: {file_id}.png → 画像: {image_side}, 指定: {expected_side}")
                    has_issue = True
                else:
                    results.append(f"✅ 一致: {file_id}.png → {expected_side}")

    return results if has_issue else ["✅ 左右判定チェック：問題なし"]

# 640フォルダの画像が他のフォルダにもあるかチェック
def check_640_images(base_folder):
    sizes = ["50x50", "100x100", "320x320", "640x640"]
    results = []

    base_folder_path = os.path.join(base_folder, "640x640")
    if not os.path.isdir(base_folder_path):
        return ["❌ '640x640' フォルダが見つかりません。"]

    base_images = set(os.listdir(base_folder_path))

    for size in sizes:
        if size == "640x640":
            continue  # 640x640はチェック対象外

        size_folder = os.path.join(base_folder, size)
        if not os.path.isdir(size_folder):
            results.append(f"⚠️ フォルダが見つかりません: {size}")
            continue

        size_images = set(os.listdir(size_folder))

        missing_images = base_images - size_images
        for img in missing_images:
            results.append(f"❗ 不足: {img} → {size}")

        extra_images = size_images - base_images
        for img in extra_images:
            results.append(f"⚠️ 余分: {img} → {size}")

    return results if results else ["✅ すべてのフォルダに適切な画像があります！"]

# Streamlit UI
st.title("画像チェック統合ツール")

# フォルダパス入力
# base_folder = st.text_input("チェックするフォルダのパスを入力:", "")
# 固定フォルダパスを設定
base_folder = r"C:\Users\shimomatsuya_s\Desktop\業務\チェック\書き出しチェック"

# ユーザーがパスを変更できないようにテキストを表示（変更不可）
st.write(f"📁 チェック対象フォルダ: {base_folder}")


# IDリスト入力
st.write("IDリストを以下に貼り付けてください（例: ID + タグ）")
pasted_text = st.text_area("IDリスト:", "", height=150)

# 画像サイズチェック
if st.button("画像サイズチェック実行"):
    if base_folder and os.path.isdir(base_folder):
        results = check_image_sizes(base_folder)
        for result in results:
            st.write(result)
    else:
        st.error("正しいフォルダパスを入力してください。")

# 960のIDチェック
if st.button("960のIDチェック実行"):
    if base_folder and os.path.isdir(base_folder) and pasted_text.strip():
        results = check_files(base_folder, pasted_text)
        for result in results:
            st.write(result)
    else:
        st.error("正しいフォルダパスとIDリストを入力してください。")

# 左右判定チェック
if st.button("左右判定チェック実行"):
    if base_folder and os.path.isdir(base_folder) and pasted_text.strip():
        results = check_image_sides(base_folder, pasted_text)
        for result in results:
            st.write(result)
    else:
        st.error("正しいフォルダパスとIDリストを入力してください。")

# 640フォルダのチェック
if st.button("640フォルダの画像存在チェック実行"):
    if base_folder and os.path.isdir(base_folder):
        results = check_640_images(base_folder)
        for result in results:
            st.write(result)
    else:
        st.error("正しいフォルダパスを入力してください。")
