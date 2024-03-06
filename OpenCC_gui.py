import os, chardet, opencc, sys
import tkinter.filedialog as tkf
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image

class param():
    main_title = 'OpenCC v1.1.7 GUI'
    win_width, win_height = 430, 485
    color_theme = 'blue'
    app_mode = 'dark'
    fonts = ('Microsoft JhengHei UI', 13, 'bold')
    rad_fonts = ('Microsoft JhengHei UI', 13, 'bold')
    gui_icon = 'assets/favicon.ico'
    file_paths = []
    translation_json = ''
    file_formats = (('All','*.*'), ('Text-based', '*.txt;*.csv;*.html;*.json;*.xml;*.cfg;*.ini;*.md;*.log;*.yaml'),
               ('Subtitle','*.srt;*.ass;*.sub;*.vtt;*.lrc'))
    
    class radlist():
        src_title = '原有語言'
        src_lang = ['簡體','繁體','臺灣繁體','香港繁體','日本漢字 (Kanji)', '繁體 (古籍印刷通用字)']
        dest_title = '目標語言'
        dest_lang = src_lang + ['簡體 (中國大陸常用詞彙)', '繁體 (臺灣常用詞彙)']
        lang_abbrev = ['s', 't', 'tw', 'hk', 'jp', 'g', 'sp', 'twp']
    class lang_combination():  # [src_lang]      
        s = ['t','tw','hk','g','twp']
        t = ['s','tw','hk','jp']
        tw = ['s','t','sp']
        hk = ['s','t']
        jp = ['t']
        sp = []
        twp = []
        g = ['s']
        name = ['s2t','t2s','s2tw','tw2s','s2hk','hk2s',
                's2twp','tw2sp','t2tw','hk2t','t2hk','t2jp','jp2t','tw2t', 's2g', 'g2s']
        
class msgBox():
    def show_error(win_title, msg):
        CTkMessagebox(width=300, height=150, title=win_title, message=msg, icon='cancel', font=param.fonts)
    def completion(win_title, msg):
        CTkMessagebox(width=300, height=150, title=win_title, message=msg, icon='check', font=param.fonts)

class radBtn_frame(ctk.CTkFrame):
    def __init__(self, master, title, radioTitle, font, init_state):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = radioTitle
        self.title = title
        self.fonts = font
        self.status = init_state
        self.radiobuttons = []
        self.variable = ctk.StringVar(value="")
        self.radBtnDICT = {}
        
        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6, font=self.fonts)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='nsew')
        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(self, text=value, value=param.radlist.lang_abbrev[i], variable=self.variable, font=self.fonts, command=self.rad_action, state=self.status)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)
            self.radBtnDICT[param.radlist.lang_abbrev[i]] = radiobutton
        pass
            
    def get(self):
        return self.variable.get()
    def set(self, value):
        self.variable.set(value)
    
    def rad_action(self):
        _is_choosing_destlang_ = False if self.title._text == '原有語言' else True
        if not _is_choosing_destlang_:
            ava_options = getattr(param.lang_combination, self.get())
            self.master.switch_radBtn(ava_options)
  
class text_convert_popup():
    def __init__(self, master, srctext):
        self.master_win = master
        self.new_win = ctk.CTkToplevel()
        self.new_win.title('純文字轉換') 
        self.new_win.after(300, lambda: self.new_win.iconbitmap(resource_path(param.gui_icon)))
        self.new_win.resizable(False, False)               
        self.new_win.geometry('780x450')
        self.new_win.grid_columnconfigure(0, weight=5)
        self.new_win.grid_columnconfigure(1, weight=1)
        self.new_win.grid_columnconfigure(2, weight=5)
        self.new_win.grid_rowconfigure(0, weight=1)
        self.converted_str = opencc_converter.text_converter(srctext, param.translation_json)
        
        self.original_str_textbox = ctk.CTkTextbox(self.new_win, width=360, height=390, font=param.fonts, state='normal')
        self.original_str_textbox.grid(row=0, column=0, padx=(10,5), pady=(10,10), sticky='nsew')
        self.original_str_textbox.bind("<KeyRelease>", self.update_result)
        
        arrow_image = ctk.CTkImage(dark_image=Image.open(resource_path("assets/right_arrow.png")), size=(20,20))
        arrow_icon = ctk.CTkLabel(self.new_win, image=arrow_image, text='')
        arrow_icon.grid(row=0, column=1)
        
        self.printout = ctk.CTkTextbox(self.new_win, width=360, height=390, font=param.fonts, state='normal')
        self.printout.insert('1.0', text=self.converted_str)
        self.printout.configure(state='disabled')
        self.printout.grid(row=0, column=2, padx=(5,10), pady=(10,10), sticky='nsew')
        
        self.copyBtn = ctk.CTkButton(self.new_win, text='複製', command=self.copy_text, font=param.fonts)
        self.copyBtn.grid(row=1, column=0, columnspan=3, padx=(10,10) , pady=(10,10))
        
    def copy_text(self):
        self.new_win.clipboard_clear()
        self.new_win.clipboard_append(self.printout.get('1.0', ctk.END))
        self.master_win.result_window.new_win.destroy()
        
    def update_result(self, _):
        self.printout.configure(state='normal')
        self.printout.delete('1.0', ctk.END)
        inserted_string = self.original_str_textbox.get('1.0', ctk.END)
        converted_string = opencc_converter.text_converter(inserted_string, param.translation_json)
        self.printout.insert(ctk.END, converted_string)
        self.printout.configure(state='disabled')
        
                  
