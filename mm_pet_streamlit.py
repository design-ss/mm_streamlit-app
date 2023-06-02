import os
import streamlit as st
import numpy as np
from scipy import ndimage
import shutil
import sys
import base64
import zipfile
from PIL import Image, ImageOps
import threading
import time
import io

st.set_page_config(page_title='mmペット書き出し')

st.title('mmペット書き出し')

#ファイル選択
export_files = st.file_uploader("ファイルを選択", accept_multiple_files=True)

st.markdown('<br>''<br>', unsafe_allow_html=True)
st.write('圧縮前のデータを使用してください。圧縮後データだとエラーが出ます。')
st.markdown('---')


# パターン1説明
st.write('パターン1：見た目の中心を取って配置します。')

# パターン1
if st.button('パターン1：ペット一括書き出し'):

    # output1フォルダがあったら削除
    if os.path.exists('output1'):
        shutil.rmtree('output1')
    os.makedirs('output1')
    
    OUTPUT_PATH = os.getcwd()
    OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'output1')

    # フォルダが存在しないときは作成
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    
    # Create an in-memory buffer to store the zip file
    with io.BytesIO() as buffer:
        # Write the zip file to the buffer
        with zipfile.ZipFile(buffer, "w") as zip:
            for export_file in export_files:
                ####################################

                #　50 × 50、100×100　のリサイズ

                ####################################
                image = Image.open(export_file)

                # 不要な透明部分削除
                image = image.crop(image.getbbox())

                # メモ（のちほど）
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

                image_np = np.array(resized_image)
                alpha = image_np[:, :, 3]
                cy, cx = ndimage.center_of_mass(alpha)

                # 中心座標
                center_x = int(cx)
                center_y = int(cy)

                bottom_coord = center_y + 50

                # 画像の不透明部分の最下部
                image_y = np.max(np.nonzero(alpha)[0])


                width, height = image.size
                if not (width < height and width > 100 and height / width > 1.7) and not (height < width and height > 100 and width / height > 1.7):
                    # （center_y - 50）-　image_yの値により移動
                    if bottom_coord - image_y > 6:
                        center_y -= (bottom_coord - image_y) - 6
                    elif bottom_coord - image_y < 6:
                        center_y += 6 - (bottom_coord - image_y)

                # 0.8縮小
                resized_image = resized_image.resize((int(resized_image.width * 0.8), int(resized_image.height * 0.8)))
                center_x = int(center_x * 0.8)
                center_y = int(center_y * 0.8)

                # 100×100
                b_image = resized_image.crop((center_x - 50, center_y - 50, center_x + 50, center_y + 50))

                # 100 × 100保存
                b_image = Image.new("RGBA", (100, 100))

                # 50 × 50保存
                a_image = b_image.resize((50, 50))
                a_image = Image.new("RGBA", (50, 50))
                
                ####################################

                #　640 × 640、320 ×　320　のリサイズ

                ####################################

                # 画像を読み込む
                image = Image.open(export_file)

                # 960×640
                image = image.resize((960, 640))
                image = Image.new("RGBA", (960, 640))


                # 不要な透明部分削除
                image = image.crop(image.getbbox())

                image_np = np.array(image)
                alpha = image_np[:, :, 3]
                cy, cx = ndimage.center_of_mass(alpha)
                center_x = int(cx)
                center_y = int(cy)

                # 下の座標を取得
                bottom_coord = center_y + 320

                # 画像の不透明部分の最下部の座標を測定（変数image_yとする）
                image_y = np.max(np.nonzero(alpha)[0])

                width, height = image.size

            # （center_y - 50）-　image_yの値により移動
                if bottom_coord - image_y > 15:
                    center_y -= (bottom_coord - image_y) - 15
                elif bottom_coord - image_y < 15:
                    center_y += 15 - (bottom_coord - image_y)

                # 640×640
                left = center_x - 640 // 2
                top = center_y - 640 // 2
                right = left + 640
                bottom = top + 640
                d_image = image.crop((left, top, right, bottom))

                # 320×320
                c_image = d_image.resize((320, 320))

                c_image = Image.new("RGBA", (320, 320))
                d_image = Image.new("RGBA", (640, 640))
                
                
                
                 # メモリ上に画像データを保存
                with io.BytesIO() as img_buffer:
                    a_image.save(img_buffer, format="PNG")
                    zip.writestr(f"{os.path.splitext(export_file.name)[0]}/a.png", img_buffer.getvalue())
                with io.BytesIO() as img_buffer:
                    b_image.save(img_buffer, format="PNG")
                    zip.writestr(f"{os.path.splitext(export_file.name)[0]}/b.png", img_buffer.getvalue())
                with io.BytesIO() as img_buffer:
                    c_image.save(img_buffer, format="PNG")
                    zip.writestr(f"{os.path.splitext(export_file.name)[0]}/c.png", img_buffer.getvalue())
                with io.BytesIO() as img_buffer:
                    d_image.save(img_buffer, format="PNG")
                    zip.writestr(f"{os.path.splitext(export_file.name)[0]}/d.png", img_buffer.getvalue())
                with io.BytesIO() as img_buffer:
                    e_image.save(img_buffer, format="PNG")
                    zip.writestr(f"{os.path.splitext(export_file.name)[0]}/e.png", img_buffer.getvalue())

        buffer.seek(0)
                
                

                ####################################
                
                # 書き出しフォルダを作成,移動
                
                ####################################
                

                dir_names = ["50x50", "100x100", "320x320", "640x640", "960x640"]

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
    shutil.make_archive('output1', 'zip', 'output1')
        buffer.seek(0)

    st.download_button(
        label="Download ZIP",
        data=buffer,
        file_name="images.zip",
        mime="application/zip"
    )
    
    os.remove('output1.zip')

    
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('---')

