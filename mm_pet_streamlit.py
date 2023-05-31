import tkinter
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mbox
from tkinter import filedialog
from PIL import Image
import os
import shutil
import glob
import sys
import subprocess

# 画面作成
window = tkinter.Tk()
window.geometry('350x180')
window.title('モンコレフレームセット書き出し')

###################################################################

#個人フレーム、ギルドフレームファイル指定、ラベル

###################################################################

# 個人フレームファイルを選択
def select_file1():
    global file_selected1
    file_selected1 = filedialog.askopenfilenames()  # 複数選択に変更
    full_paths = [os.path.abspath(file) for file in file_selected1]  # 全てのファイルに対して、絶対パスを取得
    select_file_label1.config(text=str(full_paths))  # ラベルに全てのパスを表示する
    return file_selected1


# ギルドフレームファイルを選択
def select_file2():
    global file_selected2
    file_selected2 = filedialog.askopenfilenames()  # 複数選択に変更
    full_paths = [os.path.abspath(file) for file in file_selected2]  # 全てのファイルに対して、絶対パスを取得
    select_file_label2.config(text=str(full_paths))  # ラベルに全てのパスを表示する
    return file_selected2
    
# ファイルを選択するボタンを表示する
select_button1 = tk.Button(window, text='アイコンフレームを選択', command=select_file1)
select_button1.place(x=30, y=5)

select_button2 = tk.Button(window, text='ギルドフレームを選択', command=select_file2)
select_button2.place(x=30, y=55)

# 選択したファイル名を表示するラベルを作成する
select_file_label1 = tk.Label(window, text="")
select_file_label1.place(x=30, y=30)

select_file_label2 = tk.Label(window, text="")
select_file_label2.place(x=30, y=80)


#shimomatsuya: 230407 メッセージボックス追加
def export():
    file_selected1 = select_file_label1.cget("text")
    mbox.showinfo("書き出し開始", "書き出しを開始します。")
    batch_export(file_selected1)
    mbox.showinfo("書き出し完了", "書き出しが完了しました。")

###################################################################

#書き出し処理

