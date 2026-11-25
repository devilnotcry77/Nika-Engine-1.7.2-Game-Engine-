#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, shutil, tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox, simpledialog

DEFAULT = {"title":"Новая новелла","start_scene":"scene_1","scenes":[
 {"id":"scene_1","name":"Первая сцена","background":"","entries":[
  {"type":"dialogue","speaker":"Рассказчик","text":"Добро пожаловать в NovelForge!","portrait":""},
  {"type":"dialogue","speaker":"Героиня","text":"Здесь начинается ваша история.","portrait":""}]}]}
BG="#171923"; PANEL="#242938"; ACC="#8172f5"; FG="#f0f1f7"

class Editor:
 def __init__(self, root):
  self.root=root; root.title("NovelForge — редактор визуальных новелл"); root.geometry("1250x780"); root.minsize(950,600); root.configure(bg=BG)
  self.data=json.loads(json.dumps(DEFAULT)); self.folder=None; self.si=0; self.ei=None; self.photo=None
  st=ttk.Style(); st.theme_use("clam")
  st.configure(".",font=("Segoe UI",10)); st.configure("TFrame",background=BG); st.configure("P.TFrame",background=PANEL)
  st.configure("TLabel",background=BG,foreground=FG); st.configure("P.TLabel",background=PANEL,foreground=FG)
  st.configure("TButton",background="#353c50",foreground=FG,padding=7,borderwidth=0)
  st.map("TButton",background=[("active","#4a526b")])
  st.configure("Treeview",background=PANEL,fieldbackground=PANEL,foreground=FG,rowheight=28)
  st.configure("Treeview.Heading",background="#343b50",foreground=FG)
  st.map("Treeview",background=[("selected","#51478c")])
  top=ttk.Frame(root,padding=12); top.pack(fill="x")
  ttk.Label(top,text="NikaEngine",font=("Segoe UI",18,"bold")).pack(side="left")
  for label,fn in [("Новый",self.new),("Открыть",self.open),("Сохранить",self.save),("▶ Играть",self.play)]:
   ttk.Button(top,text=label,command=fn).pack(side="right",padx=3)
  body=ttk.Frame(root,padding=10); body.pack(fill="both",expand=True)
  left=ttk.Frame(body,style="P.TFrame",padding=10,width=220); left.pack(side="left",fill="y"); left.pack_propagate(False)
  ttk.Label(left,text="СЦЕНЫ",style="P.TLabel").pack(anchor="w",pady=5)
  self.scenes=ttk.Treeview(left,show="tree"); self.scenes.pack(fill="both",expand=True); self.scenes.bind("<<TreeviewSelect>>",self.pick_scene)
  ttk.Button(left,text="+ Добавить сцену",command=self.add_scene).pack(fill="x",pady=5)
  ttk.Button(left,text="− Удалить сцену",command=self.del_scene).pack(fill="x")
  ttk.Button(left,text="Выбрать фон…",command=self.background).pack(fill="x",pady=(15,3))
  self.bglabel=ttk.Label(left,text="Фон не выбран",style="P.TLabel",wraplength=190); self.bglabel.pack(anchor="w")
  mid=ttk.Frame(body,style="P.TFrame",padding=10); mid.pack(side="left",fill="both",expand=True,padx=10)
  ttk.Label(mid,text="СЦЕНАРИЙ",style="P.TLabel",font=("Segoe UI",11,"bold")).pack(anchor="w")
  self.rows=ttk.Treeview(mid,columns=("type","speaker","text"),show="headings")
  for c,t,w in [("type","Тип",90),("speaker","Персонаж",130),("text","Текст",450)]:
   self.rows.heading(c,text=t); self.rows.column(c,width=w,stretch=(c=="text"))
  self.rows.pack(fill="both",expand=True,pady=8); self.rows.bind("<<TreeviewSelect>>",self.pick_entry)
  bar=ttk.Frame(mid,style="P.TFrame"); bar.pack(fill="x")
  for label,fn in [("+ Реплика",self.add_line),("+ Выбор",self.add_choice),("↑",lambda:self.move(-1)),("↓",lambda:self.move(1)),("Удалить",self.del_entry)]:
   ttk.Button(bar,text=label,command=fn).pack(side="left",padx=2)
  right=ttk.Frame(body,style="P.TFrame",padding=12,width=280); right.pack(side="right",fill="y"); right.pack_propagate(False)
  ttk.Label(right,text="СВОЙСТВА",style="P.TLabel",font=("Segoe UI",11,"bold")).pack(anchor="w",pady=(0,10))
  ttk.Label(right,text="Тип элемента",style="P.TLabel").pack(anchor="w")
  self.kind=tk.StringVar(value="Реплика"); ttk.Combobox(right,textvariable=self.kind,values=["Реплика","Выбор"],state="readonly").pack(fill="x",pady=4)
  ttk.Label(right,text="Персонаж / имя",style="P.TLabel").pack(anchor="w",pady=(7,0))
  self.speaker=tk.StringVar(); ttk.Entry(right,textvariable=self.speaker).pack(fill="x",pady=4)
  ttk.Label(right,text="Текст реплики / вопроса",style="P.TLabel").pack(anchor="w",pady=(7,0))
  self.text=tk.Text(right,height=7,bg="#11141e",fg=FG,insertbackground="white",relief="flat",wrap="word"); self.text.pack(fill="x",pady=4)
  ttk.Label(right,text="Варианты выбора (строка: Текст | ID сцены)",style="P.TLabel",wraplength=250).pack(anchor="w",pady=(7,0))
  self.choices=tk.Text(right,height=6,bg="#11141e",fg=FG,insertbackground="white",relief="flat",wrap="word"); self.choices.pack(fill="x",pady=4)
  ttk.Label(right,text="Портрет (путь в проекте)",style="P.TLabel").pack(anchor="w",pady=(7,0))
  self.portrait=tk.StringVar(); ttk.Entry(right,textvariable=self.portrait).pack(fill="x",pady=4)
  ttk.Button(right,text="Импортировать портрет…",command=self.pick_portrait).pack(fill="x")
  ttk.Button(right,text="Применить изменения",command=self.apply).pack(fill="x",pady=12)
  self.status=tk.StringVar(value="Готово"); ttk.Label(root,textvariable=self.status,background="#10121a",foreground="#aeb5c7",padding=7).pack(fill="x",side="bottom")
  self.refresh()

 def scene(self): return self.data["scenes"][self.si]
 def refresh(self):
  self.scenes.delete(*self.scenes.get_children())
  for i,s in enumerate(self.data["scenes"]): self.scenes.insert("","end",iid=str(i),text=s["name"])
  if self.data["scenes"]:
   self.scenes.selection_set(str(self.si)); self.refresh_rows()
 def refresh_rows(self):
  self.rows.delete(*self.rows.get_children()); self.ei=None
  for i,e in enumerate(self.scene()["entries"]):
   typ="Реплика" if e["type"]=="dialogue" else "Выбор"
   self.rows.insert("","end",iid=str(i),values=(typ,e.get("speaker","Игрок"),e.get("text","")[:100]))
  self.clear_editor(); self.bglabel.config(text="Фон: "+(self.scene().get("background") or "не выбран"))
 def clear_editor(self):
  self.speaker.set(""); self.text.delete("1.0","end"); self.choices.delete("1.0","end"); self.portrait.set(""); self.kind.set("Реплика")
 def pick_scene(self,_=None):
  sel=self.scenes.selection()
  if sel: self.si=int(sel[0]); self.refresh_rows()
 def pick_entry(self,_=None):
  sel=self.rows.selection()
  if not sel:return
  self.ei=int(sel[0]); e=self.scene()["entries"][self.ei]
  self.kind.set("Реплика" if e["type"]=="dialogue" else "Выбор")
  self.speaker.set(e.get("speaker","")); self.portrait.set(e.get("portrait",""))
  self.text.delete("1.0","end"); self.text.insert("1.0",e.get("text",""))
  self.choices.delete("1.0","end")
  self.choices.insert("1.0","\\n".join(c["text"]+" | "+c["target"] for c in e.get("choices",[])))
 def apply(self):
  if self.ei is None:return
  txt=self.text.get("1.0","end").strip()
  if self.kind.get()=="Реплика":
   e={"type":"dialogue","speaker":self.speaker.get() or "Рассказчик","text":txt,"portrait":self.portrait.get()}
  else:
   cs=[]
   for line in self.choices.get("1.0","end").splitlines():
    if line.strip():
     a=line.split("|",1); cs.append({"text":a[0].strip(),"target":a[1].strip() if len(a)>1 else self.scene()["id"]})
   e={"type":"choice","text":txt,"choices":cs}
  self.scene()["entries"][self.ei]=e; self.refresh_rows(); self.rows.selection_set(str(self.ei)); self.pick_entry(); self.status.set("Элемент обновлён")
 def add_line(self):
  self.scene()["entries"].append({"type":"dialogue","speaker":"Персонаж","text":"Новая реплика","portrait":""}); self.refresh_rows(); self.select_last()
 def add_choice(self):
  sid=self.scene()["id"]; self.scene()["entries"].append({"type":"choice","text":"Что вы сделаете?","choices":[{"text":"Вариант 1","target":sid},{"text":"Вариант 2","target":sid}]}); self.refresh_rows(); self.select_last()
 def select_last(self):
  i=len(self.scene()["entries"])-1; self.rows.selection_set(str(i)); self.pick_entry()
 def del_entry(self):
  if self.ei is not None: del self.scene()["entries"][self.ei]; self.refresh_rows()
 def move(self,d):
  if self.ei is None:return
  a=self.scene()["entries"]; n=self.ei+d
  if 0<=n<len(a): a[self.ei],a[n]=a[n],a[self.ei]; self.refresh_rows(); self.rows.selection_set(str(n)); self.pick_entry()
 def add_scene(self):
  name=simpledialog.askstring("Новая сцена","Название сцены:")
  if name:
   self.data["scenes"].append({"id":"scene_"+str(len(self.data["scenes"])+1),"name":name,"background":"","entries":[]}); self.si=len(self.data["scenes"])-1; self.refresh()
 def del_scene(self):
  if len(self.data["scenes"])<2: messagebox.showwarning("Сцены","Нужна хотя бы одна сцена."); return
  if messagebox.askyesno("Удалить","Удалить выбранную сцену?"):
   del self.data["scenes"][self.si]; self.si=max(0,self.si-1); self.refresh()
 def asset(self,path):
  if not self.folder:
   f=filedialog.askdirectory(title="Выберите папку проекта")
   if not f:return ""
   self.folder=Path(f); (self.folder/"assets").mkdir(exist_ok=True)
  dest=self.folder/"assets"/Path(path).name; dest.parent.mkdir(exist_ok=True)
  if Path(path).resolve()!=dest.resolve(): shutil.copy2(path,dest)
  return "assets/"+dest.name
 def background(self):
  p=filedialog.askopenfilename(filetypes=[("Изображения","*.png *.jpg *.jpeg *.gif")])
  if p:
   r=self.asset(p)
   if r:self.scene()["background"]=r; self.bglabel.config(text="Фон: "+r)
 def pick_portrait(self):
  p=filedialog.askopenfilename(filetypes=[("Изображения","*.png *.jpg *.jpeg *.gif")])
  if p:self.portrait.set(self.asset(p))
 def new(self):
  if messagebox.askyesno("Новый проект","Создать новый проект?"):
   self.data=json.loads(json.dumps(DEFAULT)); self.folder=None; self.si=0; self.refresh()
 def open(self):
  p=filedialog.askopenfilename(filetypes=[("Проект NovelForge","*.nvp *.json")])
  if not p:return
  try:self.data=json.loads(Path(p).read_text(encoding="utf-8")); self.folder=Path(p).parent; self.si=0; self.refresh()
  except Exception as e:messagebox.showerror("Ошибка",str(e))
 def save(self):
  if not self.folder:
   f=filedialog.askdirectory(title="Папка проекта")
   if not f:return
   self.folder=Path(f); (self.folder/"assets").mkdir(exist_ok=True)
  p=self.folder/"project.nvp"; p.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding="utf-8")
  self.status.set("Сохранено: "+str(p)); messagebox.showinfo("Сохранение","Проект сохранён в "+str(p))
 def play(self):
  self.apply()
  if not self.folder:
   messagebox.showinfo("Предпросмотр","Сначала сохраните проект."); return
  Player(self.root,self.data,self.folder)

