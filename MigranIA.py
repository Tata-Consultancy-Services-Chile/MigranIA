import json
import os
import openai  # pip install openai
import typer  # pip install "typer[all]"
from rich import print  # pip install rich
from rich.table import Table
import sys
import shutil

EOF = "#############################################"


PROMPT_MIGRACION = """
    Migra los siguientes codigos fuentes : \n{fuentes}\n los cuales estan en {tecnologia_original}, debes migrar esto a {tecnologia_destino},
    quiero que tu respuesta este en el siguiento formato
    
    @@@@NOMBRE ARCHIVO
    CONTENIDO CODIGO MIGRADO
    #############################################

    No agregue espacios en blanco despues de la ultima linea de codigo, ya que esto puede generar errores en la migracion
    No coloques comentarios en el codigo, ya que esto puede generar errores en la migracion
    No menciones sugerencias ni acciones dentro del codigo, si quieres realizarlo comentalo en formato de comentario
    . \n
"""

def main():
    # obtener la llave de openai desde el archivo .env
    openai.api_key = os.getenv("OPENAI_API_KEY")

    print("🤖 [bold green]Migracion asistida por ChatGPT[/bold green]")
    origin_path =  typer.prompt("\nIngrese ruta de fuentes a migrar :")
    origin_tech =  typer.prompt("\nIngrese tecnologia de Origen  :")
    destiny_tech = typer.prompt("\nIngrese tecnologia de Destino :")
    sources = readFilePathsFromPath(origin_path)
    
    prompt = PROMPT_MIGRACION.format(fuentes=sources, tecnologia_original=origin_tech, tecnologia_destino=destiny_tech)
 
    requestIA = prompt

    # Contexto del asistente
    context = {"role": "system",
               "content": "Eres un developer senior."}
    messages = [context]

    messages.append({"role": "user", "content": requestIA})
    responseIA = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages)
    
    #print(responseIA)

    response_content = responseIA.choices[0].message.content
    messages.append({"role": "assistant", "content": response_content})
    
    
    #itera la lectura del response_content linea a linea
    isNameFile = True

    nameFile =""
    contentFile =""

    for line in response_content.splitlines():
        if isNameFile:
            if line.startswith('@@@@'):
                nameFile=line.replace("@@@@", "")
                isNameFile=False
        else:
            if line != EOF:
                contentFile += line + "\n"
            else:
                ### variables usadas para descomprimir el archivo.
                ####   filename = "./xxx.zip"
                ####   outputFolder = "./f1"
                ####   extractZipFile(filename, outputFolder)

                createSource(nameFile,contentFile)
                isNameFile=True
                nameFile =""
                contentFile =""


def createSource(filename,content):
    table = Table(filename)
    table.add_row(content)
    print(table)    


    #verificar si carpeta existe, sino se crea una en la ruta especificada
    if not os.path.exists("./output"):
        print("creando carpeta output")
        os.mkdir("./output")
    print("Los fuentes seran dejados en la carpeta 'output'")

    #verificar si archivo existe, sino se crea un archivo nuevo
    path = "./output/"+ filename
    if os.path.exists(path):
        print("El archivo ya existe - Proceso se ha detenido.")
        print("Borre los archivos para continuar")
        # salir de la aplicacion
        sys.exit(-1);
        
       
    else:
        print("creando  archivo  =>"+filename)
        file = open("./output/" + (filename),"w")
        file.write(content)
        file.close()

#crear funcion para leer nombres de archivos de un directorio y iterar cada nonmbre de archivo
def readFilePathsFromPath(path):
    contentSourcesFile = ""
    
    for root, dirs, files in os.walk(path):
        for file in files:
            contentSourcesFile += "\n" + file + readContentFromPath(path +"\\" +file) + "\n"        
    return contentSourcesFile



def readContentFromPath(path):
    with open(path, "r") as f:
        content = f.read()
    return content
    
def extractZipFile(filename,outputFolder):
    shutil.unpack_archive(filename, outputFolder)   
    return "["+filename+"] archivo descomprimido exitosamente"


if __name__ == "__main__":
    typer.run(main)