###################################################################
def batch_export(file_selected1):
    #個人フレームのファイル
    icon_frame = file_selected1  # 選択された全てのファイルパスをリストに変換する
    #ギルドフレームのファイル
    guild_frame = file_selected2  # 選択された全てのファイルパスをリストに変換する
    
    
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
    ICON_OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'output', 'アイコンフレーム')
    GUILD_OUTPUT_PATH = os.path.join(OUTPUT_PATH, 'output', 'ギルドフレーム')
    if not os.path.exists(ICON_OUTPUT_PATH):
        os.makedirs(ICON_OUTPUT_PATH)
    if not os.path.exists(GUILD_OUTPUT_PATH):
        os.makedirs(GUILD_OUTPUT_PATH)
    mbox.showinfo("title", "以下の経路で書き出します。\n個人フレーム: " + ICON_OUTPUT_PATH + "\nギルドフレーム: " + GUILD_OUTPUT_PATH)
    
        # 個人フレーム処理　ループ一応残しておく
    for ICON in  icon_frame:
        ####################################

        #　50 × 50、100 × 100、200 × 200のリサイズ

        ####################################

        # ファイルパスの設定
        image_path = ICON

        # 画像ファイルを開く
        image = Image.open(image_path)

        # 50、100、200にリサイズして保存
        resized_50 = image.resize((50, 50))
        resized_50.save(os.path.join(ICON_OUTPUT_PATH,'a.png'))

        resized_100 = image.resize((100, 100))
        resized_100.save(os.path.join(ICON_OUTPUT_PATH,'b.png'))

        resized_200 = image.resize((200, 200))
        resized_200.save(os.path.join(ICON_OUTPUT_PATH,'c.png'))

        ####################################

        #　320 × 320、640 × 640リサイズ

        ####################################

        # 画像ファイルを開く
        image = Image.open(image_path)

        # 292×292にリサイズしておく
        image = image.resize((292, 292))

        # 空白画像を作成
        blank_image = Image.new('RGBA', (640, 640), (0, 0, 0, 0))

        # 元の画像を貼り付け
        left = (blank_image.width - image.width) // 2
        top = int((blank_image.height - image.height) * 0.8)
        blank_image.paste(image, (left, top))

        # 320リサイズと640の保存
        d_image = blank_image.resize((320, 320))
        d_image.save(os.path.join(ICON_OUTPUT_PATH,'d.png'))
        blank_image.save(os.path.join(ICON_OUTPUT_PATH,'e.png'))


        
        ####################################
        
        # 書き出しフォルダを作成,移動
        
        ####################################

        # フォルダ名を格納したリスト
        dir_names = ['50x50', '100x100','200x200','320x320', '640x640']

        # フォルダがなければ作成
        for dir_name in dir_names:
            dir_path = os.path.join(ICON_OUTPUT_PATH, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            else:
                pass
            
        # フォルダとファイルのパス
        folder_paths = ['50x50', '100x100','200x200','320x320', '640x640']
        file_paths = ['a.png', 'b.png', 'c.png', 'd.png', 'e.png']

        # ファイルを移動する
        for folder, file in zip(folder_paths, file_paths):
            source_path = os.path.join(ICON_OUTPUT_PATH, file)
            destination_path = os.path.join(ICON_OUTPUT_PATH, folder, file)
            shutil.move(source_path, destination_path)

            
        ####################################
        
        # 元ファイル名にリネーム
        
        ####################################

        # リネームするファイルとフォルダのパス
        folder_paths = ['50x50', '100x100','200x200','320x320', '640x640']
        file_names = ['a.png', 'b.png', 'c.png', 'd.png', 'e.png']

        for folder, file in zip(folder_paths, file_names):
            src = os.path.join(ICON_OUTPUT_PATH, folder, file)
            dst = os.path.join(ICON_OUTPUT_PATH, folder, os.path.basename(ICON))
            os.rename(src, dst)

            
    # ギルドフレーム処理　ループ一応残しておく
    for GUILD in guild_frame:
        ####################################

        #　50 × 50、100 × 100、224 × 552のリサイズ

        ####################################

        # ファイルパスの設定
        icon_frame = file_selected1
        guild_frame = file_selected2

        # 画像ファイルを開く
        icon_image = Image.open(icon_frame)
        guild_image = Image.open(guild_frame)

        # 個人フレームを50、100にリサイズして保存
        resized_50 = icon_image.resize((50, 50))
        resized_50.save(os.path.join(GUILD_OUTPUT_PATH,'a.png'))
        resized_100 = icon_image.resize((100, 100))
        resized_100.save(os.path.join(GUILD_OUTPUT_PATH,'b.png'))
        
        ####################################

        #　112 × 272のリサイズ

        ####################################

        # ギルドフレームを112 × 272リサイズして保存
        resized_112 = guild_image.resize((112, 272))
        resized_112.save(os.path.join(GUILD_OUTPUT_PATH,'c.png'))
        
        ####################################

        #　320 × 320、640 × 640リサイズ

        ####################################



        # 空白画像を作成
        resized_640 = Image.new('RGBA', (640, 640), (0, 0, 0, 0))

        # 元の画像を貼り付け
        left = (blank_image.width - image.width) // 2
        top = int((blank_image.height - image.height) * 0.8)
        resized_640.paste(image, (left, top))

        # 320と640の保存
        resized_320 = resized_640.resize((320, 320))
        resized_320.save(os.path.join(GUILD_OUTPUT_PATH,'d.png'))
        resized_640.save(os.path.join(GUILD_OUTPUT_PATH,'e.png'))
        

        ####################################
        
        # 書き出しフォルダを作成,移動
        
        ####################################

        # フォルダ名を格納したリスト
        dir_names = ['50x50', '100x100','112x272', '320x320','640x640']
        
        # フォルダがなければ作成
        for dir_name in dir_names:
            dir_path = os.path.join(GUILD_OUTPUT_PATH, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            else:
                pass
            
        # フォルダとファイルのパス
        folder_paths =  ['50x50', '100x100','112x272', '320x320','640x640']
        file_paths = ['a.png', 'b.png', 'c.png','d.png', 'e.png']

        # ファイルを移動する
        for folder, file in zip(folder_paths, file_paths):
            source_path = os.path.join(GUILD_OUTPUT_PATH , file)
            destination_path = os.path.join(GUILD_OUTPUT_PATH , folder, file)
            shutil.move(source_path, destination_path)

            
        ####################################
        
        # 元ファイル名にリネーム
        
        ####################################

        # リネームするファイルとフォルダのパス
        folder_paths = ['50x50', '100x100','112x272', '320x320','640x640']
        file_names = ['a.png', 'b.png', 'c.png','d.png', 'e.png']

        for folder, file in zip(folder_paths, file_names):
            src = os.path.join(GUILD_OUTPUT_PATH , folder, file)
            dst = os.path.join(GUILD_OUTPUT_PATH , folder, os.path.basename(GUILD))
            os.rename(src, dst)
            
# ボタン作成
button1 = tk.Button(window, text='フレーム一括書き出し', command=export)
button1.place(x=30, y=125)

# 画面表示（常駐）
window.mainloop()