class Player:
 def __init__(self,parent,data,folder):
  self.data=data; self.folder=folder; self.sid=data.get("start_scene",data["scenes"][0]["id"]); self.i=0; self.photo=None
  self.win=tk.Toplevel(parent); self.win.title("Предпросмотр игры"); self.win.geometry("950x650"); self.win.configure(bg="#11131b")
  self.canvas=tk.Canvas(self.win,bg="#25283a",highlightthickness=0); self.canvas.pack(fill="both",expand=True)
  self.panel=tk.Frame(self.win,bg="#171923",padx=20,pady=15); self.panel.place(relx=.04,rely=.70,relwidth=.92,relheight=.27)
  self.name=tk.Label(self.panel,text="",bg="#171923",fg="#b6a9ff",font=("Segoe UI",14,"bold")); self.name.pack(anchor="w")
  self.line=tk.Label(self.panel,text="",bg="#171923",fg="white",font=("Segoe UI",13),wraplength=850,justify="left"); self.line.pack(anchor="w",pady=8)
  self.buttons=tk.Frame(self.panel,bg="#171923"); self.buttons.pack(anchor="w",fill="x")
  self.next=tk.Button(self.panel,text="Далее ›",command=self.advance,bg=ACC,fg="white",relief="flat",padx=16,pady=6); self.next.pack(side="right")
  self.show_scene()
 def scene(self):return next((s for s in self.data["scenes"] if s["id"]==self.sid),self.data["scenes"][0])
 def show_scene(self):
  self.canvas.delete("all"); bg=self.scene().get("background")
  if bg:
   try:
    from PIL import Image,ImageTk
    im=Image.open(self.folder/bg); im.thumbnail((1200,850)); self.photo=ImageTk.PhotoImage(im)
    self.canvas.create_image(475,320,image=self.photo)
   except ImportError:
    try:self.photo=tk.PhotoImage(file=str(self.folder/bg)); self.canvas.create_image(475,320,image=self.photo)
    except Exception:pass
   except Exception:pass
  self.advance()
 def advance(self):
  for w in self.buttons.winfo_children():w.destroy()
  entries=self.scene()["entries"]
  if self.i>=len(entries):
   self.name.config(text="Конец сцены"); self.line.config(text="Сцена завершена."); self.next.config(text="Закрыть",command=self.win.destroy); return
  e=entries[self.i]; self.i+=1
  if e["type"]=="choice":
   self.name.config(text="Выбор"); self.line.config(text=e.get("text",""))
   self.next.pack_forget()
   for c in e.get("choices",[]):
    tk.Button(self.buttons,text=c["text"],command=lambda t=c["target"]:self.go(t),bg="#394158",fg="white",relief="flat",padx=10,pady=6).pack(side="left",padx=3)
  else:
   self.next.pack(side="right"); self.next.config(text="Далее ›",command=self.advance)
   self.name.config(text=e.get("speaker","")); self.line.config(text=e.get("text",""))
 def go(self,target):
  if not any(s["id"]==target for s in self.data["scenes"]):messagebox.showerror("Переход","Сцена не найдена: "+target); return
  self.sid=target; self.i=0; self.show_scene()

if __name__=="__main__":
 root=tk.Tk(); Editor(root); root.mainloop()
