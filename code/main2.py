
import librosa
import streamlit as st
from music21 import stream, note

st.title('Sound Sketch')
st.write('upload your mp3 or .wav file and get the music sheet of audio')
st.image('https://wallpapercave.com/wp/wp11882246.jpg')
file=st.file_uploader('please upload your mp3 or .wav file here',
                      type=['mp3','wav'])
notes_sheet=[]

cleaning_notes=[]


if file is not None:
    y,sr = librosa.load(file)

    # '''y is audio sample
    #     sr is sample rate(sample per second)
    #     duration of the sound depends on y and sr
    #
    #      because duration=length of y/sr'''

    pitches, magnitudes=librosa.piptrack(y=y,sr=sr)
    # '''piptrack returns two lists(metrices) pitches and magnitude
    #     pitches contains  frequency while
    #     magnitudes contains loudness(how loud is the frequency)'''




# '''    for row in pitches:
#         for frequencies in row:
#             if frequencies>0:
#                 notes=librosa.hz_to_note(frequencies)
#                 notes_sheet.append(notes)
# ''' it's also a method to detect not but they dont store duration  
            
                # librosa.hz_to_note()this function takes
                #   frequencies and converts it into notes
                #   (piano notes)

#unique_notes=list(dict.fromkeys(notes_sheet))
    for t_frame in range(pitches.shape[1]):

        loudest_frequency_index = magnitudes[:, t_frame].argmax()
        detected_frequency = pitches[loudest_frequency_index, t_frame]

        if detected_frequency > 0:

            detected_note = librosa.hz_to_note(detected_frequency)
            notes_sheet.append(detected_note)
    score=stream.Stream()
    for a in notes_sheet:
        a=a.replace('♯','#')
        if len(cleaning_notes)==0 or a!=cleaning_notes[-1]:
            cleaning_notes.append(a)

    for n in cleaning_notes:
        note_obj=note.Note(n)
        score.append(note_obj)
    
    score.write('musicxml', fp='output.musicxml')

    st.download_button(
    "Download MusicXML",
    data=open("output.musicxml","rb"),
    file_name="output.musicxml"
    )
    st.success('musicsheet successfully generated')
    st.info(
    "Sound Sketch is currently optimized for simple piano recordings.")
    st.warning('''Sound Sketch is still a sample prototype and
                may contain incorrect notes, rhythems and missing sections
                of the music.remember that it may contain flaws and is not a final product.
                                    ~best regards from the developer''')
