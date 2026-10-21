from fasthtml.common import *

from starlette.datastructures import UploadFile
from starlette.responses import FileResponse

import librosa
from music21 import stream, note

from pathlib import Path
from tempfile import NamedTemporaryFile
import uuid

#upper line of ocde imports all esstial library
app,rt=fast_app()
application = app

OUTPUT_DIR=Path("generated")
OUTPUT_DIR.mkdir(exist_ok=True)

#rt stands for router
@rt("/")
def home_page():
    return (
        H1("Sound Sketch"),#replaace of st.title
        P("Upload your MP3 or .wav file and get the music sheet of audio"),#replace of st.write
        Img(
            src="https://wallpapercave.com/wp/wp11882246.jpg",
            alt="Welcome to Sound Sketch",
            width=400,
            height=200
        ),#this shows image replace of st.img
        Form(
            Input(
                type="file",
                name="file",
                accept=".mp3,.wav",
                required=True),#Input ask for input an there are parameteers that suggests ut work 
            #aside from that it creates a file uploader because its type =file
            
            Button("Generate Music Sheet"),#st.button
            
            action="/convert",#run the convert function from router convert
            method="post",
            enctype="multipart/form-data"
        )
    )


@rt("/convert", methods=["POST"])
async def convert(file: UploadFile):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in [".mp3", ".wav"]:
        return P("Please upload an MP3 or WAV file.")#it requires to the spevific type 

    audio_data = await file.read()#reading the file and storing that a variable

    if not audio_data:
        return P("The uploaded file is empty.")

    temp_path = None
    output_path = OUTPUT_DIR / f"{uuid.uuid4().hex}.musicxml"

    try:
        with NamedTemporaryFile(suffix=extension, delete=False) as temp:
            temp.write(audio_data)#storing data to a temporary variable 
            temp_path = Path(temp.name)

#here the backend starts

        y, sr = librosa.load(str(temp_path))

        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        notes_sheet = []
        cleaning_notes = []

        for t_frame in range(pitches.shape[1]):

            loudest_frequency_index = magnitudes[:, t_frame].argmax()
            #finding loudest frequency in the audio 
            detected_frequency = pitches[loudest_frequency_index, t_frame]# takes all detechted frequuencies

            if detected_frequency > 0:

                detected_note = librosa.hz_to_note(detected_frequency)#finding all notes from frequencies
                
                notes_sheet.append(detected_note)#adding detceheted notes to our notes sheet 

        for a in notes_sheet:
            a = a.replace("♯", "#")# convertting the # symbol to the fisrt hashtag symbol because music 21 supports 1st one and librosa supports standard  #

            if not cleaning_notes or a != cleaning_notes[-1]:
                cleaning_notes.append(a)#match

        score = stream.Stream()# score is the whole 

        for n in cleaning_notes:
            note_obj = note.Note(n)
            
            score.append(note_obj)#adding the not obj that we created upper line 

        score.write("musicxml", fp=str(output_path))# writing the output musicxml sheet

        return (
            H1("Sound Sketch"),#h1 tag from html
            H2("Music sheet successfully generated!"),#h2 sub heading
            
            P(f"Detected {len(cleaning_notes)} notes."),#paragraph replace of st.write
            P(
                A(
                    "Download MusicXML",

                    href=f"/download/{output_path.stem}"
                )
            ),
            P(
                "Sound Sketch is currently should be used for simple piano recordings."
            ),
            P(
                '''Sound Sketch is still a sample prototype and
                may contain incorrect notes, rhythems and missing sections
                of the music.remember that it may contain flaws and is not a final product.
                                    ~best regards from the developer'''),
            
            P(A("Convert another file", href="/"))# calling the whole code agin if user clciks this link
        )

    except Exception as e:

        print(f"Conversion error: {e}")

        return (
            H1("Conversion failed"),

            P("Could not process the audio file. Please try another MP3 or WAV file."),
            P(A("Go back", href="/"))
        )

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


@rt("/download/{file_id}")# adding downloading button and asking user where to store it
def download(file_id: str):
    if not file_id or any(
        c not in "0123456789abcdef"
        for c in file_id.lower()
    ):
        return P("File not found.")

    output_path = OUTPUT_DIR / f"{file_id}.musicxml"

    if not output_path.is_file():
        return P("File not found.")

    return FileResponse(
        output_path,
        filename="output.musicxml",
        media_type="application/vnd.recordare.musicxml+xml"
    )


if __name__ == "__main__":
    serve()

# serve serveing
# frequency is wriiten in hz
#its my first project written in fasthtml so give me feedback
