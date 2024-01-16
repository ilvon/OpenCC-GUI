import os, chardet, opencc
import tkinter.filedialog as tkf
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

class param():
    main_title = 'OpenCC v1.1.7 GUI'
    win_width, win_height = 430, 500
    color_theme = 'blue'
    app_mode = 'dark'
    fonts = ('Microsoft JhengHei UI', 13)
    rad_fonts = ('Microsoft JhengHei UI', 13)
    # gui_icon = 'conv.ico'
    file_paths = []
    translation_json = ''
    file_formats = (('All','*.*'), ('Text-based', '*.txt;*.csv;*.html;*.json;*.xml;*.cfg;*.ini;*.md;*.log;*.yaml'),
               ('Subtitle','*.srt;*.ass;*.sub;*.vtt;*.lrc'))
    
    class radlist():
        src_title = '原有語言'
        src_lang = ['簡體','繁體','臺灣繁體','香港繁體','日本漢字 (Kanji)']
        dest_title = '目標語言'
        dest_lang = src_lang + ['簡體 (中國大陸常用詞彙)', '繁體 (臺灣常用詞彙)']
        lang_abbrev = ['s', 't', 'tw', 'hk', 'jp', 'sp', 'twp']
    class lang_combination():  # [src_lang], [target_lang]        
        s = [['t','tw','hk','twp'], ['t','tw','hk']]
        t = [['s','tw','hk','jp'], ['s','tw','hk','jp']]
        tw = [['s','t','sp'], ['s','t']]
        hk = [['s','t'], ['s','t']]
        jp = [['t'], ['t']]
        sp = [[], ['tw']]
        twp = [[], ['s']]
        name = ['s2t','t2s','s2tw','tw2s','s2hk','hk2s',
                's2twp','tw2sp','t2tw','hk2t','t2hk','t2jp','jp2t','tw2t']
        
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
        ava_options = getattr(param.lang_combination, self.get())[int(_is_choosing_destlang_)]
        self.master.switch_radBtn(_is_choosing_destlang_, ava_options) # do nothing if clicking destlang_radBtn
             
class openCCgui(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme(param.color_theme)
        ctk.set_appearance_mode(param.app_mode)
        self.title(param.main_title)
        # self.iconbitmap(param.gui_icon)
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
        self.textbox_radBtn = ctk.CTkRadioButton(self, text='目標文本：', font=param.fonts, value=0, variable=self._is_convert_from_file_, command=self.switch_srcRadbtn)
        self.textbox_radBtn.grid(row=2, column=0, padx=(40,10), pady=(10,10), sticky='e')

        self.fileSelectBtn = ctk.CTkButton(self, text='選擇檔案', command=self.file_select, font=param.fonts)
        self.fileSelectBtn.grid(row=1, column=1, padx=(40,25), pady=(0,0), sticky='w')
        
        self.textbox = ctk.CTkTextbox(self, height=120, width=220, font=param.fonts, state='disabled')
        self.textbox.grid(row=2, column=1, padx=(0,10), pady=(0,0), sticky='w')
        
        self.convertBtn = ctk.CTkButton(self, text='開始轉換', command=self.submit, font=param.fonts)
        self.convertBtn.grid(row=3, column=0, padx=(100,100), pady=(10,10), sticky='ew', columnspan=2)
        
        self.mainloop()
    
    def switch_radBtn(self, selecting_destlang, opt_list):
        if selecting_destlang == False:
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
            self.textbox.delete('1.0', ctk.END)
            self.textbox.configure(state='disabled')
            self.fileSelectBtn.configure(state='normal')
        else:
            self.fileSelectBtn.configure(state='disabled', text='選擇檔案')
            self.textbox.configure(state='normal')
    
    def chk_selection(self, json_name):
        if json_name not in param.lang_combination.name:
            msgBox.show_error('錯誤', '請選擇語言')
            return None
        if (len(param.file_paths) == 0 and self._is_convert_from_file_.get()):
            msgBox.show_error('錯誤', '請選擇檔案')
            return None
        if (not self._is_convert_from_file_.get() and len(self.textbox.get('1.0', ctk.END)) < 2):
            msgBox.show_error('錯誤', '請輸入文字')
            return None
        return json_name + '.json'
        
    def submit(self):
        param.translation_json = self.chk_selection(f'{self.srclang_radframe.get()}2{self.destlang_radframe.get()}')
        if(param.translation_json != None):
            try:
                if self._is_convert_from_file_.get():
                    opencc_converter.file_converter(param.file_paths, param.translation_json)
                else:
                    outtext = opencc_converter.text_converter(self.textbox.get('1.0', ctk.END), param.translation_json)
                    self.textbox.delete('1.0', ctk.END)
                    self.textbox.insert(ctk.END, outtext)
                    self.clipboard_clear()
                    self.clipboard_append(outtext)
            except:
                msgBox.show_error('錯誤', '檔案轉換錯誤')
                
    def file_select(self):
        param.file_paths = tkf.askopenfilenames(title='請選擇檔案', filetypes=param.file_formats)
        file_count = len(param.file_paths)
        self.fileSelectBtn.configure(text=f'已選擇檔案：{file_count}')
                
class opencc_converter:
    def file_converter(src_files, lang_json):       
        conv = opencc.OpenCC(lang_json)
        for file in src_files:
            target = os.path.splitext(os.path.basename(file))
            output_filename = conv.convert(target[0]) + '_converted' + target[1]
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
        msgBox.completion('通知', '已完成轉換')
        return result_text
    
if __name__ == '__main__':
    main_GUI = openCCgui()