# パターン2の説明
st.write('パターン2：パターン１と同じく見た目の中心を取って配置しますが、1よりも上に配置されます。')

# パターン2
if st.button('パターン2：ペット一括書き出し'):
    # output2フォルダがあったらそのフォルダを削除
    if os.path.exists('output2'):
        shutil.rmtree('output2')
    os.makedirs('output2')
    OUTPUT_PATH = os.getcwd()
    OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'output2')

    # フォルダが存在しないときは作成
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for export_file in export_files:
        ####################################

        #　50 × 50、100×100　のリサイズ

        ####################################
        image = Image.open(export_file)

        # 不要な透明部分削除
        image = image.crop(image.getbbox())

        # メモ（のちほど）
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

        image_np = np.array(resized_image)
        alpha = image_np[:, :, 3]
        cy, cx = ndimage.center_of_mass(alpha)

        # 中心座標
        center_x = int(cx)
        center_y = int(cy)

        bottom_coord = center_y + 50

        # 画像の不透明部分の最下部
        image_y = np.max(np.nonzero(alpha)[0])

        width, height = image.size
        if not (width < height and width > 100 and height / width > 1.7) and not (height < width and height > 100 and width / height > 1.7):
             # （center_y - 50）-　image_yの値により移動
            if bottom_coord - image_y > 18:
                center_y -= (bottom_coord - image_y) - 18
            elif bottom_coord - image_y < 18:
                center_y += 18 - (bottom_coord - image_y)

        # 0.8縮小
        resized_image = resized_image.resize((int(resized_image.width * 0.8), int(resized_image.height * 0.8)))
        center_x = int(center_x * 0.8)
        center_y = int(center_y * 0.8)

        #100×100保存
        b_image = resized_image.crop((center_x - 50, center_y - 50, center_x + 50, center_y + 50))
        b_image.save(os.path.join(OUTPUT_PATH,'b.png'))

        # 50×50保存
        b_image = b_image.resize((50, 50))
        b_image.save(os.path.join(OUTPUT_PATH,'a.png'))
        
        ####################################

        #　640 × 640、320 ×　320　のリサイズ

        ####################################


        # 画像を読み込む
        image = Image.open(export_file)

        # 960×640
        image = image.resize((960, 640))
        image.save(os.path.join(OUTPUT_PATH,'e.png'))


        # 不要な透明部分削除
        image = image.crop(image.getbbox())
        
        image_np = np.array(image)
        alpha = image_np[:, :, 3]
        cy, cx = ndimage.center_of_mass(alpha)
        center_x = int(cx)
        center_y = int(cy)

        bottom_coord = center_y + 320

        # 画像の不透明部分の最下部の座標を測定（変数image_yとする）
        image_y = np.max(np.nonzero(alpha)[0])

        width, height = image.size
        
       # （center_y - 50）-　image_yの値により移動
        if bottom_coord - image_y > 15:
            center_y -= (bottom_coord - image_y) - 15
        elif bottom_coord - image_y < 15:
            center_y += 15 - (bottom_coord - image_y)

        # 640×640
        left = center_x - 640 // 2
        top = center_y - 640 // 2
        right = left + 640
        bottom = top + 640
        d_image = image.crop((left, top, right, bottom))

        # 320×320
        c_image = d_image.resize((320, 320))

        c_image.save(os.path.join(OUTPUT_PATH,'c.png'))
        d_image.save(os.path.join(OUTPUT_PATH,'d.png'))
        

        ####################################
        
        # 書き出しフォルダを作成,移動
        
        ####################################
        
        dir_names = ["50x50", "100x100", "320x320", "640x640", "960x640"]

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
    
    # 削除実行　AI生成
    thread = threading.Thread(target=delete_data)
    thread.start() 
           
    st.markdown(f'<span style="color:red">書き出しが完了しました。フォルダ「output2」を確認してください。</span>', unsafe_allow_html=True)
    shutil.make_archive('output2', 'zip', 'output2')
    st.download_button(label="output2.zipをダウンロード", data=open('output2.zip', 'rb'), file_name='output2.zip', mime='application/zip')
    os.remove('output2.zip')

