import os
import sys
import openai  # pip install openai
import typer  # pip install "typer[all]"
from rich import print  # pip install rich
from rich.table import Table
import subprocess


class MigranIABot:

    def __init__(self, api_key):
        self.api_key = api_key
        self.messages = []
        self.response = ""
        self.EOF = "#############################################"
        self.PROMPT_MIGRACION = """
        Migra el siguiente codigo fuentes : \n{fuentes}\n el cual esta desarrollado en {tecnologia_original}, debes migrar esto a {tecnologia_destino},
        quiero que tu respuesta este en el siguiento formato
        
        @@@@NOMBRE ARCHIVO
        CONTENIDO CODIGO MIGRADO
        #############################################

        No agregue espacios en blanco despues de la ultima linea de codigo, ya que esto puede generar errores en la migracion
        No coloques comentarios en el codigo, ya que esto puede generar errores en la migracion
        No menciones sugerencias ni acciones dentro del codigo, si quieres realizarlo comentalo en formato de comentario
        . \n
        """
            
    def context(self, context):
        context = {"role": "system",
                "content": context}
        
        self.messages = [context]
        content = "Eres un developer senior."
        self.messages.append({"role": "user", "content": content})
        self.origin_path = ""
        self.origin_tech = ""
        self.destiny_tech = ""

        self.response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages)

    def migrar(self, origin_path, origin_tech, destiny_tech):
        self.origin_path = origin_path
        self.origin_tech = origin_tech
        self.destiny_tech = destiny_tech
        self.findFiles(origin_path)
        
    def findFiles(self, pathFiles):           
        print(pathFiles)     
        for root, dirs, files in os.walk(pathFiles, topdown=False):
            for name in files:
                self.migraSource(root,name)



    def readContentFromPath(selt,path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def migraSource(self, path,filename):
        #print("Migra el archivo : " + name + " hacia " +   self.destiny_tech)
        fileNameAndPath = path + "\\" + filename
        sources = self.readContentFromPath(fileNameAndPath)
            
        temporarypath = path
        
        subPrompt = filename + "\n" +sources
        
        
        prompt = self.PROMPT_MIGRACION.format(fuentes=subPrompt,
                                        tecnologia_original=origin_tech, 
                                        tecnologia_destino=destiny_tech)

        requestIA = prompt
        
        # Contexto del asistente
        context = {"role": "system", "content": "Eres un developer senior."}
        messages = [context]
        
        messages.append({"role": "user", "content": requestIA})
        responseIA = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages)        
            
        response_content = responseIA.choices[0].message.content        
        messages.append({"role": "assistant", "content": response_content})

        isNameFile = True
        nameFile =""
        contentFile =""

        for line in response_content.splitlines():
            if isNameFile:
                if line.startswith('@@@@'):
                    nameFile=line.replace("@@@@", "")
                    isNameFile=False
            else:
                if line != self.EOF:
                    contentFile += line + "\n"
                else:
                    self.createSource(temporarypath, nameFile, contentFile)
                    isNameFile=True
                    nameFile =""
                    contentFile =""        

    def createSource(self,temporarypath, filename,content):
        table = Table(filename)
        table.add_row(content)
        print(table)    

        relativepath= temporarypath.replace(self.origin_path, "")
        
        ###get current path
        currentpath = os.path.dirname(os.path.realpath(__file__))
        outputmainfolder = currentpath +"\\output" + relativepath 
        if not os.path.exists(outputmainfolder):
            try:
                subprocess.run(["mkdir", outputmainfolder], shell=True, check=True)                
            except subprocess.CalledProcessError as e:
                print(f"No se pudo crear la carpeta '{outputmainfolder}': {e}")     

        path = outputmainfolder +"\\"+ filename
        print("creando  archivo  =>"+path)
        file = open(path,"w")
        file.write(content)
        file.close()        


    def save_response_IA(self,response):
        
        return True

if __name__ == "__main__":

    botConMigranIA = MigranIABot(os.getenv("OPENAI_API_KEY"))
    botConMigranIA.context("Eres un developer senior.")

    print("🤖 [bold green]Migracion asistida por ChatGPT[/bold green]")
    origin_path =  typer.prompt("\nIngrese ruta de fuentes a migrar :")
    origin_tech =  typer.prompt("\nIngrese tecnologia de Origen  :")
    destiny_tech = typer.prompt("\nIngrese tecnologia de Destino :")
    botConMigranIA.migrar(origin_path, origin_tech, destiny_tech)