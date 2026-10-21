
import customtkinter as ctk
from tkinter import filedialog, messagebox
import librosa
from music21 import stream, note

app = ctk.CTk()
app.title("Sound Sketch")
app.geometry("1000x800")

ctk.CTkLabel(
    app, text="🎵 Sound Sketch",
    font=("Arial", 62, "bold"),
    text_color='blue'
).pack(pady=20)

result = ctk.CTkLabel(app, 
                      text="Please upload an audio file (.wav,.mp3)",font=("Arial", 40))
result.pack(pady=10,)
a=ctk.CTkLabel(app,
               text='''please wait after you upload 
                        the file untill the pop up 
                        windows apppear''',text_color='yellow')
a.pack(pady=10)
def generate():
    file = filedialog.askopenfilename(filetypes=[("Audio", "*.wav *.mp3")])
    if not file:
        return
    
    y, sr = librosa.load(file)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    score = stream.Stream()
    previous_s = None

    for i in range(pitches.shape[1]):
        index = magnitudes[:, i].argmax()
        frequency = pitches[index, i]

        if frequency > 0:
            
            n = librosa.hz_to_note(frequency).replace("♯", "#")#because in music 21 sheet we use this ♯ symbol instead of #(hashtag)
            if n != previous_s:

                score.append(note.Note(n))
                previous_s = n

   # if anybody reading this code dont know musicsheet comes with .musicxml extension
        
#fp represents file path somewhy i keep forgeting that
    if messagebox.askyesno("Save Music Sheet", "Do you want to save your music sheet?"):
        path = filedialog.asksaveasfilename(#ask save as file name
        defaultextension=".musicxml",
        filetypes=[("MusicXML", "*.musicxml")])

        if not path:
            result.configure(text="Save cancelled.",text_color='green')
            return

        try:
            score.write("musicxml", fp=path)
            result.configure(
                text="✅ Music sheet saved!",
                text_color="green")
                
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
    else:
        result.configure(text="Save skipped.",text_color='orange')
ctk.CTkButton(
    app, text="Upload & Generate Sheet",
    command=generate,
    height=50,
    width=300).pack(pady=40,)

ctk.CTkLabel(app,text='''⚠️Sound Sketch is still a sample prototype and
                may contain incorrect notes, rhythems and missing sections
                of the music.remember that it may contain flaws and is not a final product.
                                    ~best regards from the developer''',font=('Arial',30),text_color='#00FFFF').pack(pady=10)


app.mainloop()
