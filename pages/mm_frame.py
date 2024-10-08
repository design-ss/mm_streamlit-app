import streamlit as st
import numpy as np
from scipy import ndimage
import zipfile
import io
from PIL import Image, ImageOps, ImageDraw
import time
import base64

binary_dict = dict()


def show_zip_download(file_name, target_dict):
    # st.write(target_dict)
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as zip:
            for key in target_dict.keys():
                image = target_dict[key]
                img_buffer = io.BytesIO()
                image.save(img_buffer, "PNG")
                zip.writestr(key, img_buffer.getvalue())
        buffer.seek(0)
        st.download_button(label=file_name + "をダウンロード", data=buffer, file_name=file_name, mime='application/zip')

st.set_page_config(page_title='mmフレーム書き出し')

st.title('mmフレーム書き出し')
st.write('**ID付与前に「複数枚同時に」書き出す場合はお気をつけください。** <p style="font-size: 80%;">ファイルは選択順に関係なく「名前の昇順」でアップされます。<br> そのため、適切にフレームを組み合わせるために、ファイル名の先頭に3桁の数字を付けるなどで順番を制御してください。<br>（例）<br>アイコンフレーム：「001.男_アイコンフレーム」「002.女_アイコンフレーム」<br>ギルドフレーム：「003.男_ギルドフレーム」「004.女_ギルドフレーム」<br> とそれぞれ対応するフレームの順番が正しくなるように数字を付けてください。</p>', unsafe_allow_html=True)
st.write('<span style="color:red;">※未圧縮データを使ってください！</span>', unsafe_allow_html=True)
# アイコンフレームファイル指定
export_files_iconframe = st.file_uploader("アイコンフレームファイルを選択", type='png', accept_multiple_files=True, key="export_files_iconframe")

# ギルドフレームファイル指定
export_files_guildframe = st.file_uploader("ギルドフレームファイルを選択", type='png', accept_multiple_files=True, key="export_files_guildframe")

# ファイル名を昇順に並び替える
export_files_iconframe = sorted(export_files_iconframe, key=lambda x: x.name)
export_files_guildframe = sorted(export_files_guildframe, key=lambda x: x.name)


# 一括書き出しと個別書き出し
export_button1, export_selected_button1 = st.columns(2)

# 一括書き出し
with export_button1:
    if st.button('一括書き出し'):
        with st.spinner("画像生成中です..."):
            binary_dict.clear() # 初期化
            
            for ICON in export_files_iconframe:
                ####################################

                #　50 × 50、100 × 100、200 × 200のリサイズ

                ####################################
                # 画像ファイルを開く
                image = Image.open(ICON)

                # 50、100、200にリサイズして保存
                resized_50 = image.resize((50, 50))
                resized_100 = image.resize((100, 100))
                resized_200 = image.resize((200, 200))
                
                # 50 × 50保存
                binary_dict["/frame/icon_frame/50x50/" + ICON.name] = resized_50

                # 100 × 100保存
                binary_dict["/frame/icon_frame/100x100/" + ICON.name] = resized_100

                # 200 × 200保存
                binary_dict["/frame/icon_frame/200x200/" + ICON.name] = resized_200


                ####################################

                #　640 × 640、320 ×　320　のリサイズ

                ####################################


                image = image.resize((300, 300))
                blank_image = Image.new('RGBA', (640, 640), (0, 0, 0, 0))

                # 元画像
                left = (blank_image.width - image.width) // 2
                top = int((blank_image.height - image.height) * 0.8)
                blank_image.paste(image, (left, top))
                resized_640 = blank_image
              
                resized_320 = blank_image.resize((320, 320))

                binary_dict["/frame/icon_frame/320x320/" + ICON.name] = resized_320
                binary_dict["/frame/icon_frame/640x640/" + ICON.name] = resized_640
                
            # ギルドフレーム処理　ループ一応残しておく
            for ICON, GUILD in zip(export_files_iconframe, export_files_guildframe):
                ####################################

                #　50 × 50、100 × 100

                ####################################

                # 画像ファイルを開く
                icon_image = Image.open(ICON)
                guild_image = Image.open(GUILD)

                # アイコンフレームを50、100にリサイズして保存
                resized_50 = icon_image.resize((50, 50))
                binary_dict["/frame/guild_frame/50x50/" + GUILD.name] = resized_50
                resized_100 = icon_image.resize((100, 100))
                binary_dict["/frame/guild_frame/100x100/" + GUILD.name] = resized_100
                
                ####################################

                #　640 × 640、320 ×　320　のリサイズ 、224 × 552のリサイズもついでに

                ####################################
                # ちょっとミスったのでいつか直す
                icon_image = image
                image = image.resize((300, 300))
                blank_image = Image.new('RGBA', (640, 640), (0, 0, 0, 0))

                # 元画像
                left = (blank_image.width - image.width) // 2
                top = int((blank_image.height - image.height) * 0.8)
                blank_image.paste(image, (left, top))
                resized_640 = blank_image
              
                resized_320 = blank_image.resize((320, 320))

                binary_dict["/frame/guild_frame/320x320/" + GUILD.name] = resized_320
                binary_dict["/frame/guild_frame/640x640/" + GUILD.name] = resized_640
                
                # ギルドフレームを保存
                resized_224 = guild_image.resize((224, 552))
                binary_dict["/frame/guild_frame/224x552/" + GUILD.name] = resized_224
                    
            time.sleep(3)
        st.markdown(f'<span style="color:red">書き出しが完了しました。ダウンロードボタンが表示されるまでお待ちください。</span>', unsafe_allow_html=True)
        show_zip_download("mm_frame.zip", binary_dict)
st.markdown('---')