class openCCgui(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme(param.color_theme)
        ctk.set_appearance_mode(param.app_mode)
        self.title(param.main_title)
        self.iconbitmap(resource_path(param.gui_icon))
        self.geometry(f'{param.win_width}x{param.win_height}')
        self.resizable(False, False)
        self.grid_columnconfigure((0,1), weight=1, minsize=200)
        self.grid_rowconfigure((0,1,2,3), weight=1)
        
        self.srclang_radframe = radBtn_frame(self, title=param.radlist.src_title, radioTitle=param.radlist.src_lang, font=param.rad_fonts, init_state='normal')
        self.srclang_radframe.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky='nsew')
        self.destlang_radframe = radBtn_frame(self, title=param.radlist.dest_title, radioTitle=param.radlist.dest_lang, font=param.rad_fonts, init_state='disabled')
        self.destlang_radframe.grid(row=0, column=1, padx=(10,10), pady=(10,10), sticky='nsew')
        
        self._is_convert_from_file_ = ctk.IntVar(value=1)
        self.fileSelection_radBtn = ctk.CTkRadioButton(self, text='目標檔案：', font=param.fonts, value=1, variable=self._is_convert_from_file_, command=self.switch_srcRadbtn)
        self.fileSelection_radBtn.grid(row=1, column=0, padx=(40,10), pady=(10,10), sticky='e')
        self.textbox_radBtn = ctk.CTkRadioButton(self, text='純文字轉換', font=param.fonts, value=0, variable=self._is_convert_from_file_, command=self.switch_srcRadbtn)
        self.textbox_radBtn.grid(row=2, column=0, padx=(0,0), pady=(10,10), columnspan=2, sticky='ns')

        self.fileSelectBtn = ctk.CTkButton(self, text='選擇檔案', command=self.file_select, font=param.fonts)
        self.fileSelectBtn.grid(row=1, column=1, padx=(40,25), pady=(0,0), sticky='w')
        
        self.convertBtn = ctk.CTkButton(self, text='開始轉換', command=self.submit, font=param.fonts)
        self.convertBtn.grid(row=3, column=0, padx=(100,100), pady=(10,20), sticky='ew', columnspan=2)
        self.result_window = None
        
        self.mainloop()
    
    def switch_radBtn(self, opt_list):
        invalid_lang_set = set(param.radlist.lang_abbrev) - set(opt_list)
        selected_destlang = self.destlang_radframe.get()
        for opt in opt_list:
            self.destlang_radframe.radBtnDICT[f'{opt}'].configure(state='normal')
        for nopt in invalid_lang_set:
            self.destlang_radframe.radBtnDICT[f'{nopt}'].configure(state='disabled')
        if selected_destlang != '':
            self.destlang_radframe.radBtnDICT[f'{selected_destlang}'].deselect()
    
    def switch_srcRadbtn(self):
        if self._is_convert_from_file_.get():
            self.fileSelectBtn.configure(state='normal')
        else:
            self.fileSelectBtn.configure(state='disabled', text='選擇檔案')
    
    def chk_selection(self, json_name):
        if json_name not in param.lang_combination.name:
            msgBox.show_error('錯誤', '請選擇語言')
            return None
        if (len(param.file_paths) == 0 and self._is_convert_from_file_.get()):
            msgBox.show_error('錯誤', '請選擇檔案')
            return None
        return json_name + '.json'
        
    def submit(self):
        target_language_abbrev = self.destlang_radframe.get()
        if target_language_abbrev:
            target_language_suffix = param.radlist.dest_lang[param.radlist.lang_abbrev.index(target_language_abbrev)]
        param.translation_json = self.chk_selection(f'{self.srclang_radframe.get()}2{target_language_abbrev}')
        if(param.translation_json != None):
            try:
                if self._is_convert_from_file_.get():
                    opencc_converter.file_converter(param.file_paths, param.translation_json, target_language_suffix)
                else:
                    if self.result_window is not None and self.result_window.new_win.winfo_exists():
                        self.result_window.new_win.destroy()
                    self.result_window = text_convert_popup(self, '')   
            except Exception as err:
                msgBox.show_error('錯誤', str(err))
                
    def file_select(self):
        param.file_paths = tkf.askopenfilenames(title='請選擇檔案', filetypes=param.file_formats)
        file_count = len(param.file_paths)
        self.fileSelectBtn.configure(text=f'已選擇檔案：{file_count}')
                
class opencc_converter:
    def file_converter(src_files, lang_json, file_suffix):       
        conv = opencc.OpenCC(lang_json)
        for file in src_files:
            target = os.path.splitext(os.path.basename(file))
            output_filename = conv.convert(target[0]) + f'_{file_suffix}{target[1]}'
            output_filename =  os.path.join(os.path.dirname(file), output_filename)
            with open(file, 'rb') as fin, open(output_filename, 'w', encoding='UTF-8') as fout:
                content = fin.read()
                dectecting = chardet.detect(content)['encoding']
                encoding_type = 'GB18030' if (dectecting == 'GB2312' or dectecting == 'GBK') else dectecting
                decoded_text = content.decode(encoding_type, errors='replace')
                for line in decoded_text.splitlines():
                    fout.write(conv.convert(line) + '\n')
        msgBox.completion('通知', '已完成轉換所有檔案') 
        
    def text_converter(src_text, lang_json):
        conv = opencc.OpenCC(lang_json)
        result_text = ''
        for line in src_text.splitlines():
            result_text = result_text + conv.convert(line) + '\n'
        while result_text.endswith('\n'):
            result_text = result_text[:-1]
        return result_text
    
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    
if __name__ == '__main__':
    main_GUI = openCCgui()