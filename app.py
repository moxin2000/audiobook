import PyPDF2
import pyttsx3

speaker = pyttsx3.init()Code language: Python (python)

pdfReader = PyPDF2.PdfFileReader(open('file.pdf', 'rb'))Code language: Python (python)

for page_num in range(pdfReader.numPages):
 text =  pdfReader.getPage(page_num).extractText()
 speaker.say(text)
 speaker.runAndWait()
 speaker.stop()Code language: Python (python)

engine.save_to_file(text, 'audio.mp3')
 engine.runAndWait()Code language: Python (python)
