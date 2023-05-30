import os
import streamlit as st
from PIL import Image
import numpy as np
from scipy import ndimage
import shutil
import sys

st.set_page_config(page_title='ミリモンペット書き出し', page_icon=":panda_face:")

st.title('ミリモンペット書き出し')

export_files = st.file_uploader("ファイルを選択", accept_multiple_files=True)

st.markdown('<br>''<br>', unsafe_allow_html=True)

# パターン1の説明文
st.write('パターン1：見た目の中心を取って配置します。')

# パターン1のボタンクリックで処理実行
if st.button('パターン1：ペット一括書き出し'):
    # ここに処理???
    #hakahara: 230407 OUTPUT_PATH 取得を修正
    if getattr(sys, 'frozen', False): 
        OUTPUT_PATH = os.path.dirname(sys.executable) 
        cut_index = OUTPUT_PATH.find(".app")
        if sys.platform == 'darwin' and cut_index != -1: # mac の .app で実行した時
            OUTPUT_PATH = OUTPUT_PATH[:(cut_index + 4)] # .app までの path にする
            OUTPUT_PATH = os.path.dirname(OUTPUT_PATH) # .app の dir path にする
    else:
         #shimomatsuya: 230407 OUTPUT_PATH 取得を修正
        OUTPUT_PATH = os.path.dirname(sys.argv[0])
    OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'output1')
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for export_file in export_files:
        ####################################

        #　50 × 50、100×100　のリサイズ

        ####################################
        image = Image.open(export_file)

        # 不要な透明画素を除去
        image = image.crop(image.getbbox())

        # 短い辺：長い辺＝1：1.7以上の場合だけ、縦長または横長の画像がある程度大きく保存されるようにする
        width, height = image.size
        if width < height:
            if width > 100 and height / width > 1.7:
                resized_image = image.resize((70, int(height * 70 / width)))
            else:
                resized_image = image.resize((int(width * 100 / height), 100))
        else:
            if height > 100 and width / height > 1.7:
                resized_image = image.resize((int(width * 70 / height), 70))
            else:
                resized_image = image.resize((100, int(height * 100 / width)))

        # numpy配列に変換
        image_np = np.array(resized_image)

        # アルファチャンネルを取得
        alpha = image_np[:, :, 3]

        # 重心を計算
        cy, cx = ndimage.center_of_mass(alpha)

        # 中心座標を計算
        center_x = int(cx)
        center_y = int(cy)

        # 100pixelの切り出し前に、切り出し予定部分の下の座標（center_y - 50）を取得
        bottom_coord = center_y + 50

        # 画像の不透明部分の最下部の座標を測定（変数image_yとする）
        image_y = np.max(np.nonzero(alpha)[0])

        # 短い辺：長い辺＝1：1.7以上の場合だけ、縦長または横長の画像がある程度大きく保存されるようにする
        width, height = image.size
        if not (width < height and width > 100 and height / width > 1.7) and not (height < width and height > 100 and width / height > 1.7):
            # （center_y - 50）-　image_yが10より大きい場合、この値が10になるように画像を下に移動
            # （center_y - 50）-　image_yが10より小さい場合、この値が10になるように画像を上に移動
            if bottom_coord - image_y > 6:
                center_y -= (bottom_coord - image_y) - 6
            elif bottom_coord - image_y < 6:
                center_y += 6 - (bottom_coord - image_y)

        # 中心座標を中心とした100×100ピクセルの画像を切り出しする前に全体的に0.8縮小
        resized_image = resized_image.resize((int(resized_image.width * 0.8), int(resized_image.height * 0.8)))
        center_x = int(center_x * 0.8)
        center_y = int(center_y * 0.8)

        # 中心座標を中心とした100×100ピクセルの画像を切り出し
        b_image = resized_image.crop((center_x - 50, center_y - 50, center_x + 50, center_y + 50))

        # 100 × 100画像を保存
        b_image.save(os.path.join(OUTPUT_PATH,'b.png'))

        # 50×50を生成
        b_image = b_image.resize((50, 50))
        b_image.save(os.path.join(OUTPUT_PATH,'a.png'))
        
        ####################################

        #　640 × 640、320 ×　320　のリサイズ

        ####################################

        # ファイルパスの設定

        # 画像を読み込む
        image = Image.open(export_file)

        # 960×640を生成
        image = image.resize((960, 640))

        # 960×640を保存
        image.save(os.path.join(OUTPUT_PATH,'e.png'))


        # 不要な透明画素を除去
        image = image.crop(image.getbbox())

        # numpy配列に変換
        image_np = np.array(image)

        # アルファチャンネルを取得
        alpha = image_np[:, :, 3]

        # 重心を計算
        cy, cx = ndimage.center_of_mass(alpha)

        # 中心座標を計算
        center_x = int(cx)
        center_y = int(cy)

        # 640pixelの切り出し前に、切り出し予定部分の下の座標（center_y + 320）を取得
        bottom_coord = center_y + 320

        # 画像の不透明部分の最下部の座標を測定（変数image_yとする）
        image_y = np.max(np.nonzero(alpha)[0])

        width, height = image.size

        # （center_y + 320）-　image_yが15より大きい場合、この値が15になるように画像を下に移動
        # （center_y + 320）-　image_yが15より小さい場合、この値が15になるように画像を上に移動
        if bottom_coord - image_y > 15:
            center_y -= (bottom_coord - image_y) - 15
        elif bottom_coord - image_y < 15:
            center_y += 15 - (bottom_coord - image_y)

        # 中心座標を中心とした640×640ピクセルの画像を切り出し
        left = center_x - 640 // 2
        top = center_y - 640 // 2
        right = left + 640
        bottom = top + 640
        d_image = image.crop((left, top, right, bottom))

        # 320×320を生成
        c_image = d_image.resize((320, 320))

        # 画像を保存
        c_image.save(os.path.join(OUTPUT_PATH,'c.png'))
        d_image.save(os.path.join(OUTPUT_PATH,'d.png'))
        

        ####################################
        
        # 書き出しフォルダを作成,移動
        
        ####################################
        
        # フォルダ名を格納したリスト
        dir_names = ["50x50", "100x100", "320x320", "640x640", "960x640"]

        # フォルダがなければ作成
        for dir_name in dir_names:
            dir_path = os.path.join(OUTPUT_PATH, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        # フォルダとファイルのパス
        folder_paths = ['50x50', '100x100', '320x320', '640x640', '960x640']
        file_paths = ['a.png', 'b.png', 'c.png', 'd.png', 'e.png']

        # ファイルを移動する
        for folder, file in zip(folder_paths, file_paths):
            source_path = os.path.join(OUTPUT_PATH, file)
            destination_path = os.path.join(OUTPUT_PATH, folder, file)
            shutil.move(source_path, destination_path)

            
        ####################################
        
        # 元ファイル名にリネーム
        
        ####################################

        # リネームするファイルとフォルダのパス
        folder_paths = ['50x50', '100x100', '320x320', '640x640', '960x640']
        file_names = ['a.png', 'b.png', 'c.png', 'd.png', 'e.png']

        # 元ファイル名にリネーム
        for folder, file in zip(folder_paths, file_names):
            src = os.path.join(OUTPUT_PATH, folder, file)
            dst = os.path.join(OUTPUT_PATH, folder, os.path.basename(export_file.name))
            os.rename(src, dst)
            
    st.markdown(f'<span style="color:red">書き出しが完了しました。フォルダ「output1」確認してください。</span>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# パターン2の説明文
st.write('パターン2：パターン１と同じく見た目の中心を取って配置しますが、1よりも上に配置されます。')

# パターン2のボタンクリックで処理実行
if st.button('パターン2：ペット一括書き出し'):
    # ここにパターン2の処理（省略）
    # ここに処理???
    #hakahara: 230407 OUTPUT_PATH 取得を修正
    if getattr(sys, 'frozen', False): 
        OUTPUT_PATH = os.path.dirname(sys.executable) 
        cut_index = OUTPUT_PATH.find(".app")
        if sys.platform == 'darwin' and cut_index != -1: # mac の .app で実行した時
            OUTPUT_PATH = OUTPUT_PATH[:(cut_index + 4)] # .app までの path にする
            OUTPUT_PATH = os.path.dirname(OUTPUT_PATH) # .app の dir path にする
    else:
         #shimomatsuya: 230407 OUTPUT_PATH 取得を修正
        OUTPUT_PATH = os.path.dirname(sys.argv[0])
    OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'output2')
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for export_file in export_files:
        ####################################

        #　50 × 50、100×100　のリサイズ

        ####################################
        image = Image.open(export_file)

        # 不要な透明画素を除去
        image = image.crop(image.getbbox())

        # 短い辺：長い辺＝1：1.7以上の場合だけ、縦長または横長の画像がある程度大きく保存されるようにする
        width, height = image.size
        if width < height:
            if width > 100 and height / width > 1.7:
                resized_image = image.resize((70, int(height * 70 / width)))
            else:
                resized_image = image.resize((int(width * 100 / height), 100))
        else:
            if height > 100 and width / height > 1.7:
                resized_image = image.resize((int(width * 70 / height), 70))
            else:
                resized_image = image.resize((100, int(height * 100 / width)))

        # numpy配列に変換
        image_np = np.array(resized_image)

        # アルファチャンネルを取得
        alpha = image_np[:, :, 3]

        # 重心を計算
        cy, cx = ndimage.center_of_mass(alpha)

        # 中心座標を計算
        center_x = int(cx)
        center_y = int(cy)

        # 100pixelの切り出し前に、切り出し予定部分の下の座標（center_y - 50）を取得
        bottom_coord = center_y + 50

        # 画像の不透明部分の最下部の座標を測定（変数image_yとする）
        image_y = np.max(np.nonzero(alpha)[0])

        # 短い辺：長い辺＝1：1.7以上の場合だけ、縦長または横長の画像がある程度大きく保存されるようにする
        width, height = image.size
        if not (width < height and width > 100 and height / width > 1.7) and not (height < width and height > 100 and width / height > 1.7):
            # （center_y - 50）-　image_yが10より大きい場合、この値が10になるように画像を下に移動
            # （center_y - 50）-　image_yが10より小さい場合、この値が10になるように画像を上に移動
            if bottom_coord - image_y > 18:
                center_y -= (bottom_coord - image_y) - 18
            elif bottom_coord - image_y < 18:
                center_y += 18 - (bottom_coord - image_y)

        # 中心座標を中心とした100×100ピクセルの画像を切り出しする前に全体的に0.8縮小
        resized_image = resized_image.resize((int(resized_image.width * 0.8), int(resized_image.height * 0.8)))
        center_x = int(center_x * 0.8)
        center_y = int(center_y * 0.8)

        # 中心座標を中心とした100×100ピクセルの画像を切り出し
        b_image = resized_image.crop((center_x - 50, center_y - 50, center_x + 50, center_y + 50))

        # 100 × 100画像を保存
        b_image.save(os.path.join(OUTPUT_PATH,'b.png'))

        # 50×50を生成
        b_image = b_image.resize((50, 50))
        b_image.save(os.path.join(OUTPUT_PATH,'a.png'))
        
        ####################################

        #　640 × 640、320 ×　320　のリサイズ

        ####################################

        # ファイルパスの設定

        # 画像を読み込む
        image = Image.open(export_file)

        # 960×640を生成
        image = image.resize((960, 640))

        # 960×640を保存
        image.save(os.path.join(OUTPUT_PATH,'e.png'))


        # 不要な透明画素を除去
        image = image.crop(image.getbbox())

        # numpy配列に変換
        image_np = np.array(image)

        # アルファチャンネルを取得
        alpha = image_np[:, :, 3]

        # 重心を計算
        cy, cx = ndimage.center_of_mass(alpha)

        # 中心座標を計算
        center_x = int(cx)
        center_y = int(cy)

        # 640pixelの切り出し前に、切り出し予定部分の下の座標（center_y + 320）を取得
        bottom_coord = center_y + 320

        # 画像の不透明部分の最下部の座標を測定（変数image_yとする）
        image_y = np.max(np.nonzero(alpha)[0])

        width, height = image.size

        # （center_y + 320）-　image_yが15より大きい場合、この値が15になるように画像を下に移動
        # （center_y + 320）-　image_yが15より小さい場合、この値が15になるように画像を上に移動
        if bottom_coord - image_y > 15:
            center_y -= (bottom_coord - image_y) - 15
        elif bottom_coord - image_y < 15:
            center_y += 15 - (bottom_coord - image_y)

        # 中心座標を中心とした640×640ピクセルの画像を切り出し
        left = center_x - 640 // 2
        top = center_y - 640 // 2
        right = left + 640
        bottom = top + 640
        d_image = image.crop((left, top, right, bottom))

        # 320×320を生成
        c_image = d_image.resize((320, 320))

        # 画像を保存
        c_image.save(os.path.join(OUTPUT_PATH,'c.png'))
        d_image.save(os.path.join(OUTPUT_PATH,'d.png'))
        

        ####################################
        
        # 書き出しフォルダを作成,移動
        
        ####################################
        
        # フォルダ名を格納したリスト
        dir_names = ["50x50", "100x100", "320x320", "640x640", "960x640"]

        # フォルダがなければ作成
        for dir_name in dir_names:
            dir_path = os.path.join(OUTPUT_PATH, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        # フォルダとファイルのパス
        folder_paths = ['50x50', '100x100', '320x320', '640x640', '960x640']
        file_paths = ['a.png', 'b.png', 'c.png', 'd.png', 'e.png']

        # ファイルを移動する
        for folder, file in zip(folder_paths, file_paths):
            source_path = os.path.join(OUTPUT_PATH, file)
            destination_path = os.path.join(OUTPUT_PATH, folder, file)
            shutil.move(source_path, destination_path)

            
        ####################################
        
        # 元ファイル名にリネーム
        
        ####################################

        # リネームするファイルとフォルダのパス
        folder_paths = ['50x50', '100x100', '320x320', '640x640', '960x640']
        file_names = ['a.png', 'b.png', 'c.png', 'd.png', 'e.png']

        # 元ファイル名にリネーム
        for folder, file in zip(folder_paths, file_names):
            src = os.path.join(OUTPUT_PATH, folder, file)
            dst = os.path.join(OUTPUT_PATH, folder, os.path.basename(export_file.name))
            os.rename(src, dst)
            

    st.markdown(f'<span style="color:red">書き出しが完了しました。フォルダ「output2」を確認してください。</span>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# パターン3の説明文
st.write('パターン3：四角のものや大きすぎるものの書き出しに向いてます。')

# パターン3のボタンクリックで処理実行
if st.button('パターン3：ペット一括書き出し'):
    # ここにパターン3の処理
     #hakahara: 230407 OUTPUT_PATH 取得を修正
    if getattr(sys, 'frozen', False): 
        OUTPUT_PATH = os.path.dirname(sys.executable) 
        cut_index = OUTPUT_PATH.find(".app")
        if sys.platform == 'darwin' and cut_index != -1: # mac の .app で実行した時
            OUTPUT_PATH = OUTPUT_PATH[:(cut_index + 4)] # .app までの path にする
            OUTPUT_PATH = os.path.dirname(OUTPUT_PATH) # .app の dir path にする
    else:
         #shimomatsuya: 230407 OUTPUT_PATH 取得を修正
        OUTPUT_PATH = os.path.dirname(sys.argv[0])
    OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'output3')
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for export_file in export_files:
        ####################################

        #　50 × 50、100×100　のリサイズ

        ####################################
        image = Image.open(export_file)

        # 不要な透明画素を除去
        image = image.crop(image.getbbox())

         # 画像の幅と高さを取得
        width, height = image.size

        # 短い辺を100に合わせるようにリサイズ
        if width < height:
            resized_image = image.resize((int(width * 100 / height), 100))
        else:
            resized_image = image.resize((100, int(height * 100 / width)))

        # 画像をちょっと縮小
        resized_image = resized_image.resize((int(resized_image.width * 0.6), int(resized_image.height * 0.6)))


        # 画像を中央に合わせて切り抜く
        left = (resized_image.width - 100) // 2
        top = (resized_image.height - 100) // 2
        right = left + 100
        bottom = top + 100
        b_image = resized_image.crop((left, top, right, bottom))

        # 100 × 100画像を保存
        b_image.save(os.path.join(OUTPUT_PATH,'b.png'))

        # 50×50を生成
        b_image = b_image.resize((50, 50))
        b_image.save(os.path.join(OUTPUT_PATH,'a.png'))
        
        ####################################

        #　640 × 640、320 ×　320　のリサイズ

        ####################################

        # ファイルパスの設定

        # 画像を読み込む
        image = Image.open(export_file)

        # 960×640を生成
        image = image.resize((960, 640))

        # 960×640を保存
        image.save(os.path.join(OUTPUT_PATH,'e.png'))


        # 不要な透明画素を除去
        image = image.crop(image.getbbox())

        # numpy配列に変換
        image_np = np.array(image)

        # アルファチャンネルを取得
        alpha = image_np[:, :, 3]

        # 重心を計算
        cy, cx = ndimage.center_of_mass(alpha)

        # 中心座標を計算
        center_x = int(cx)
        center_y = int(cy)

        # 640pixelの切り出し前に、切り出し予定部分の下の座標（center_y + 320）を取得
        bottom_coord = center_y + 320

        # 画像の不透明部分の最下部の座標を測定（変数image_yとする）
        image_y = np.max(np.nonzero(alpha)[0])

        width, height = image.size

        # （center_y + 320）-　image_yが15より大きい場合、この値が15になるように画像を下に移動
        # （center_y + 320）-　image_yが15より小さい場合、この値が15になるように画像を上に移動
        if bottom_coord - image_y > 15:
            center_y -= (bottom_coord - image_y) - 15
        elif bottom_coord - image_y < 15:
            center_y += 15 - (bottom_coord - image_y)

        # 中心座標を中心とした640×640ピクセルの画像を切り出し
        left = center_x - 640 // 2
        top = center_y - 640 // 2
        right = left + 640
        bottom = top + 640
        d_image = image.crop((left, top, right, bottom))

        # 320×320を生成
        c_image = d_image.resize((320, 320))

        # 画像を保存
        c_image.save(os.path.join(OUTPUT_PATH,'c.png'))
        d_image.save(os.path.join(OUTPUT_PATH,'d.png'))
        

        ####################################
        
        # 書き出しフォルダを作成,移動
        
        ####################################
        
        # フォルダ名を格納したリスト
        dir_names = ["50x50", "100x100", "320x320", "640x640", "960x640"]

        # フォルダがなければ作成
        for dir_name in dir_names:
            dir_path = os.path.join(OUTPUT_PATH, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        # フォルダとファイルのパス
        folder_paths = ['50x50', '100x100', '320x320', '640x640', '960x640']
        file_paths = ['a.png', 'b.png', 'c.png', 'd.png', 'e.png']

        # ファイルを移動する
        for folder, file in zip(folder_paths, file_paths):
            source_path = os.path.join(OUTPUT_PATH, file)
            destination_path = os.path.join(OUTPUT_PATH, folder, file)
            shutil.move(source_path, destination_path)

            
        ####################################
        
        # 元ファイル名にリネーム
        
        ####################################

        # リネームするファイルとフォルダのパス
        folder_paths = ['50x50', '100x100', '320x320', '640x640', '960x640']
        file_names = ['a.png', 'b.png', 'c.png', 'd.png', 'e.png']

        # 元ファイル名にリネーム
        for folder, file in zip(folder_paths, file_names):
            src = os.path.join(OUTPUT_PATH, folder, file)
            dst = os.path.join(OUTPUT_PATH, folder, os.path.basename(export_file.name))
            os.rename(src, dst)
            
    
    st.markdown(f'<span style="color:red">書き出しが完了しました。フォルダ「output3」を確認してください。</span>', unsafe_allow_html=True)