st.markdown('<br>', unsafe_allow_html=True)
st.markdown('---')
# パターン3の説明文
st.write('パターン3：1枚ずつ調整できます。ボタンを押すとプレビューが出ます。')

horizontal_shift = st.slider('数字を増やすほど左に移動します。', min_value=-30, max_value=30, value=0)
vertical_shift = st.slider('数字を増やすほど上に移動します。', min_value=-30, max_value=30, value=0)
scale = st.slider('数字を増やすほど拡大されます。', min_value=0.0, max_value=2.0, value=0.7)

# パターン3のボタンクリックで処理実行
if st.button('パターン3：ペット一括書き出し'):
    # output3フォルダが存在する場合、そのフォルダを削除
    if os.path.exists('output3'):
        shutil.rmtree('output3')
    os.makedirs('output3')

    OUTPUT_PATH = os.getcwd()
    OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'output3')

    # フォルダが存在しない時は作成
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for export_file in export_files:
        ####################################

        #　50 × 50、100×100　のリサイズ

        ####################################
        image = Image.open(export_file)
        image = image.crop(image.getbbox())
        width, height = image.size

        # 短い辺を100に合わせるようにリサイズ
        if width < height:
            resized_image = image.resize((int(width * 100 / height), 100))
        else:
            resized_image = image.resize((100, int(height * 100 / width)))

        # 画像をちょっと縮小　ユーザーが弄れる
        resized_image = resized_image.resize((int(resized_image.width * scale), int(resized_image.height * scale)))


       # 画像を中央に合わせて切り抜く
        left = (resized_image.width - 100) // 2 + horizontal_shift
        top = (resized_image.height - 100) // 2 + vertical_shift
        right = left + 100
        bottom = top + 100
        b_image = resized_image.crop((left, top, right, bottom))


        # 100×100保存
        b_image.save(os.path.join(OUTPUT_PATH,'b.png'))

        # 50×50保存
        b_image = b_image.resize((50, 50))
        b_image.save(os.path.join(OUTPUT_PATH,'a.png'))
        
        # 画像のプレビューを表示
        image = Image.open('output3/b.png')
        image_with_border = ImageOps.expand(image, border=1, fill='red')
        st.image(image_with_border, caption='100×100のプレビュー', use_column_width=False)

                
        ####################################

        #　640 × 640、320 ×　320　のリサイズ

        ####################################

        # 画像を読み込む
        image = Image.open(export_file)

        # 960×640保存
        image = image.resize((960, 640))
        image.save(os.path.join(OUTPUT_PATH,'e.png'))

        # 不要な透明部分削除
        image = image.crop(image.getbbox())

        image_np = np.array(image)
        alpha = image_np[:, :, 3]
        cy, cx = ndimage.center_of_mass(alpha)
        center_x = int(cx)
        center_y = int(cy)

        # 下の座標を取得
        bottom_coord = center_y + 320

        # 画像の不透明部分の最下部の座標を測定（変数image_yとする）
        image_y = np.max(np.nonzero(alpha)[0])

        width, height = image.size

        # （center_y - 50）-　image_yの値により移動
        if bottom_coord - image_y > 15:
            center_y -= (bottom_coord - image_y) - 15
        elif bottom_coord - image_y < 15:
            center_y += 15 - (bottom_coord - image_y)

        # 640×640
        left = center_x - 640 // 2
        top = center_y - 640 // 2
        right = left + 640
        bottom = top + 640
        d_image = image.crop((left, top, right, bottom))

        # 320×320
        c_image = d_image.resize((320, 320))

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
          
    # 削除実行　AI生成　
    thread = threading.Thread(target=delete_data)
    thread.start()       
    
    st.markdown(f'<span style="color:red">書き出しが完了しました。フォルダ「output3」を確認してください。</span>', unsafe_allow_html=True)
    shutil.make_archive('output3', 'zip', 'output3')
    st.download_button(label="output3.zipをダウンロード", data=open('output3.zip', 'rb'), file_name='output3.zip', mime='application/zip')
    os.remove('output3.zip')
