import os.path as osp
import tkinter.filedialog as tkf
import chardet
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import opencc

class param():
    title = 'OpenCC v1.1.6 GUI'
    win_width, win_height = 430, 500
    color_theme = 'blue'
    app_mode = 'dark'
    fonts = ('Microsoft JhengHei UI', 13)
    rad_fonts = ('Microsoft JhengHei UI', 13)
    # gui_icon = 'conv.ico'
    fpath = []
    trans_json = ''
    fformat = (('All','*.*'), ('Text-based', '*.txt;*.csv;*.html;*.json;*.xml;*.cfg;*.ini;*.md;*.log;*.yaml'),
               ('Subtitle','*.srt;*.ass;*.sub;*.vtt;*.lrc'))
    
    class radlist():
        src_title = '原有語言'
        src_lang = ['簡體','繁體','臺灣繁體','香港繁體','日本漢字 (Kanji)']
        dest_title = '目標語言'
        dest_lang = src_lang + ['簡體 (中國大陸常用詞彙)', '繁體 (臺灣常用詞彙)']
        lang_sym = ['s', 't', 'tw', 'hk', 'jp', 'sp', 'twp']
    class lang_comb():  # [src_lang], [target_lang]        
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
    def __init__(self, master, title, radioTitle, font, ini_state):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = radioTitle
        self.title = title
        self.fonts = font
        self.status = ini_state
        self.radiobuttons = []
        self.variable = ctk.StringVar(value="")
        self.btndict = {}
        
        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6, font=self.fonts)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='nsew')
        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(self, text=value, value=param.radlist.lang_sym[i], variable=self.variable, font=self.fonts, command=self.rad_action, state=self.status)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)
            self.btndict[param.radlist.lang_sym[i]] = radiobutton
            
    def get(self):
        return self.variable.get()
    def set(self, value):
        self.variable.set(value)
    
    def rad_action(self):
        rad_list_side = 0 if self.title.cget('text')=='原有語言' else 1
        ava_opts = getattr(param.lang_comb, self.get())[rad_list_side]
        self.master.off_radbtn(rad_list_side, ava_opts)
             
class openCCgui(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_default_color_theme(param.color_theme)
        ctk.set_appearance_mode(param.app_mode)
        self.title(param.title)
        # self.iconbitmap(param.gui_icon)
        self.geometry(f'{param.win_width}x{param.win_height}')
        self.resizable(False, False)
        self.grid_columnconfigure((0,1), weight=1, minsize=200)
        self.grid_rowconfigure((0,1,2,3), weight=1)
        
        self.radio_srcf = radBtn_frame(self, title=param.radlist.src_title, radioTitle=param.radlist.src_lang, font=param.rad_fonts, ini_state='normal')
        self.radio_srcf.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky='nsew')
        self.radio_desf = radBtn_frame(self, title=param.radlist.dest_title, radioTitle=param.radlist.dest_lang, font=param.rad_fonts, ini_state='disabled')
        self.radio_desf.grid(row=0, column=1, padx=(10,10), pady=(10,10), sticky='nsew')
        
        self._isLocalFileVar = ctk.IntVar(value=1)
        self.selfile_radio = ctk.CTkRadioButton(self, text='目標檔案：', font=param.fonts, value=1, variable=self._isLocalFileVar, command=self.switch_srcRadbtn)
        self.selfile_radio.grid(row=1, column=0, padx=(40,10), pady=(10,10), sticky='e')
        self.txtbox_radio = ctk.CTkRadioButton(self, text='目標文本：', font=param.fonts, value=0, variable=self._isLocalFileVar, command=self.switch_srcRadbtn)
        self.txtbox_radio.grid(row=2, column=0, padx=(40,10), pady=(10,10), sticky='e')

        self.selbtn = ctk.CTkButton(self, text='選擇檔案', command=self.file_select, font=param.fonts)
        self.selbtn.grid(row=1, column=1, padx=(40,25), pady=(0,0), sticky='w')
        
        self.txtbox = ctk.CTkTextbox(self, height=120, width=220, font=param.fonts, state='disabled')
        self.txtbox.grid(row=2, column=1, padx=(0,10), pady=(0,0), sticky='w')
        
        self.covbtn = ctk.CTkButton(self, text='開始轉換', command=self.submit, font=param.fonts)
        self.covbtn.grid(row=3, column=0, padx=(100,100), pady=(10,10), sticky='ew', columnspan=2)
        
        self.mainloop()
    
    def off_radbtn(self, side, opt_list):
        not_ava_set = set(param.radlist.lang_sym) - set(opt_list)
        on_deslang = self.radio_desf.get()
        if side == 0:   # src lang
            for opt in opt_list:
                self.radio_desf.btndict[f'{opt}'].configure(state='normal')
            for nopt in not_ava_set:
                self.radio_desf.btndict[f'{nopt}'].configure(state='disabled')
            if on_deslang != '':
                self.radio_desf.btndict[f'{on_deslang}'].deselect()
    
    def switch_srcRadbtn(self):
        if self._isLocalFileVar.get():
            self.txtbox.delete('1.0', ctk.END)
            self.txtbox.configure(state='disabled')
            self.selbtn.configure(state='normal')
        else:
            self.selbtn.configure(state='disabled', text='選擇檔案')
            self.txtbox.configure(state='normal')
    
    def chk_selection(self, json_name):
        if json_name not in param.lang_comb.name:
            msgBox.show_error('錯誤', '請選擇語言')
            return None
        if (len(param.fpath) == 0 and self._isLocalFileVar.get()):
            msgBox.show_error('錯誤', '請選擇檔案')
            return None
        if (not self._isLocalFileVar.get() and len(self.txtbox.get('1.0', ctk.END)) < 2):
            msgBox.show_error('錯誤', '請輸入文字')
            return None
        return json_name + '.json'
        
    def submit(self):
        param.trans_json = self.chk_selection(f'{self.radio_srcf.get()}2{self.radio_desf.get()}')
        if(param.trans_json != None):
            try:
                if self._isLocalFileVar.get():
                    opencc_converter.file_converter(param.fpath, param.trans_json)
                else:
                    outtext = opencc_converter.text_converter(self.txtbox.get('1.0', ctk.END), param.trans_json)
                    self.txtbox.delete('1.0', ctk.END)
                    self.txtbox.insert(ctk.END, outtext)
            except:
                msgBox.show_error('錯誤', '檔案轉換錯誤')
                
    def file_select(self):
        param.fpath = tkf.askopenfilenames(title='請選擇檔案', filetypes=param.fformat)
        f_no = len(param.fpath)
        self.selbtn.configure(text=f'已選擇檔案：{f_no}')
                
class opencc_converter:
    def file_converter(src_files, lang_json):       
        conv = opencc.OpenCC(lang_json)
        for file in src_files:
            out_name = osp.splitext(file)[0] + '_converted' + osp.splitext(file)[1]
            with open(file, 'rb') as fin, open(out_name, 'w', encoding='utf-8') as fout:
                content = fin.read()
                dectecting = chardet.detect(content)
                decoded_text = content.decode(dectecting['encoding'])
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
