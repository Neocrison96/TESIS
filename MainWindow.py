import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout, QFileDialog, QSlider, QLineEdit
from PyQt5 import uic
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import QLocale
import math as mt
import numpy as np
from scipy.io.wavfile import read, write
import matplotlib.pyplot as plt



def CalcularITD(dis_oidos):
      dis_oidos2 = dis_oidos/100 #Conversion de cm a metros
      a = dis_oidos2/2 
      c = 343 #Velocidad del sonido
      azimuth1 = np.arange(0,np.pi/2,np.pi/18)
      azimuth2 = np.arange(np.pi/2,np.pi,np.pi/18)
      itd1 = azimuth1+np.sin(azimuth1)
      ITD1 = (a/c)*itd1
      itd2 = np.pi-azimuth2+np.sin(azimuth2)
      ITD2 = (a/c)*itd2
      ITD1 = ITD1.tolist()
      ITD2 = ITD2.tolist()
      ITD = []
      azimuth =[]
      for i in range(len(ITD1)):
            x = ITD1[i]
            ITD.append(x)
      for i in range(len(ITD2)):
            x = ITD2[i]
            ITD.append(x)
      for i in range(len(azimuth1)):
            x = azimuth1[i]
            azimuth.append(x)
      for i in range(len(azimuth2)):
            x = azimuth2[i]
            azimuth.append(x)
      j = len(azimuth)
      y = azimuth[j-1]+np.pi/18
      azimuth.append(y)
      ITD.append(0)
      return ITD

def leerArchivo(nombre):
      datos= read(nombre)
      audios = datos[1]
      ImpulsoL = audios[:,1]
      ImpulsoR = audios[:,0]
      ImpulsoL = ImpulsoL.tolist()
      ImpulsoR = ImpulsoR.tolist()
      return ImpulsoL, ImpulsoR

def RellenarZeros(ImpulsoL, ImpulsoR, Audio):
      i = len(ImpulsoL)
      for i in range(len(Audio)):
            ImpulsoL.append(0)
            ImpulsoR.append(0)
      return ImpulsoL, ImpulsoR

def Convolucion(Impulso1,Impulso2, Canal):
      ConvoL = np.convolve(Canal,Impulso1,mode='full')
      ConvoR = np.convolve(Canal,Impulso2,mode='full')
      ConvolucionL = ConvoL.tolist()
      ConvolucionR = ConvoR.tolist()
      
      return ConvolucionL, ConvolucionR

def Comparacion(Impulso,Ref,Original):
      if Original > Ref:
            y = Original - Ref
            Impulso.reverse()
            for i in range(y):
                  Impulso.append(0)
            Impulso.reverse()
      elif Original < Ref:
            y = Ref - Original
            for i in range(y):
                  Impulso.pop(i)
      else:
            pass
      
      return Impulso

def Normalizar(Arreglo1,Arreglo2):
      y1 = max(Arreglo1)
      y2 = max(Arreglo2)
      Arreglo3 = []
      Arreglo4 = []
      if y1 > y2:
            for i in range(len(Arreglo1)):
                  x = (Arreglo1[i]/(3*y1))
                  Arreglo3.append(x)
            for i in range(len(Arreglo2)):
                  x = (Arreglo2[i]/(3*y1))
                  Arreglo4.append(x)
      elif y2 > y1:
            for i in range(len(Arreglo1)):
                  x = (Arreglo1[i]/(1.8*y2))
                  Arreglo3.append(x)
            for i in range(len(Arreglo2)):
                  x = (Arreglo2[i]/(1.8*y2))
                  Arreglo4.append(x)

      return Arreglo3, Arreglo4

def Revisar_Longitud(Arreglo1,Arreglo2):
      x = len(Arreglo1)
      y = len(Arreglo2)
      if x > y:
            k = x-y
            for i in range(k):
                  Arreglo2.append(0)
      elif y > x:
            k = y-x
            for i in range(k):
                  Arreglo1.append(0)
      
