### +============================================================================< Agosto 2023 >===+
###    _____   .__                                .___    _____                 ____    _______   
###   /     \  |__|  ____ _______ _____     ____  |   |  /  _  \       ___  __ /_   |   \   _  \  
###  /  \ /  \ |  | / ___\\_  __ \\__  \   /    \ |   | /  /_\  \      \  \/ /  |   |   /  /_\  \ 
### /    Y    \|  |/ /_/  >|  | \/ / __ \_|   |  \|   |/    |    \      \   /   |   |   \  \_/   \
### \____|__  /|__|\___  / |__|   (____  /|___|  /|___|\____|__  / /\    \_/ /\ |___| /\ \_____  /
###         \/    /_____/              \/      \/              \/  \/        \/       \/       \/ 
###
### +==============================================================================================+ 
### Created by:
###
### Fernando Mateluna                                                                                          
### Martín Vergara B.
### 

import logging
import os
import shutil
import sys
import openai  # pip install openai
import typer  # pip install "typer[all]"
from rich import print  # pip install rich
from rich.table import Table
import subprocess
from datetime import datetime
import sys 
sys.path.append('..')
from util import utilfunctions


class MigranIABot:

    def __init__(self, api_key):
        self.currentlypath=os.getcwd()
        filenamelog=self.creararchivolog()
        logging.basicConfig(filename=filenamelog, level=logging.DEBUG)
        

        self.api_key = api_key
        self.messages = []
        self.response = ""
        self.EOF = "***-EOF-***"
        self.PROMPT_MIGRACION = self.readContentFromPath("./config/prompt.gpt")
            
    def context(self, context):
        context = {"role": "system",
                "content": context}
        
        self.messages = [context]
        content = "Eres un developer senior."
        self.messages.append({"role": "user", "content": content})
        self.origin_path = ""
        self.origin_tech = ""
        self.destiny_tech = ""

        try:
            self.response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=self.messages)

            if self.response == "" or len (self.response)== 0:
                ###logging.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.")  
                return self.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.", -1)
            return True
        except openai.error.APIError as e:
        #Handle API error here, e.g. retry or log
            ###logging.error(f"OpenAI API returned an API Error: {e}")
            return self.error(f"OpenAI API returned an API Error: {e}",-10)
        except openai.error.APIConnectionError as e:
        #Handle connection error here
            ###logging.error(f"Failed to connect to OpenAI API: {e}")
            return self.error(f"Failed to connect to OpenAI API: {e}",-10)
        except openai.error.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
            ###logging.error(f"OpenAI API request exceeded rate limit: {e}")
            return self.error(f"OpenAI API request exceeded rate limit: {e}",-10)


    def migrar(self, origin_path, origin_tech, destiny_tech,migration_path):

        self.origin_path = origin_path
        self.origin_tech = origin_tech
        self.destiny_tech = destiny_tech
        self.migration_path = migration_path

        if not os.path.exists(self.migration_path):
            try:
                subprocess.run(["mkdir", self.migration_path], shell=True, check=True)                
            except subprocess.CalledProcessError as e:
                self.error("No se pudo crear la carpeta '{self.migration_path}': {e}",-1)           


        if not os.path.exists(origin_path):
            return self.error("\n * El directorio '"+origin_path+"' especificado No existe", -1)            
        
        if not self.findFiles(origin_path, origin_tech):
            return False
        return True
        
    def findFiles(self, pathFiles, origin_tech):           
        #TODO : Tarea pendiente identificar la extencion de la tecnologia de origen
        if origin_tech.startswith("java")  or len(origin_tech)>0:   
            ###logging.info(pathFiles)
            for root, dirs, files in os.walk(pathFiles, topdown=False):
                for name in files:
                    #Identifica las extenciones de archivos a migrar
                    if name.endswith(".java") or len(origin_tech)>0:
                        ###logging.info("name:"+name)
                        if not self.migraSource(root,name):
                            return False
            return True
        else:
            return self.error("\n * Lenguage de origen '" + origin_tech+ "' Aun no se encuentra implementado para traducir. \n Intente con Java !!! ", -2)


    def creararchivolog(self):
        
        logpath=self.currentlypath+"\\log"

        if not os.path.exists(logpath):
            try:
                subprocess.run(["mkdir", logpath], shell=True, check=True)                
            except subprocess.CalledProcessError as e:
                return self.error("No se pudo crear la carpeta log': {e}",-1)     

        temporarylog = datetime.now().strftime("%Y%m%d%H%M%S")
        filog=logpath+"\\log"+temporarylog+".txt"
        return filog   
    
    def readContentFromPath(self,path):
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
                                        tecnologia_original=self.origin_tech, 
                                        tecnologia_destino=self.destiny_tech)
        
        requestia = prompt
        
        # Contexto del asistente
        context = {"role": "assistant", "content": "Eres un developer senior."}
        messages = [context]
        
        messages.append({"role": "assistant", "content": requestia})

        try:
            ## haciendo la pregunta a CHATGPT
            responseia = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages)   

            if responseia == "" or len (responseia)== 0:
                ###logging.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.")  
                return self.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.", -1)

        except openai.error.APIError as e:
            #Handle API error here, e.g. retry or log
            ###logging.error(f"OpenAI API returned an API Error: {e}")
            return self.error(f"OpenAI API returned an API Error: {e}",-10)
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            ###logging.error(f"Failed to connect to OpenAI API: {e}")
            return self.error(f"Failed to connect to OpenAI API: {e}",-10)
        except openai.error.RateLimitError as e:
             #Handle rate limit error (we recommend using exponential backoff)
            ###logging.error(f"OpenAI API request exceeded rate limit: {e}")
            return self.error(f"OpenAI API request exceeded rate limit: {e}",-10)

         ## Obteniendo la respuesta de CHATGPT
        response_content = responseia.choices[0].message.content        

        
        messages.append({"role": "assistant", "content": response_content})

        if response_content == "" or len (response_content)== 0:
            ###logging.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.")  
            return self.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.", -1)

        isNameFile = True
        nameFile =""
        contentFile =""
        comentarios=""
        for line in response_content.splitlines():
            if isNameFile:
                if line.startswith('@@@@'):
                    nameFile=line.replace("@@@@", "")
                    isNameFile=False
            else:
                if line != self.EOF:
                    if nameFile!="":
                        contentFile += line + "\n"
                else:
                    if self.createSource(temporarypath, nameFile, contentFile):
                        isNameFile=True
                        nameFile =""
                        contentFile =""
                    else:
                        return False

        self.historIA(filename,prompt, response_content, comentarios)        
        return True

    def historIA(self,filename,request, response, comentarios):
        shutil.copyfile(os.getcwd() + "/config/styles.css", self.migration_path + "/styles.css")
        htmfile=utilfunctions.createhtml(request, response, self.origin_tech,self.destiny_tech, comentarios)
        if not os.path.exists(self.migration_path):
            try:
                subprocess.run(["mkdir", self.migration_path], shell=True, check=True)                
            except subprocess.CalledProcessError as e:
                return self.error("No se pudo crear la carpeta '{self.migration_path}': {e}",-1)

        path = self.migration_path +"\\"+ filename + ".html"
        file = open(path,"w")
        file.write(htmfile)
        file.close()

    def createSource(self,temporarypath, filename,content):
        table = Table(filename)
        table.add_row(content)
        print(table)    

        relativepath= temporarypath.replace(self.origin_path, "")

        outputmainfolder = self.migration_path +"\\fuentes" + relativepath 

        if not os.path.exists(outputmainfolder):
            try:
                subprocess.run(["mkdir", outputmainfolder], shell=True, check=True)                
            except subprocess.CalledProcessError as e:
                return self.error("No se pudo crear la carpeta '{outputmainfolder}': {e}",-1)     

        path = outputmainfolder +"\\"+ filename
        logging.info("creando  archivo  =>"+path)
        file = open(path,"w")
        file.write(content)
        file.close()   
        return True     

    def error(self, mensaje, codSalida):
        print(mensaje)
        logging.error(mensaje)
        return False



     
        
