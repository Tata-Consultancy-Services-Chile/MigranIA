    
    def extractZipFile(self, filename,outputFolder):
        if not os.path.exists(outputFolder):
            os.mkdir(outputFolder)

        if os.path.exists(filename):
            shutil.unpack_archive(filename, outputFolder) 
            msg= ("["+filename+"] archivo descomprimido exitosamente")
            print(msg)
        else:
            self.salir("Archivo "+filename+" No encontrado.!",-3);
        return ""