class VentanaPrincipal(QMainWindow):
      def __init__(self):
            QMainWindow.__init__(self)
            uic.loadUi("Ambisonics.ui",self)
            self.pushButton.clicked.connect(self.abrirarchivo) #Funcion para abrir el archivo de Audio
            self.pushButton_3.clicked.connect(self.Binauralizar) #Funcion para binauralizar el Audio Ambisonics
            self.pushButton_2.clicked.connect(self.Exportar_Archivo)#Funcion para poder exportar el nuevo archivo de audio
            
      def abrirarchivo(self):
            global Mono
            
            while True:
                  try:
                        nombre_archivo = QFileDialog.getOpenFileName(self, 'Abrir Archivo Ambisonics format B','/Users/cristianpedraza/Desktop/','Archivos WAVE (*.wav)')
                        nombre_archivo = nombre_archivo[0]
                        datos = read(nombre_archivo)
                        audios = datos[1]
                        CanalW = audios[:,0]
                        CanalY = audios[:,1]
                        CanalZ = audios[:,2]
                        CanalX = audios[:,3]
                        break
                  except ValueError:
                        QMessageBox.warning(self, "Error", "El audio seleccionado no es Ambisonics format B")
                        
              

            Azimuth = []
            
            for i in range(len(CanalX)):
                  if CanalX[i] > 0 and CanalY[i] > 0:
                        x = mt.atan(CanalY[i]/CanalX[i])
                        Azimuth.append(x)
                  elif CanalX[i] < 0 and CanalY[i] > 0:
                        x = mt.atan(CanalY[i]/CanalX[i]) + mt.pi
                        Azimuth.append(x)
                  elif CanalX[i] < 0 and CanalY[i] < 0:
                        x = mt.atan(CanalY[i]/CanalX[i]) + mt.pi
                        Azimuth.append(x)
                  elif CanalX[i] > 0 and CanalY[i] < 0:
                        x = mt.atan(CanalY[i]/CanalX[i]) + (2*mt.pi)
                        Azimuth.append(x)
                  elif CanalX[i] == 0 and CanalY[i] > 0:
                        Azimuth.append(mt.pi/2)
                  elif CanalX[i] == 0 and CanalY[i] < 0:
                        Azimuth.append(3*mt.pi/2)
                  elif CanalX[i] > 0 and CanalY[i] == 0:
                        Azimuth.append(0)
                  elif CanalX[i] < 0 and CanalY[i] == 0:
                        Azimuth.append(mt.pi)
                  else:
                        Azimuth.append(0)
            
            Elevacion = []

            for i in range(len(CanalZ)):
                  if CanalY[i] != 0 and CanalZ[i] != 0:
                        elev = mt.atan(CanalZ[i]/CanalY[i])
                        Elevacion.append(elev)
                  else:
                        Elevacion.append(0)

            Mono = []

            for i in range(len(CanalW)):
                  s = ((1*CanalW[i])+((1-1/2))*(CanalX[i]*mt.cos(Azimuth[i])*mt.cos(Elevacion[i])+CanalY[i]*mt.sin(Azimuth[i])*mt.cos(Elevacion[i])+CanalZ[i]*mt.sin(Elevacion[i])))
                  Mono.append(s)

      def Binauralizar(self):
            global ConvL, ConvR

            directorio ='/Users/cristianpedraza/Documents/Universidad/'
            
            DIT = []
            T = 1/44100
            x = self.plainTextEdit.toPlainText()
            x = float(x)
            DIT = CalcularITD(x)
            NZref = []
            NZ = []
            Azimuth_Us = self.plainTextEdit_3.toPlainText()
            Azimuth_Us = int(Azimuth_Us)
            Elevacion_Us = self.plainTextEdit_4.toPlainText()
            Elevacion_Us = int(Elevacion_Us)
            
            if self.radioButton.isChecked():

                  ref = [0.0, 9.948031510467523e-05, 0.00019745314106415276, 0.0002924567930280854, 0.0003831198029955061, 0.0004682025911760408, 0.0005466351299945818, 0.0006175494563376969, 0.0006803060441736205, 0.0007345132362271134, 0.0006803060441736205, 0.0006175494563376969, 0.0005466351299945818, 0.0004682025911760408, 0.00038311980299550615, 0.0002924567930280854, 0.00019745314106415257, 9.948031510467516e-05, 0]
                  
                  for i in range(len(ref)):
                        x = ref[i]/T
                        NZref.append(x)

                  for i in range(len(DIT)):
                        x = DIT[i]/T
                        NZ.append(x)
                  
                  [ImpulsoL1_e0,ImpulsoR1_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e000a.wav')
                  [ImpulsoL2_e0,ImpulsoR2_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e010a.wav')
                  [ImpulsoL3_e0,ImpulsoR3_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e020a.wav')
                  [ImpulsoL4_e0,ImpulsoR4_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e030a.wav')
                  [ImpulsoL5_e0,ImpulsoR5_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e040a.wav')
                  [ImpulsoL6_e0,ImpulsoR6_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e050a.wav')
                  [ImpulsoL7_e0,ImpulsoR7_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e060a.wav')
                  [ImpulsoL8_e0,ImpulsoR8_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e070a.wav')
                  [ImpulsoL9_e0,ImpulsoR9_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e080a.wav')
                  [ImpulsoL10_e0,ImpulsoR10_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e090a.wav')
                  [ImpulsoL11_e0,ImpulsoR11_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e100a.wav')
                  [ImpulsoL12_e0,ImpulsoR12_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e110a.wav')
                  [ImpulsoL13_e0,ImpulsoR13_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e120a.wav')
                  [ImpulsoL14_e0,ImpulsoR14_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e130a.wav')
                  [ImpulsoL15_e0,ImpulsoR15_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e140a.wav')
                  [ImpulsoL16_e0,ImpulsoR16_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e150a.wav')
                  [ImpulsoL17_e0,ImpulsoR17_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e160a.wav')
                  [ImpulsoL18_e0,ImpulsoR18_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e170a.wav')
                  [ImpulsoL19_e0,ImpulsoR19_e0] = leerArchivo(directorio+'TESIS/USB/elev 0/H0e180a.wav')

                  [ImpulsoL1_e10,ImpulsoR1_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e000a.wav')
                  [ImpulsoL2_e10,ImpulsoR2_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e010a.wav')
                  [ImpulsoL3_e10,ImpulsoR3_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e020a.wav')
                  [ImpulsoL4_e10,ImpulsoR4_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e030a.wav')
                  [ImpulsoL5_e10,ImpulsoR5_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e040a.wav')
                  [ImpulsoL6_e10,ImpulsoR6_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e050a.wav')
                  [ImpulsoL7_e10,ImpulsoR7_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e060a.wav')
                  [ImpulsoL8_e10,ImpulsoR8_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e070a.wav')
                  [ImpulsoL9_e10,ImpulsoR9_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e080a.wav')
                  [ImpulsoL10_e10,ImpulsoR10_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e090a.wav')
                  [ImpulsoL11_e10,ImpulsoR11_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e100a.wav')
                  [ImpulsoL12_e10,ImpulsoR12_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e110a.wav')
                  [ImpulsoL13_e10,ImpulsoR13_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e120a.wav')
                  [ImpulsoL14_e10,ImpulsoR14_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e130a.wav')
                  [ImpulsoL15_e10,ImpulsoR15_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e140a.wav')
                  [ImpulsoL16_e10,ImpulsoR16_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e150a.wav')
                  [ImpulsoL17_e10,ImpulsoR17_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e160a.wav')
                  [ImpulsoL18_e10,ImpulsoR18_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e170a.wav')
                  [ImpulsoL19_e10,ImpulsoR19_e10] = leerArchivo(directorio+'TESIS/USB/elev 10/H10e180a.wav')

                  [ImpulsoL1_e20,ImpulsoR1_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e000a.wav')
                  [ImpulsoL2_e20,ImpulsoR2_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e010a.wav')
                  [ImpulsoL3_e20,ImpulsoR3_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e020a.wav')
                  [ImpulsoL4_e20,ImpulsoR4_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e030a.wav')
                  [ImpulsoL5_e20,ImpulsoR5_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e040a.wav')
                  [ImpulsoL6_e20,ImpulsoR6_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e050a.wav')
                  [ImpulsoL7_e20,ImpulsoR7_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e060a.wav')
                  [ImpulsoL8_e20,ImpulsoR8_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e070a.wav')
                  [ImpulsoL9_e20,ImpulsoR9_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e080a.wav')
                  [ImpulsoL10_e20,ImpulsoR10_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e090a.wav')
                  [ImpulsoL11_e20,ImpulsoR11_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e100a.wav')
                  [ImpulsoL12_e20,ImpulsoR12_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e110a.wav')
                  [ImpulsoL13_e20,ImpulsoR13_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e120a.wav')
                  [ImpulsoL14_e20,ImpulsoR14_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e130a.wav')
                  [ImpulsoL15_e20,ImpulsoR15_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e140a.wav')
                  [ImpulsoL16_e20,ImpulsoR16_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e150a.wav')
                  [ImpulsoL17_e20,ImpulsoR17_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e160a.wav')
                  [ImpulsoL18_e20,ImpulsoR18_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e170a.wav')
                  [ImpulsoL19_e20,ImpulsoR19_e20] = leerArchivo(directorio+'TESIS/USB/elev 20/H20e180a.wav')

                  [ImpulsoL1_e30,ImpulsoR1_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e000a.wav')
                  [ImpulsoL2_e30,ImpulsoR2_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e010a.wav')
                  [ImpulsoL3_e30,ImpulsoR3_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e020a.wav')
                  [ImpulsoL4_e30,ImpulsoR4_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e030a.wav')
                  [ImpulsoL5_e30,ImpulsoR5_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e040a.wav')
                  [ImpulsoL6_e30,ImpulsoR6_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e050a.wav')
                  [ImpulsoL7_e30,ImpulsoR7_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e060a.wav')
                  [ImpulsoL8_e30,ImpulsoR8_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e070a.wav')
                  [ImpulsoL9_e30,ImpulsoR9_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e080a.wav')
                  [ImpulsoL10_e30,ImpulsoR10_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e090a.wav')
                  [ImpulsoL11_e30,ImpulsoR11_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e100a.wav')
                  [ImpulsoL12_e30,ImpulsoR12_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e110a.wav')
                  [ImpulsoL13_e30,ImpulsoR13_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e120a.wav')
                  [ImpulsoL14_e30,ImpulsoR14_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e130a.wav')
                  [ImpulsoL15_e30,ImpulsoR15_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e140a.wav')
                  [ImpulsoL16_e30,ImpulsoR16_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e150a.wav')
                  [ImpulsoL17_e30,ImpulsoR17_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e160a.wav')
                  [ImpulsoL18_e30,ImpulsoR18_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e170a.wav')
                  [ImpulsoL19_e30,ImpulsoR19_e30] = leerArchivo(directorio+'TESIS/USB/elev 30/H30e180a.wav')

                  [ImpulsoL1_en10,ImpulsoR1_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e000a.wav')
                  [ImpulsoL2_en10,ImpulsoR2_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e010a.wav')
                  [ImpulsoL3_en10,ImpulsoR3_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e020a.wav')
                  [ImpulsoL4_en10,ImpulsoR4_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e030a.wav')
                  [ImpulsoL5_en10,ImpulsoR5_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e040a.wav')
                  [ImpulsoL6_en10,ImpulsoR6_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e050a.wav')
                  [ImpulsoL7_en10,ImpulsoR7_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e060a.wav')
                  [ImpulsoL8_en10,ImpulsoR8_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e070a.wav')
                  [ImpulsoL9_en10,ImpulsoR9_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e080a.wav')
                  [ImpulsoL10_en10,ImpulsoR10_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e090a.wav')
                  [ImpulsoL11_en10,ImpulsoR11_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e100a.wav')
                  [ImpulsoL12_en10,ImpulsoR12_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e110a.wav')
                  [ImpulsoL13_en10,ImpulsoR13_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e120a.wav')
                  [ImpulsoL14_en10,ImpulsoR14_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e130a.wav')
                  [ImpulsoL15_en10,ImpulsoR15_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e140a.wav')
                  [ImpulsoL16_en10,ImpulsoR16_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e150a.wav')
                  [ImpulsoL17_en10,ImpulsoR17_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e160a.wav')
                  [ImpulsoL18_en10,ImpulsoR18_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e170a.wav')
                  [ImpulsoL19_en10,ImpulsoR19_en10] = leerArchivo(directorio+'TESIS/USB/elev -10/H-10e180a.wav')


                  [ImpulsoL1_en20,ImpulsoR1_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e000a.wav')
                  [ImpulsoL2_en20,ImpulsoR2_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e010a.wav')
                  [ImpulsoL3_en20,ImpulsoR3_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e020a.wav')
                  [ImpulsoL4_en20,ImpulsoR4_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e030a.wav')
                  [ImpulsoL5_en20,ImpulsoR5_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e040a.wav')
                  [ImpulsoL6_en20,ImpulsoR6_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e050a.wav')
                  [ImpulsoL7_en20,ImpulsoR7_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e060a.wav')
                  [ImpulsoL8_en20,ImpulsoR8_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e070a.wav')
                  [ImpulsoL9_en20,ImpulsoR9_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e080a.wav')
                  [ImpulsoL10_en20,ImpulsoR10_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e090a.wav')
                  [ImpulsoL11_en20,ImpulsoR11_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e100a.wav')
                  [ImpulsoL12_en20,ImpulsoR12_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e110a.wav')
                  [ImpulsoL13_en20,ImpulsoR13_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e120a.wav')
                  [ImpulsoL14_en20,ImpulsoR14_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e130a.wav')
                  [ImpulsoL15_en20,ImpulsoR15_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e140a.wav')
                  [ImpulsoL16_en20,ImpulsoR16_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e150a.wav')
                  [ImpulsoL17_en20,ImpulsoR17_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e160a.wav')
                  [ImpulsoL18_en20,ImpulsoR18_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e170a.wav')
                  [ImpulsoL19_en20,ImpulsoR19_en20] = leerArchivo(directorio+'TESIS/USB/elev -20/H-20e180a.wav')
                  

                  [ImpulsoL1_en30,ImpulsoR1_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e000a.wav')
                  [ImpulsoL2_en30,ImpulsoR2_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e010a.wav')
                  [ImpulsoL3_en30,ImpulsoR3_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e020a.wav')
                  [ImpulsoL4_en30,ImpulsoR4_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e030a.wav')
                  [ImpulsoL5_en30,ImpulsoR5_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e040a.wav')
                  [ImpulsoL6_en30,ImpulsoR6_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e050a.wav')
                  [ImpulsoL7_en30,ImpulsoR7_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e060a.wav')
                  [ImpulsoL8_en30,ImpulsoR8_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e070a.wav')
                  [ImpulsoL9_en30,ImpulsoR9_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e080a.wav')
                  [ImpulsoL10_en30,ImpulsoR10_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e090a.wav')
                  [ImpulsoL11_en30,ImpulsoR11_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e100a.wav')
                  [ImpulsoL12_en30,ImpulsoR12_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e110a.wav')
                  [ImpulsoL13_en30,ImpulsoR13_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e120a.wav')
                  [ImpulsoL14_en30,ImpulsoR14_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e130a.wav')
                  [ImpulsoL15_en30,ImpulsoR15_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e140a.wav')
                  [ImpulsoL16_en30,ImpulsoR16_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e150a.wav')
                  [ImpulsoL17_en30,ImpulsoR17_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e160a.wav')
                  [ImpulsoL18_en30,ImpulsoR18_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e170a.wav')
                  [ImpulsoL19_en30,ImpulsoR19_en30] = leerArchivo(directorio+'TESIS/USB/elev -30/H-30e180a.wav')
                  
                  
                  ImpulsoR1_e0 = Comparacion(ImpulsoR1_e0,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_e0 = Comparacion(ImpulsoR2_e0,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_e0 = Comparacion(ImpulsoR3_e0,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_e0 = Comparacion(ImpulsoR4_e0,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_e0 = Comparacion(ImpulsoR5_e0,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_e0 = Comparacion(ImpulsoR6_e0,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_e0 = Comparacion(ImpulsoR7_e0,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_e0 = Comparacion(ImpulsoR8_e0,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_e0 = Comparacion(ImpulsoR9_e0,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_e0 = Comparacion(ImpulsoR10_e0,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_e0 = Comparacion(ImpulsoR11_e0,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_e0 = Comparacion(ImpulsoR12_e0,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_e0 = Comparacion(ImpulsoR13_e0,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_e0 = Comparacion(ImpulsoR14_e0,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_e0 = Comparacion(ImpulsoR15_e0,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_e0 = Comparacion(ImpulsoR16_e0,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_e0 = Comparacion(ImpulsoR17_e0,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_e0 = Comparacion(ImpulsoR18_e0,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_e0 = Comparacion(ImpulsoR19_e0,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_e10 = Comparacion(ImpulsoR1_e10,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_e10 = Comparacion(ImpulsoR2_e10,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_e10 = Comparacion(ImpulsoR3_e10,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_e10 = Comparacion(ImpulsoR4_e10,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_e10 = Comparacion(ImpulsoR5_e10,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_e10 = Comparacion(ImpulsoR6_e10,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_e10 = Comparacion(ImpulsoR7_e10,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_e10 = Comparacion(ImpulsoR8_e10,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_e10 = Comparacion(ImpulsoR9_e10,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_e10 = Comparacion(ImpulsoR10_e10,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_e10 = Comparacion(ImpulsoR11_e10,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_e10 = Comparacion(ImpulsoR12_e10,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_e10 = Comparacion(ImpulsoR13_e10,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_e10 = Comparacion(ImpulsoR14_e10,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_e10 = Comparacion(ImpulsoR15_e10,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_e10 = Comparacion(ImpulsoR16_e10,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_e10 = Comparacion(ImpulsoR17_e10,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_e10 = Comparacion(ImpulsoR18_e10,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_e10 = Comparacion(ImpulsoR19_e10,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_e20 = Comparacion(ImpulsoR1_e20,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_e20 = Comparacion(ImpulsoR2_e20,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_e20 = Comparacion(ImpulsoR3_e20,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_e20 = Comparacion(ImpulsoR4_e20,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_e20 = Comparacion(ImpulsoR5_e20,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_e20 = Comparacion(ImpulsoR6_e20,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_e20 = Comparacion(ImpulsoR7_e20,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_e20 = Comparacion(ImpulsoR8_e20,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_e20 = Comparacion(ImpulsoR9_e20,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_e20 = Comparacion(ImpulsoR10_e20,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_e20 = Comparacion(ImpulsoR11_e20,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_e20 = Comparacion(ImpulsoR12_e20,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_e20 = Comparacion(ImpulsoR13_e20,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_e20 = Comparacion(ImpulsoR14_e20,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_e20 = Comparacion(ImpulsoR15_e20,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_e20 = Comparacion(ImpulsoR16_e20,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_e20 = Comparacion(ImpulsoR17_e20,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_e20 = Comparacion(ImpulsoR18_e20,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_e20 = Comparacion(ImpulsoR19_e20,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_e30 = Comparacion(ImpulsoR1_e30,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_e30 = Comparacion(ImpulsoR2_e30,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_e30 = Comparacion(ImpulsoR3_e30,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_e30 = Comparacion(ImpulsoR4_e30,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_e30 = Comparacion(ImpulsoR5_e30,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_e30 = Comparacion(ImpulsoR6_e30,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_e30 = Comparacion(ImpulsoR7_e30,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_e30 = Comparacion(ImpulsoR8_e30,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_e30 = Comparacion(ImpulsoR9_e30,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_e30 = Comparacion(ImpulsoR10_e30,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_e30 = Comparacion(ImpulsoR11_e30,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_e30 = Comparacion(ImpulsoR12_e30,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_e30 = Comparacion(ImpulsoR13_e30,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_e30 = Comparacion(ImpulsoR14_e30,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_e30 = Comparacion(ImpulsoR15_e30,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_e30 = Comparacion(ImpulsoR16_e30,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_e30 = Comparacion(ImpulsoR17_e30,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_e30 = Comparacion(ImpulsoR18_e30,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_e30 = Comparacion(ImpulsoR19_e30,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_en10 = Comparacion(ImpulsoR1_en10,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_en10 = Comparacion(ImpulsoR2_en10,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_en10 = Comparacion(ImpulsoR3_en10,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_en10 = Comparacion(ImpulsoR4_en10,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_en10 = Comparacion(ImpulsoR5_en10,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_en10 = Comparacion(ImpulsoR6_en10,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_en10 = Comparacion(ImpulsoR7_en10,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_en10 = Comparacion(ImpulsoR8_en10,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_en10 = Comparacion(ImpulsoR9_en10,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_en10 = Comparacion(ImpulsoR10_en10,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_en10 = Comparacion(ImpulsoR11_en10,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_en10 = Comparacion(ImpulsoR12_en10,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_en10 = Comparacion(ImpulsoR13_en10,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_en10 = Comparacion(ImpulsoR14_en10,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_en10 = Comparacion(ImpulsoR15_en10,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_en10 = Comparacion(ImpulsoR16_en10,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_en10 = Comparacion(ImpulsoR17_en10,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_en10 = Comparacion(ImpulsoR18_en10,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_en10 = Comparacion(ImpulsoR19_en10,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_en20 = Comparacion(ImpulsoR1_en20,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_en20 = Comparacion(ImpulsoR2_en20,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_en20 = Comparacion(ImpulsoR3_en20,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_en20 = Comparacion(ImpulsoR4_en20,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_en20 = Comparacion(ImpulsoR5_en20,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_en20 = Comparacion(ImpulsoR6_en20,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_en20 = Comparacion(ImpulsoR7_en20,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_en20 = Comparacion(ImpulsoR8_en20,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_en20 = Comparacion(ImpulsoR9_en20,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_en20 = Comparacion(ImpulsoR10_en20,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_en20 = Comparacion(ImpulsoR11_en20,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_en20 = Comparacion(ImpulsoR12_en20,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_en20 = Comparacion(ImpulsoR13_en20,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_en20 = Comparacion(ImpulsoR14_en20,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_en20 = Comparacion(ImpulsoR15_en20,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_en20 = Comparacion(ImpulsoR16_en20,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_en20 = Comparacion(ImpulsoR17_en20,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_en20 = Comparacion(ImpulsoR18_en20,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_en20 = Comparacion(ImpulsoR19_en20,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_en30 = Comparacion(ImpulsoR1_en30,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_en30 = Comparacion(ImpulsoR2_en30,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_en30 = Comparacion(ImpulsoR3_en30,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_en30 = Comparacion(ImpulsoR4_en30,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_en30 = Comparacion(ImpulsoR5_en30,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_en30 = Comparacion(ImpulsoR6_en30,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_en30 = Comparacion(ImpulsoR7_en30,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_en30 = Comparacion(ImpulsoR8_en30,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_en30 = Comparacion(ImpulsoR9_en30,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_en30 = Comparacion(ImpulsoR10_en30,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_en30 = Comparacion(ImpulsoR11_en30,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_en30 = Comparacion(ImpulsoR12_en30,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_en30 = Comparacion(ImpulsoR13_en30,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_en30 = Comparacion(ImpulsoR14_en30,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_en30 = Comparacion(ImpulsoR15_en30,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_en30 = Comparacion(ImpulsoR16_en30,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_en30 = Comparacion(ImpulsoR17_en30,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_en30 = Comparacion(ImpulsoR18_en30,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_en30 = Comparacion(ImpulsoR19_en30,int(NZref[18]),int(NZ[18]))
                  

                  if Elevacion_Us == 0:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e0, ImpulsoR1_e0,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_e0, ImpulsoR2_e0,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_e0, ImpulsoR3_e0,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_e0, ImpulsoR4_e0,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_e0, ImpulsoR5_e0,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_e0, ImpulsoR6_e0,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_e0, ImpulsoR7_e0,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_e0, ImpulsoR8_e0,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_e0, ImpulsoR9_e0,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_e0, ImpulsoR10_e0,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_e0, ImpulsoR11_e0,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_e0, ImpulsoR12_e0,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_e0, ImpulsoR13_e0,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_e0, ImpulsoR14_e0,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_e0, ImpulsoR15_e0,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_e0, ImpulsoR16_e0,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_e0, ImpulsoR17_e0,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_e0, ImpulsoR18_e0,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_e0, ImpulsoR19_e0,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_e0, ImpulsoL18_e0,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_e0, ImpulsoL17_e0,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_e0, ImpulsoL16_e0,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_e0, ImpulsoL15_e0,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_e0, ImpulsoL14_e0,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_e0, ImpulsoL13_e0,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_e0, ImpulsoL12_e0,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_e0, ImpulsoL11_e0,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_e0, ImpulsoL10_e0,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_e0, ImpulsoL9_e0,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_e0, ImpulsoL8_e0,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_e0, ImpulsoL7_e0,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_e0, ImpulsoL6_e0,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_e0, ImpulsoL5_e0,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_e0, ImpulsoL4_e0,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_e0, ImpulsoL3_e0,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_e0, ImpulsoL2_e0,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e0, ImpulsoR1_e0,Mono)
                              
                  elif Elevacion_Us == 10:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e10, ImpulsoR1_e10,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_e10, ImpulsoR2_e10,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_e10, ImpulsoR3_e10,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_e10, ImpulsoR4_e10,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_e10, ImpulsoR5_e10,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_e10, ImpulsoR6_e10,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_e10, ImpulsoR7_e10,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_e10, ImpulsoR8_e10,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_e10, ImpulsoR9_e10,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_e10, ImpulsoR10_e10,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_e10, ImpulsoR11_e10,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_e10, ImpulsoR12_e10,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_e10 ,ImpulsoR13_e10,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_e10, ImpulsoR14_e10,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_e10, ImpulsoR15_e10,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_e10, ImpulsoR16_e10,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_e10, ImpulsoR17_e10,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_e10, ImpulsoR18_e10,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_e10, ImpulsoR19_e10,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_e10, ImpulsoL18_e10,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_e10, ImpulsoL17_e10,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_e10, ImpulsoL16_e10,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_e10, ImpulsoL15_e10,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_e10, ImpulsoL14_e10,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_e10, ImpulsoL13_e10,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_e10, ImpulsoL12_e10,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_e10, ImpulsoL11_e10,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_e10, ImpulsoL10_e10,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_e10, ImpulsoL9_e10,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_e10, ImpulsoL8_e10,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_e10, ImpulsoL7_e10,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_e10, ImpulsoL6_e10,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_e10, ImpulsoL5_e10,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_e10, ImpulsoL4_e10,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_e10, ImpulsoL3_e10,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_e10, ImpulsoL2_e10,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e10, ImpulsoR1_e10,Mono)

                  elif Elevacion_Us == 20:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e20, ImpulsoR1_e20,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_e20, ImpulsoR2_e20,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_e20, ImpulsoR3_e20,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_e20, ImpulsoR4_e20,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_e20, ImpulsoR5_e20,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_e20, ImpulsoR6_e20,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_e20, ImpulsoR7_e20,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_e20, ImpulsoR8_e20,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_e20, ImpulsoR9_e20,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_e20, ImpulsoR10_e20,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_e20, ImpulsoR11_e20,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_e20, ImpulsoR12_e20,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_e20 ,ImpulsoR13_e20,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_e20, ImpulsoR14_e20,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_e20, ImpulsoR15_e20,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_e20, ImpulsoR16_e20,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_e20, ImpulsoR17_e20,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_e20, ImpulsoR18_e20,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_e20, ImpulsoR19_e20,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_e20, ImpulsoL18_e20,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_e20, ImpulsoL17_e20,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_e20, ImpulsoL16_e20,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_e20, ImpulsoL15_e20,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_e20, ImpulsoL14_e20,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_e20, ImpulsoL13_e20,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_e20, ImpulsoL12_e20,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_e20, ImpulsoL11_e20,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_e20, ImpulsoL10_e20,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_e20, ImpulsoL9_e20,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_e20, ImpulsoL8_e20,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_e20, ImpulsoL7_e20,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_e20, ImpulsoL6_e20,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_e20, ImpulsoL5_e20,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_e20, ImpulsoL4_e20,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_e20, ImpulsoL3_e20,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_e20, ImpulsoL2_e20,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e20, ImpulsoR1_e20,Mono)

                  elif Elevacion_Us == 30:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e30, ImpulsoR1_e30,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_e30, ImpulsoR2_e30,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_e30, ImpulsoR3_e30,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_e30, ImpulsoR4_e30,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_e30, ImpulsoR5_e30,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_e30, ImpulsoR6_e30,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_e30, ImpulsoR7_e30,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_e30, ImpulsoR8_e30,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_e30, ImpulsoR9_e30,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_e30, ImpulsoR10_e30,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_e30, ImpulsoR11_e30,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_e30, ImpulsoR12_e30,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_e30 ,ImpulsoR13_e30,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_e30, ImpulsoR14_e30,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_e30, ImpulsoR15_e30,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_e30, ImpulsoR16_e30,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_e30, ImpulsoR17_e30,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_e30, ImpulsoR18_e30,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_e30, ImpulsoR19_e30,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_e30, ImpulsoL18_e30,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_e30, ImpulsoL17_e30,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_e30, ImpulsoL16_e30,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_e30, ImpulsoL15_e30,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_e30, ImpulsoL14_e30,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_e30, ImpulsoL13_e30,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_e30, ImpulsoL12_e30,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_e30, ImpulsoL11_e30,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_e30, ImpulsoL10_e30,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_e30, ImpulsoL9_e30,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_e30, ImpulsoL8_e30,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_e30, ImpulsoL7_e30,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_e30, ImpulsoL6_e30,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_e30, ImpulsoL5_e30,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_e30, ImpulsoL4_e30,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_e30, ImpulsoL3_e30,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_e30, ImpulsoL2_e30,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e30, ImpulsoR1_e30,Mono)

                  elif Elevacion_Us == -10:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en10, ImpulsoR1_en10,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_en10, ImpulsoR2_en10,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_en10, ImpulsoR3_en10,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_en10, ImpulsoR4_en10,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_en10, ImpulsoR5_en10,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_en10, ImpulsoR6_en10,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_en10, ImpulsoR7_en10,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_en10, ImpulsoR8_en10,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_en10, ImpulsoR9_en10,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_en10, ImpulsoR10_en10,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_en10, ImpulsoR11_en10,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_en10, ImpulsoR12_en10,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_en10 ,ImpulsoR13_en10,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_en10, ImpulsoR14_en10,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_en10, ImpulsoR15_en10,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_en10, ImpulsoR16_en10,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_en10, ImpulsoR17_en10,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_en10, ImpulsoR18_en10,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_en10, ImpulsoR19_en10,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_en10, ImpulsoL18_en10,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_en10, ImpulsoL17_en10,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_en10, ImpulsoL16_en10,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_en10, ImpulsoL15_en10,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_en10, ImpulsoL14_en10,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_en10, ImpulsoL13_en10,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_en10, ImpulsoL12_en10,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_en10, ImpulsoL11_en10,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_en10, ImpulsoL10_en10,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_en10, ImpulsoL9_en10,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_en10, ImpulsoL8_en10,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_en10, ImpulsoL7_en10,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_en10, ImpulsoL6_en10,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_en10, ImpulsoL5_en10,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_en10, ImpulsoL4_en10,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_en10, ImpulsoL3_en10,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_en10, ImpulsoL2_en10,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en10, ImpulsoR1_en10,Mono)

                  elif Elevacion_Us == -20:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en20, ImpulsoR1_en20,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_en20, ImpulsoR2_en20,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_en20, ImpulsoR3_en20,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_en20, ImpulsoR4_en20,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_en20, ImpulsoR5_en20,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_en20, ImpulsoR6_en20,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_en20, ImpulsoR7_en20,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_en20, ImpulsoR8_en20,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_en20, ImpulsoR9_en20,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_en20, ImpulsoR10_en20,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_en20, ImpulsoR11_en20,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_en20, ImpulsoR12_en20,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_en20 ,ImpulsoR13_en20,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_en20, ImpulsoR14_en20,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_en20, ImpulsoR15_en20,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_en20, ImpulsoR16_en20,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_en20, ImpulsoR17_en20,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_en20, ImpulsoR18_en20,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_en20, ImpulsoR19_en20,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_en20, ImpulsoL18_en20,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_en20, ImpulsoL17_en20,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_en20, ImpulsoL16_en20,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_en20, ImpulsoL15_en20,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_en20, ImpulsoL14_en20,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_en20, ImpulsoL13_en20,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_en20, ImpulsoL12_en20,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_en20, ImpulsoL11_en20,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_en20, ImpulsoL10_en20,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_en20, ImpulsoL9_en20,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_en20, ImpulsoL8_en20,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_en20, ImpulsoL7_en20,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_en20, ImpulsoL6_en20,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_en20, ImpulsoL5_en20,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_en20, ImpulsoL4_en20,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_en20, ImpulsoL3_en20,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_en20, ImpulsoL2_en20,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en20, ImpulsoR1_en20,Mono)

                  elif Elevacion_Us == -30:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en30, ImpulsoR1_en30,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_en30, ImpulsoR2_en30,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_en30, ImpulsoR3_en30,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_en30, ImpulsoR4_en30,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_en30, ImpulsoR5_en30,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_en30, ImpulsoR6_en30,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_en30, ImpulsoR7_en30,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_en30, ImpulsoR8_en30,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_en30, ImpulsoR9_en30,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_en30, ImpulsoR10_en30,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_en30, ImpulsoR11_en30,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_en30, ImpulsoR12_en30,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_en30 ,ImpulsoR13_en30,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_en30, ImpulsoR14_en30,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_en30, ImpulsoR15_en30,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_en30, ImpulsoR16_en30,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_en30, ImpulsoR17_en30,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_en30, ImpulsoR18_en30,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_en30, ImpulsoR19_en30,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_en30, ImpulsoL18_en30,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_en30, ImpulsoL17_en30,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_en30, ImpulsoL16_en30,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_en30, ImpulsoL15_en30,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_en30, ImpulsoL14_en30,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_en30, ImpulsoL13_en30,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_en30, ImpulsoL12_en30,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_en30, ImpulsoL11_en30,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_en30, ImpulsoL10_en30,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_en30, ImpulsoL9_en30,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_en30, ImpulsoL8_en30,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_en30, ImpulsoL7_en30,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_en30, ImpulsoL6_en30,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_en30, ImpulsoL5_en30,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_en30, ImpulsoL4_en30,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_en30, ImpulsoL3_en30,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_en30, ImpulsoL2_en30,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en30, ImpulsoR1_en30,Mono)
                  
            elif self.radioButton_2.isChecked():

                  ref = [0.0, 9.694255196424984e-05, 0.00019241607113904682, 0.00028499616055287913, 0.00037334633863337583, 0.0004562586475235908, 0.0005326903562702303, 0.000601795643676021, 0.0006629512981487833, 0.0007157756536702993, 0.0006629512981487833, 0.000601795643676021, 0.0005326903562702302, 0.0004562586475235908, 0.0003733463386333759, 0.00028499616055287913, 0.00019241607113904663, 9.694255196424977e-05, 0]
                  
                  for i in range(len(ref)):
                        x = ref[i]/T
                        NZref.append(x)

                  for i in range(len(DIT)):
                        x = DIT[i]/T
                        NZ.append(x)

                  [ImpulsoL1_e0,ImpulsoR1_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e000a.wav')
                  [ImpulsoL2_e0,ImpulsoR2_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e010a.wav')
                  [ImpulsoL3_e0,ImpulsoR3_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e020a.wav')
                  [ImpulsoL4_e0,ImpulsoR4_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e030a.wav')
                  [ImpulsoL5_e0,ImpulsoR5_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e040a.wav')
                  [ImpulsoL6_e0,ImpulsoR6_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e050a.wav')
                  [ImpulsoL7_e0,ImpulsoR7_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e060a.wav')
                  [ImpulsoL8_e0,ImpulsoR8_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e070a.wav')
                  [ImpulsoL9_e0,ImpulsoR9_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e080a.wav')
                  [ImpulsoL10_e0,ImpulsoR10_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e090a.wav')
                  [ImpulsoL11_e0,ImpulsoR11_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e100a.wav')
                  [ImpulsoL12_e0,ImpulsoR12_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e110a.wav')
                  [ImpulsoL13_e0,ImpulsoR13_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e120a.wav')
                  [ImpulsoL14_e0,ImpulsoR14_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e130a.wav')
                  [ImpulsoL15_e0,ImpulsoR15_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e140a.wav')
                  [ImpulsoL16_e0,ImpulsoR16_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e150a.wav')
                  [ImpulsoL17_e0,ImpulsoR17_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e160a.wav')
                  [ImpulsoL18_e0,ImpulsoR18_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e170a.wav')
                  [ImpulsoL19_e0,ImpulsoR19_e0] = leerArchivo(directorio+'TESIS/MIT/elev0/H0e180a.wav')

                  [ImpulsoL1_e10,ImpulsoR1_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e000a.wav')
                  [ImpulsoL2_e10,ImpulsoR2_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e010a.wav')
                  [ImpulsoL3_e10,ImpulsoR3_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e020a.wav')
                  [ImpulsoL4_e10,ImpulsoR4_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e030a.wav')
                  [ImpulsoL5_e10,ImpulsoR5_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e040a.wav')
                  [ImpulsoL6_e10,ImpulsoR6_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e050a.wav')
                  [ImpulsoL7_e10,ImpulsoR7_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e060a.wav')
                  [ImpulsoL8_e10,ImpulsoR8_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e070a.wav')
                  [ImpulsoL9_e10,ImpulsoR9_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e080a.wav')
                  [ImpulsoL10_e10,ImpulsoR10_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e090a.wav')
                  [ImpulsoL11_e10,ImpulsoR11_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e100a.wav')
                  [ImpulsoL12_e10,ImpulsoR12_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e110a.wav')
                  [ImpulsoL13_e10,ImpulsoR13_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e120a.wav')
                  [ImpulsoL14_e10,ImpulsoR14_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e130a.wav')
                  [ImpulsoL15_e10,ImpulsoR15_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e140a.wav')
                  [ImpulsoL16_e10,ImpulsoR16_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e150a.wav')
                  [ImpulsoL17_e10,ImpulsoR17_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e160a.wav')
                  [ImpulsoL18_e10,ImpulsoR18_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e170a.wav')
                  [ImpulsoL19_e10,ImpulsoR19_e10] = leerArchivo(directorio+'TESIS/MIT/elev10/H10e180a.wav')
                  
                  [ImpulsoL1_e20,ImpulsoR1_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e000a.wav')
                  [ImpulsoL2_e20,ImpulsoR2_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e010a.wav')
                  [ImpulsoL3_e20,ImpulsoR3_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e020a.wav')
                  [ImpulsoL4_e20,ImpulsoR4_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e030a.wav')
                  [ImpulsoL5_e20,ImpulsoR5_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e040a.wav')
                  [ImpulsoL6_e20,ImpulsoR6_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e050a.wav')
                  [ImpulsoL7_e20,ImpulsoR7_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e060a.wav')
                  [ImpulsoL8_e20,ImpulsoR8_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e070a.wav')
                  [ImpulsoL9_e20,ImpulsoR9_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e080a.wav')
                  [ImpulsoL10_e20,ImpulsoR10_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e090a.wav')
                  [ImpulsoL11_e20,ImpulsoR11_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e100a.wav')
                  [ImpulsoL12_e20,ImpulsoR12_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e110a.wav')
                  [ImpulsoL13_e20,ImpulsoR13_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e120a.wav')
                  [ImpulsoL14_e20,ImpulsoR14_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e130a.wav')
                  [ImpulsoL15_e20,ImpulsoR15_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e140a.wav')
                  [ImpulsoL16_e20,ImpulsoR16_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e150a.wav')
                  [ImpulsoL17_e20,ImpulsoR17_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e160a.wav')
                  [ImpulsoL18_e20,ImpulsoR18_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e170a.wav')
                  [ImpulsoL19_e20,ImpulsoR19_e20] = leerArchivo(directorio+'TESIS/MIT/elev20/H20e180a.wav')
                
                  [ImpulsoL1_e30,ImpulsoR1_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e000a.wav')
                  [ImpulsoL2_e30,ImpulsoR2_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e012a.wav')
                  [ImpulsoL3_e30,ImpulsoR3_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e024a.wav')
                  [ImpulsoL4_e30,ImpulsoR4_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e030a.wav')
                  [ImpulsoL5_e30,ImpulsoR5_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e042a.wav')
                  [ImpulsoL6_e30,ImpulsoR6_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e054a.wav')
                  [ImpulsoL7_e30,ImpulsoR7_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e060a.wav')
                  [ImpulsoL8_e30,ImpulsoR8_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e072a.wav')
                  [ImpulsoL9_e30,ImpulsoR9_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e084a.wav')
                  [ImpulsoL10_e30,ImpulsoR10_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e090a.wav')
                  [ImpulsoL11_e30,ImpulsoR11_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e102a.wav')
                  [ImpulsoL12_e30,ImpulsoR12_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e114a.wav')
                  [ImpulsoL13_e30,ImpulsoR13_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e120a.wav')
                  [ImpulsoL14_e30,ImpulsoR14_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e132a.wav')
                  [ImpulsoL15_e30,ImpulsoR15_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e144a.wav')
                  [ImpulsoL16_e30,ImpulsoR16_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e150a.wav')
                  [ImpulsoL17_e30,ImpulsoR17_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e162a.wav')
                  [ImpulsoL18_e30,ImpulsoR18_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e174a.wav')
                  [ImpulsoL19_e30,ImpulsoR19_e30] = leerArchivo(directorio+'TESIS/MIT/elev30/H30e180a.wav')

                  [ImpulsoL1_en10,ImpulsoR1_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e000a.wav')
                  [ImpulsoL2_en10,ImpulsoR2_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e010a.wav')
                  [ImpulsoL3_en10,ImpulsoR3_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e020a.wav')
                  [ImpulsoL4_en10,ImpulsoR4_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e030a.wav')
                  [ImpulsoL5_en10,ImpulsoR5_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e040a.wav')
                  [ImpulsoL6_en10,ImpulsoR6_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e050a.wav')
                  [ImpulsoL7_en10,ImpulsoR7_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e060a.wav')
                  [ImpulsoL8_en10,ImpulsoR8_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e070a.wav')
                  [ImpulsoL9_en10,ImpulsoR9_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e080a.wav')
                  [ImpulsoL10_en10,ImpulsoR10_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e090a.wav')
                  [ImpulsoL11_en10,ImpulsoR11_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e100a.wav')
                  [ImpulsoL12_en10,ImpulsoR12_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e110a.wav')
                  [ImpulsoL13_en10,ImpulsoR13_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e120a.wav')
                  [ImpulsoL14_en10,ImpulsoR14_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e130a.wav')
                  [ImpulsoL15_en10,ImpulsoR15_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e140a.wav')
                  [ImpulsoL16_en10,ImpulsoR16_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e150a.wav')
                  [ImpulsoL17_en10,ImpulsoR17_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e160a.wav')
                  [ImpulsoL18_en10,ImpulsoR18_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e170a.wav')
                  [ImpulsoL19_en10,ImpulsoR19_en10] = leerArchivo(directorio+'TESIS/MIT/elev-10/H-10e180a.wav')
                  
                  [ImpulsoL1_en20,ImpulsoR1_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e000a.wav')
                  [ImpulsoL2_en20,ImpulsoR2_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e010a.wav')
                  [ImpulsoL3_en20,ImpulsoR3_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e020a.wav')
                  [ImpulsoL4_en20,ImpulsoR4_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e030a.wav')
                  [ImpulsoL5_en20,ImpulsoR5_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e040a.wav')
                  [ImpulsoL6_en20,ImpulsoR6_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e050a.wav')
                  [ImpulsoL7_en20,ImpulsoR7_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e060a.wav')
                  [ImpulsoL8_en20,ImpulsoR8_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e070a.wav')
                  [ImpulsoL9_en20,ImpulsoR9_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e080a.wav')
                  [ImpulsoL10_en20,ImpulsoR10_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e090a.wav')
                  [ImpulsoL11_en20,ImpulsoR11_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e100a.wav')
                  [ImpulsoL12_en20,ImpulsoR12_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e110a.wav')
                  [ImpulsoL13_en20,ImpulsoR13_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e120a.wav')
                  [ImpulsoL14_en20,ImpulsoR14_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e130a.wav')
                  [ImpulsoL15_en20,ImpulsoR15_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e140a.wav')
                  [ImpulsoL16_en20,ImpulsoR16_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e150a.wav')
                  [ImpulsoL17_en20,ImpulsoR17_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e160a.wav')
                  [ImpulsoL18_en20,ImpulsoR18_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e170a.wav')
                  [ImpulsoL19_en20,ImpulsoR19_en20] = leerArchivo(directorio+'TESIS/MIT/elev-20/H-20e180a.wav')
                
                  [ImpulsoL1_en30,ImpulsoR1_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e000a.wav')
                  [ImpulsoL2_en30,ImpulsoR2_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e012a.wav')
                  [ImpulsoL3_en30,ImpulsoR3_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e024a.wav')
                  [ImpulsoL4_en30,ImpulsoR4_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e030a.wav')
                  [ImpulsoL5_en30,ImpulsoR5_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e042a.wav')
                  [ImpulsoL6_en30,ImpulsoR6_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e054a.wav')
                  [ImpulsoL7_en30,ImpulsoR7_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e060a.wav')
                  [ImpulsoL8_en30,ImpulsoR8_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e072a.wav')
                  [ImpulsoL9_en30,ImpulsoR9_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e084a.wav')
                  [ImpulsoL10_en30,ImpulsoR10_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e090a.wav')
                  [ImpulsoL11_en30,ImpulsoR11_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e102a.wav')
                  [ImpulsoL12_en30,ImpulsoR12_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e114a.wav')
                  [ImpulsoL13_en30,ImpulsoR13_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e120a.wav')
                  [ImpulsoL14_en30,ImpulsoR14_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e132a.wav')
                  [ImpulsoL15_en30,ImpulsoR15_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e144a.wav')
                  [ImpulsoL16_en30,ImpulsoR16_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e150a.wav')
                  [ImpulsoL17_en30,ImpulsoR17_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e162a.wav')
                  [ImpulsoL18_en30,ImpulsoR18_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e174a.wav')
                  [ImpulsoL19_en30,ImpulsoR19_en30] = leerArchivo(directorio+'TESIS/MIT/elev-30/H-30e180a.wav')

                  ImpulsoR1_e0 = Comparacion(ImpulsoR1_e0,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_e0 = Comparacion(ImpulsoR2_e0,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_e0 = Comparacion(ImpulsoR3_e0,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_e0 = Comparacion(ImpulsoR4_e0,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_e0 = Comparacion(ImpulsoR5_e0,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_e0 = Comparacion(ImpulsoR6_e0,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_e0 = Comparacion(ImpulsoR7_e0,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_e0 = Comparacion(ImpulsoR8_e0,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_e0 = Comparacion(ImpulsoR9_e0,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_e0 = Comparacion(ImpulsoR10_e0,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_e0 = Comparacion(ImpulsoR11_e0,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_e0 = Comparacion(ImpulsoR12_e0,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_e0 = Comparacion(ImpulsoR13_e0,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_e0 = Comparacion(ImpulsoR14_e0,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_e0 = Comparacion(ImpulsoR15_e0,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_e0 = Comparacion(ImpulsoR16_e0,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_e0 = Comparacion(ImpulsoR17_e0,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_e0 = Comparacion(ImpulsoR18_e0,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_e0 = Comparacion(ImpulsoR19_e0,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_e10 = Comparacion(ImpulsoR1_e10,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_e10 = Comparacion(ImpulsoR2_e10,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_e10 = Comparacion(ImpulsoR3_e10,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_e10 = Comparacion(ImpulsoR4_e10,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_e10 = Comparacion(ImpulsoR5_e10,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_e10 = Comparacion(ImpulsoR6_e10,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_e10 = Comparacion(ImpulsoR7_e10,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_e10 = Comparacion(ImpulsoR8_e10,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_e10 = Comparacion(ImpulsoR9_e10,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_e10 = Comparacion(ImpulsoR10_e10,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_e10 = Comparacion(ImpulsoR11_e10,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_e10 = Comparacion(ImpulsoR12_e10,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_e10 = Comparacion(ImpulsoR13_e10,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_e10 = Comparacion(ImpulsoR14_e10,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_e10 = Comparacion(ImpulsoR15_e10,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_e10 = Comparacion(ImpulsoR16_e10,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_e10 = Comparacion(ImpulsoR17_e10,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_e10 = Comparacion(ImpulsoR18_e10,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_e10 = Comparacion(ImpulsoR19_e10,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_e20 = Comparacion(ImpulsoR1_e20,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_e20 = Comparacion(ImpulsoR2_e20,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_e20 = Comparacion(ImpulsoR3_e20,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_e20 = Comparacion(ImpulsoR4_e20,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_e20 = Comparacion(ImpulsoR5_e20,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_e20 = Comparacion(ImpulsoR6_e20,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_e20 = Comparacion(ImpulsoR7_e20,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_e20 = Comparacion(ImpulsoR8_e20,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_e20 = Comparacion(ImpulsoR9_e20,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_e20 = Comparacion(ImpulsoR10_e20,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_e20 = Comparacion(ImpulsoR11_e20,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_e20 = Comparacion(ImpulsoR12_e20,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_e20 = Comparacion(ImpulsoR13_e20,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_e20 = Comparacion(ImpulsoR14_e20,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_e20 = Comparacion(ImpulsoR15_e20,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_e20 = Comparacion(ImpulsoR16_e20,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_e20 = Comparacion(ImpulsoR17_e20,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_e20 = Comparacion(ImpulsoR18_e20,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_e20 = Comparacion(ImpulsoR19_e20,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_e30 = Comparacion(ImpulsoR1_e30,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_e30 = Comparacion(ImpulsoR2_e30,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_e30 = Comparacion(ImpulsoR3_e30,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_e30 = Comparacion(ImpulsoR4_e30,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_e30 = Comparacion(ImpulsoR5_e30,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_e30 = Comparacion(ImpulsoR6_e30,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_e30 = Comparacion(ImpulsoR7_e30,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_e30 = Comparacion(ImpulsoR8_e30,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_e30 = Comparacion(ImpulsoR9_e30,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_e30 = Comparacion(ImpulsoR10_e30,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_e30 = Comparacion(ImpulsoR11_e30,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_e30 = Comparacion(ImpulsoR12_e30,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_e30 = Comparacion(ImpulsoR13_e30,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_e30 = Comparacion(ImpulsoR14_e30,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_e30 = Comparacion(ImpulsoR15_e30,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_e30 = Comparacion(ImpulsoR16_e30,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_e30 = Comparacion(ImpulsoR17_e30,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_e30 = Comparacion(ImpulsoR18_e30,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_e30 = Comparacion(ImpulsoR19_e30,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_en10 = Comparacion(ImpulsoR1_en10,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_en10 = Comparacion(ImpulsoR2_en10,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_en10 = Comparacion(ImpulsoR3_en10,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_en10 = Comparacion(ImpulsoR4_en10,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_en10 = Comparacion(ImpulsoR5_en10,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_en10 = Comparacion(ImpulsoR6_en10,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_en10 = Comparacion(ImpulsoR7_en10,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_en10 = Comparacion(ImpulsoR8_en10,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_en10 = Comparacion(ImpulsoR9_en10,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_en10 = Comparacion(ImpulsoR10_en10,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_en10 = Comparacion(ImpulsoR11_en10,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_en10 = Comparacion(ImpulsoR12_en10,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_en10 = Comparacion(ImpulsoR13_en10,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_en10 = Comparacion(ImpulsoR14_en10,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_en10 = Comparacion(ImpulsoR15_en10,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_en10 = Comparacion(ImpulsoR16_en10,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_en10 = Comparacion(ImpulsoR17_en10,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_en10 = Comparacion(ImpulsoR18_en10,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_en10 = Comparacion(ImpulsoR19_en10,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_en20 = Comparacion(ImpulsoR1_en20,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_en20 = Comparacion(ImpulsoR2_en20,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_en20 = Comparacion(ImpulsoR3_en20,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_en20 = Comparacion(ImpulsoR4_en20,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_en20 = Comparacion(ImpulsoR5_en20,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_en20 = Comparacion(ImpulsoR6_en20,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_en20 = Comparacion(ImpulsoR7_en20,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_en20 = Comparacion(ImpulsoR8_en20,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_en20 = Comparacion(ImpulsoR9_en20,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_en20 = Comparacion(ImpulsoR10_en20,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_en20 = Comparacion(ImpulsoR11_en20,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_en20 = Comparacion(ImpulsoR12_en20,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_en20 = Comparacion(ImpulsoR13_en20,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_en20 = Comparacion(ImpulsoR14_en20,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_en20 = Comparacion(ImpulsoR15_en20,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_en20 = Comparacion(ImpulsoR16_en20,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_en20 = Comparacion(ImpulsoR17_en20,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_en20 = Comparacion(ImpulsoR18_en20,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_en20 = Comparacion(ImpulsoR19_en20,int(NZref[18]),int(NZ[18]))

                  ImpulsoR1_en30 = Comparacion(ImpulsoR1_en30,int(NZref[0]),int(NZ[0]))
                  ImpulsoR2_en30 = Comparacion(ImpulsoR2_en30,int(NZref[1]),int(NZ[1]))
                  ImpulsoR3_en30 = Comparacion(ImpulsoR3_en30,int(NZref[2]),int(NZ[2]))
                  ImpulsoR4_en30 = Comparacion(ImpulsoR4_en30,int(NZref[3]),int(NZ[3]))
                  ImpulsoR5_en30 = Comparacion(ImpulsoR5_en30,int(NZref[4]),int(NZ[4]))
                  ImpulsoR6_en30 = Comparacion(ImpulsoR6_en30,int(NZref[5]),int(NZ[5]))
                  ImpulsoR7_en30 = Comparacion(ImpulsoR7_en30,int(NZref[6]),int(NZ[6]))
                  ImpulsoR8_en30 = Comparacion(ImpulsoR8_en30,int(NZref[7]),int(NZ[7]))
                  ImpulsoR9_en30 = Comparacion(ImpulsoR9_en30,int(NZref[8]),int(NZ[8]))
                  ImpulsoR10_en30 = Comparacion(ImpulsoR10_en30,int(NZref[9]),int(NZ[9]))
                  ImpulsoR11_en30 = Comparacion(ImpulsoR11_en30,int(NZref[10]),int(NZ[10]))
                  ImpulsoR12_en30 = Comparacion(ImpulsoR12_en30,int(NZref[11]),int(NZ[11]))
                  ImpulsoR13_en30 = Comparacion(ImpulsoR13_en30,int(NZref[12]),int(NZ[12]))
                  ImpulsoR14_en30 = Comparacion(ImpulsoR14_en30,int(NZref[13]),int(NZ[13]))
                  ImpulsoR15_en30 = Comparacion(ImpulsoR15_en30,int(NZref[14]),int(NZ[14]))
                  ImpulsoR16_en30 = Comparacion(ImpulsoR16_en30,int(NZref[15]),int(NZ[15]))
                  ImpulsoR17_en30 = Comparacion(ImpulsoR17_en30,int(NZref[16]),int(NZ[16]))
                  ImpulsoR18_en30 = Comparacion(ImpulsoR18_en30,int(NZref[17]),int(NZ[17]))
                  ImpulsoR19_en30 = Comparacion(ImpulsoR19_en30,int(NZref[18]),int(NZ[18]))

                  if Elevacion_Us == 0:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e0, ImpulsoR1_e0,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_e0, ImpulsoR2_e0,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_e0, ImpulsoR3_e0,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_e0, ImpulsoR4_e0,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_e0, ImpulsoR5_e0,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_e0, ImpulsoR6_e0,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_e0, ImpulsoR7_e0,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_e0, ImpulsoR8_e0,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_e0, ImpulsoR9_e0,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_e0, ImpulsoR10_e0,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_e0, ImpulsoR11_e0,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_e0, ImpulsoR12_e0,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_e0, ImpulsoR13_e0,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_e0, ImpulsoR14_e0,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_e0, ImpulsoR15_e0,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_e0, ImpulsoR16_e0,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_e0, ImpulsoR17_e0,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_e0, ImpulsoR18_e0,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_e0, ImpulsoR19_e0,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_e0, ImpulsoL18_e0,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_e0, ImpulsoL17_e0,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_e0, ImpulsoL16_e0,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_e0, ImpulsoL15_e0,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_e0, ImpulsoL14_e0,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_e0, ImpulsoL13_e0,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_e0, ImpulsoL12_e0,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_e0, ImpulsoL11_e0,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_e0, ImpulsoL10_e0,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_e0, ImpulsoL9_e0,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_e0, ImpulsoL8_e0,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_e0, ImpulsoL7_e0,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_e0, ImpulsoL6_e0,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_e0, ImpulsoL5_e0,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_e0, ImpulsoL4_e0,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_e0, ImpulsoL3_e0,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_e0, ImpulsoL2_e0,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e0, ImpulsoR1_e0,Mono)
                              
                  elif Elevacion_Us == 10:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e10, ImpulsoR1_e10,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_e10, ImpulsoR2_e10,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_e10, ImpulsoR3_e10,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_e10, ImpulsoR4_e10,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_e10, ImpulsoR5_e10,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_e10, ImpulsoR6_e10,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_e10, ImpulsoR7_e10,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_e10, ImpulsoR8_e10,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_e10, ImpulsoR9_e10,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_e10, ImpulsoR10_e10,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_e10, ImpulsoR11_e10,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_e10, ImpulsoR12_e10,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_e10 ,ImpulsoR13_e10,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_e10, ImpulsoR14_e10,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_e10, ImpulsoR15_e10,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_e10, ImpulsoR16_e10,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_e10, ImpulsoR17_e10,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_e10, ImpulsoR18_e10,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_e10, ImpulsoR19_e10,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_e10, ImpulsoL18_e10,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_e10, ImpulsoL17_e10,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_e10, ImpulsoL16_e10,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_e10, ImpulsoL15_e10,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_e10, ImpulsoL14_e10,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_e10, ImpulsoL13_e10,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_e10, ImpulsoL12_e10,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_e10, ImpulsoL11_e10,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_e10, ImpulsoL10_e10,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_e10, ImpulsoL9_e10,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_e10, ImpulsoL8_e10,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_e10, ImpulsoL7_e10,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_e10, ImpulsoL6_e10,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_e10, ImpulsoL5_e10,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_e10, ImpulsoL4_e10,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_e10, ImpulsoL3_e10,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_e10, ImpulsoL2_e10,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e10, ImpulsoR1_e10,Mono)

                  elif Elevacion_Us == 20:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e20, ImpulsoR1_e20,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_e20, ImpulsoR2_e20,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_e20, ImpulsoR3_e20,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_e20, ImpulsoR4_e20,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_e20, ImpulsoR5_e20,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_e20, ImpulsoR6_e20,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_e20, ImpulsoR7_e20,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_e20, ImpulsoR8_e20,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_e20, ImpulsoR9_e20,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_e20, ImpulsoR10_e20,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_e20, ImpulsoR11_e20,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_e20, ImpulsoR12_e20,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_e20 ,ImpulsoR13_e20,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_e20, ImpulsoR14_e20,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_e20, ImpulsoR15_e20,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_e20, ImpulsoR16_e20,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_e20, ImpulsoR17_e20,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_e20, ImpulsoR18_e20,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_e20, ImpulsoR19_e20,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_e20, ImpulsoL18_e20,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_e20, ImpulsoL17_e20,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_e20, ImpulsoL16_e20,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_e20, ImpulsoL15_e20,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_e20, ImpulsoL14_e20,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_e20, ImpulsoL13_e20,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_e20, ImpulsoL12_e20,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_e20, ImpulsoL11_e20,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_e20, ImpulsoL10_e20,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_e20, ImpulsoL9_e20,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_e20, ImpulsoL8_e20,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_e20, ImpulsoL7_e20,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_e20, ImpulsoL6_e20,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_e20, ImpulsoL5_e20,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_e20, ImpulsoL4_e20,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_e20, ImpulsoL3_e20,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_e20, ImpulsoL2_e20,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e20, ImpulsoR1_e20,Mono)

                  elif Elevacion_Us == 30:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e30, ImpulsoR1_e30,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_e30, ImpulsoR2_e30,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_e30, ImpulsoR3_e30,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_e30, ImpulsoR4_e30,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_e30, ImpulsoR5_e30,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_e30, ImpulsoR6_e30,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_e30, ImpulsoR7_e30,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_e30, ImpulsoR8_e30,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_e30, ImpulsoR9_e30,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_e30, ImpulsoR10_e30,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_e30, ImpulsoR11_e30,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_e30, ImpulsoR12_e30,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_e30 ,ImpulsoR13_e30,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_e30, ImpulsoR14_e30,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_e30, ImpulsoR15_e30,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_e30, ImpulsoR16_e30,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_e30, ImpulsoR17_e30,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_e30, ImpulsoR18_e30,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_e30, ImpulsoR19_e30,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_e30, ImpulsoL18_e30,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_e30, ImpulsoL17_e30,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_e30, ImpulsoL16_e30,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_e30, ImpulsoL15_e30,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_e30, ImpulsoL14_e30,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_e30, ImpulsoL13_e30,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_e30, ImpulsoL12_e30,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_e30, ImpulsoL11_e30,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_e30, ImpulsoL10_e30,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_e30, ImpulsoL9_e30,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_e30, ImpulsoL8_e30,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_e30, ImpulsoL7_e30,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_e30, ImpulsoL6_e30,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_e30, ImpulsoL5_e30,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_e30, ImpulsoL4_e30,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_e30, ImpulsoL3_e30,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_e30, ImpulsoL2_e30,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_e30, ImpulsoR1_e30,Mono)

                  elif Elevacion_Us == -10:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en10, ImpulsoR1_en10,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_en10, ImpulsoR2_en10,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_en10, ImpulsoR3_en10,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_en10, ImpulsoR4_en10,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_en10, ImpulsoR5_en10,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_en10, ImpulsoR6_en10,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_en10, ImpulsoR7_en10,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_en10, ImpulsoR8_en10,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_en10, ImpulsoR9_en10,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_en10, ImpulsoR10_en10,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_en10, ImpulsoR11_en10,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_en10, ImpulsoR12_en10,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_en10 ,ImpulsoR13_en10,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_en10, ImpulsoR14_en10,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_en10, ImpulsoR15_en10,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_en10, ImpulsoR16_en10,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_en10, ImpulsoR17_en10,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_en10, ImpulsoR18_en10,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_en10, ImpulsoR19_en10,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_en10, ImpulsoL18_en10,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_en10, ImpulsoL17_en10,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_en10, ImpulsoL16_en10,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_en10, ImpulsoL15_en10,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_en10, ImpulsoL14_en10,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_en10, ImpulsoL13_en10,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_en10, ImpulsoL12_en10,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_en10, ImpulsoL11_en10,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_en10, ImpulsoL10_en10,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_en10, ImpulsoL9_en10,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_en10, ImpulsoL8_en10,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_en10, ImpulsoL7_en10,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_en10, ImpulsoL6_en10,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_en10, ImpulsoL5_en10,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_en10, ImpulsoL4_en10,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_en10, ImpulsoL3_en10,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_en10, ImpulsoL2_en10,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en10, ImpulsoR1_en10,Mono)

                  elif Elevacion_Us == -20:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en20, ImpulsoR1_en20,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_en20, ImpulsoR2_en20,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_en20, ImpulsoR3_en20,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_en20, ImpulsoR4_en20,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_en20, ImpulsoR5_en20,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_en20, ImpulsoR6_en20,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_en20, ImpulsoR7_en20,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_en20, ImpulsoR8_en20,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_en20, ImpulsoR9_en20,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_en20, ImpulsoR10_en20,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_en20, ImpulsoR11_en20,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_en20, ImpulsoR12_en20,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_en20 ,ImpulsoR13_en20,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_en20, ImpulsoR14_en20,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_en20, ImpulsoR15_en20,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_en20, ImpulsoR16_en20,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_en20, ImpulsoR17_en20,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_en20, ImpulsoR18_en20,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_en20, ImpulsoR19_en20,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_en20, ImpulsoL18_en20,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_en20, ImpulsoL17_en20,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_en20, ImpulsoL16_en20,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_en20, ImpulsoL15_en20,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_en20, ImpulsoL14_en20,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_en20, ImpulsoL13_en20,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_en20, ImpulsoL12_en20,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_en20, ImpulsoL11_en20,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_en20, ImpulsoL10_en20,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_en20, ImpulsoL9_en20,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_en20, ImpulsoL8_en20,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_en20, ImpulsoL7_en20,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_en20, ImpulsoL6_en20,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_en20, ImpulsoL5_en20,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_en20, ImpulsoL4_en20,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_en20, ImpulsoL3_en20,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_en20, ImpulsoL2_en20,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en20, ImpulsoR1_en20,Mono)

                  elif Elevacion_Us == -30:
                        if Azimuth_Us < 5:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en30, ImpulsoR1_en30,Mono)
                        elif Azimuth_Us > 5 and Azimuth_Us < 15:
                              [ConvL,ConvR] = Convolucion(ImpulsoL2_en30, ImpulsoR2_en30,Mono)
                        elif Azimuth_Us > 15 and Azimuth_Us < 25:
                              [ConvL,ConvR] = Convolucion(ImpulsoL3_en30, ImpulsoR3_en30,Mono)
                        elif Azimuth_Us > 25 and Azimuth_Us < 35:
                              [ConvL,ConvR] = Convolucion(ImpulsoL4_en30, ImpulsoR4_en30,Mono)
                        elif Azimuth_Us > 35 and Azimuth_Us < 45:
                              [ConvL,ConvR] = Convolucion(ImpulsoL5_en30, ImpulsoR5_en30,Mono)
                        elif Azimuth_Us > 45 and Azimuth_Us < 55:
                              [ConvL,ConvR] = Convolucion(ImpulsoL6_en30, ImpulsoR6_en30,Mono)
                        elif Azimuth_Us > 55 and Azimuth_Us < 65:
                              [ConvL,ConvR] = Convolucion(ImpulsoL7_en30, ImpulsoR7_en30,Mono)
                        elif Azimuth_Us > 65 and Azimuth_Us < 75:
                              [ConvL,ConvR] = Convolucion(ImpulsoL8_en30, ImpulsoR8_en30,Mono)
                        elif Azimuth_Us > 75 and Azimuth_Us < 85:
                              [ConvL,ConvR] = Convolucion(ImpulsoL9_en30, ImpulsoR9_en30,Mono)
                        elif Azimuth_Us > 85 and Azimuth_Us < 95:
                              [ConvL,ConvR] = Convolucion(ImpulsoL10_en30, ImpulsoR10_en30,Mono)
                        elif Azimuth_Us > 95 and Azimuth_Us < 105:
                              [ConvL,ConvR] = Convolucion(ImpulsoL11_en30, ImpulsoR11_en30,Mono)
                        elif Azimuth_Us > 105 and Azimuth_Us < 115:
                              [ConvL,ConvR] = Convolucion(ImpulsoL12_en30, ImpulsoR12_en30,Mono)
                        elif Azimuth_Us > 115 and Azimuth_Us < 125:
                              [ConvL,ConvR] = Convolucion(ImpulsoL13_en30 ,ImpulsoR13_en30,Mono)
                        elif Azimuth_Us > 125 and Azimuth_Us < 135:
                              [ConvL,ConvR] = Convolucion(ImpulsoL14_en30, ImpulsoR14_en30,Mono)
                        elif Azimuth_Us > 135 and Azimuth_Us < 145:
                              [ConvL,ConvR] = Convolucion(ImpulsoL15_en30, ImpulsoR15_en30,Mono)
                        elif Azimuth_Us > 145 and Azimuth_Us < 155:
                              [ConvL,ConvR] = Convolucion(ImpulsoL16_en30, ImpulsoR16_en30,Mono)
                        elif Azimuth_Us > 155 and Azimuth_Us < 165:
                              [ConvL,ConvR] = Convolucion(ImpulsoL17_en30, ImpulsoR17_en30,Mono)
                        elif Azimuth_Us > 165 and Azimuth_Us < 175:
                              [ConvL,ConvR] = Convolucion(ImpulsoL18_en30, ImpulsoR18_en30,Mono)
                        elif Azimuth_Us > 175 and Azimuth_Us < 185:
                              [ConvL,ConvR] = Convolucion(ImpulsoL19_en30, ImpulsoR19_en30,Mono)
                        elif Azimuth_Us > 185 and Azimuth_Us < 195:
                              [ConvL,ConvR] = Convolucion(ImpulsoR18_en30, ImpulsoL18_en30,Mono)
                        elif Azimuth_Us > 195 and Azimuth_Us < 205:
                              [ConvL,ConvR] = Convolucion(ImpulsoR17_en30, ImpulsoL17_en30,Mono)
                        elif Azimuth_Us > 205 and Azimuth_Us < 215:
                              [ConvL,ConvR] = Convolucion(ImpulsoR16_en30, ImpulsoL16_en30,Mono)
                        elif Azimuth_Us > 215 and Azimuth_Us < 225:
                              [ConvL,ConvR] = Convolucion(ImpulsoR15_en30, ImpulsoL15_en30,Mono)
                        elif Azimuth_Us > 225 and Azimuth_Us < 235:
                              [ConvL,ConvR] = Convolucion(ImpulsoR14_en30, ImpulsoL14_en30,Mono)
                        elif Azimuth_Us > 235 and Azimuth_Us < 245:
                              [ConvL,ConvR] = Convolucion(ImpulsoR13_en30, ImpulsoL13_en30,Mono)
                        elif Azimuth_Us > 245 and Azimuth_Us < 255:
                              [ConvL,ConvR] = Convolucion(ImpulsoR12_en30, ImpulsoL12_en30,Mono)
                        elif Azimuth_Us > 255 and Azimuth_Us < 265:
                              [ConvL,ConvR] = Convolucion(ImpulsoR11_en30, ImpulsoL11_en30,Mono)
                        elif Azimuth_Us > 265 and Azimuth_Us < 275:
                              [ConvL,ConvR] = Convolucion(ImpulsoR10_en30, ImpulsoL10_en30,Mono)
                        elif Azimuth_Us > 275 and Azimuth_Us < 285:
                              [ConvL,ConvR] = Convolucion(ImpulsoR9_en30, ImpulsoL9_en30,Mono)
                        elif Azimuth_Us > 285 and Azimuth_Us < 295:
                              [ConvL,ConvR] = Convolucion(ImpulsoR8_en30, ImpulsoL8_en30,Mono)
                        elif Azimuth_Us > 295 and Azimuth_Us < 305:
                              [ConvL,ConvR] = Convolucion(ImpulsoR7_en30, ImpulsoL7_en30,Mono)
                        elif Azimuth_Us > 305 and Azimuth_Us < 315:
                              [ConvL,ConvR] = Convolucion(ImpulsoR6_en30, ImpulsoL6_en30,Mono)
                        elif Azimuth_Us > 315 and Azimuth_Us < 325:
                              [ConvL,ConvR] = Convolucion(ImpulsoR5_en30, ImpulsoL5_en30,Mono)
                        elif Azimuth_Us > 325 and Azimuth_Us < 335:
                              [ConvL,ConvR] = Convolucion(ImpulsoR4_en30, ImpulsoL4_en30,Mono)
                        elif Azimuth_Us > 335 and Azimuth_Us < 345:
                              [ConvL,ConvR] = Convolucion(ImpulsoR3_en30, ImpulsoL3_en30,Mono)
                        elif Azimuth_Us > 345 and Azimuth_Us < 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoR2_en30, ImpulsoL2_en30,Mono)
                        elif Azimuth_Us > 355:
                              [ConvL,ConvR] = Convolucion(ImpulsoL1_en30, ImpulsoR1_en30,Mono)

                  plt.plot(ConvL)
                  plt.show
                  
      def Exportar_Archivo(self):
            nombre = self.plainTextEdit_2.toPlainText()
            nombre= str(nombre)
            
            Left = []
            Right = []
            [Left,Right] = Normalizar(ConvL,ConvR)
            Revisar_Longitud(Left,Right)
            nuevoCanal = np.array([Left, Right], dtype=np.float32)
            write(nombre+'.wav', 44100, nuevoCanal.T)
                  
app = QApplication(sys.argv)
_ventanaprincipal = VentanaPrincipal()
_ventanaprincipal.show()
app.exec_()
