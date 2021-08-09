# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFolderDestination)
from qgis import processing
import gdal
import numpy as np
from datetime import datetime

class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUTRP = 'INPUTRP'
    GRUPPO = 'GRUPPO'
    INPUTPRE = 'INPUTPRE'
    INPUTRF = 'INPUTRF'
    INPUTFUT = 'INPUTFUT'
    INPUTP = 'INPUTP'
    PIXEL_RES = 'PIXEL_RES'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'SE Protezione idrogeologica'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Protezione idrogeologica')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('SE Torino')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Algoritmo per il calcolo della protezione idrogeologica, nell'ambito del calcolo dei Servizi Ecosistemici per la Città di Torino")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        gruppi = ['1', '2', '3', '4']
        
        double_param = QgsProcessingParameterNumber(
            self.INPUTP,
            self.tr('Pioggia totale [mm]'),
            QgsProcessingParameterNumber.Double,
            55.32
        )
        double_param.setMetadata({'widget_wrapper': { 'decimals': 2 }})
        self.addParameter(double_param)
        
        self.addParameter(
            QgsProcessingParameterEnum(
                self.GRUPPO,
                self.tr('Gruppo idrologico'),
                gruppi,
                defaultValue=''
                )
            )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTRP,
                self.tr('Raster Uso suolo Stato attuale'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.INPUTPRE,
            self.tr('Anno attuale'),
            QgsProcessingParameterNumber.Integer,
            2021
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTRF,
                self.tr('Raster Uso suolo Stato di progetto'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
            self.INPUTFUT,
            self.tr('Anno progetto'),
            QgsProcessingParameterNumber.Integer,
            2030
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.PIXEL_RES,
            self.tr('Risoluzione spaziale raster (m)'),
            QgsProcessingParameterNumber.Integer,
            2
            )
        )


        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                self.tr('Salva nella cartella')
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        gruppi = ['1', '2', '3', '4']
        gruppo_id = self.parameterAsInt(parameters, self.GRUPPO, context)
        rain_tot = self.parameterAsDouble(parameters, self.INPUTP, context)
        # Load present raster
        present_raster = self.parameterAsRasterLayer(parameters, self.INPUTRP, context)
        ds_present = gdal.Open(present_raster.dataProvider().dataSourceUri())
        arr_present = ds_present.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_present[arr_present < 0] = 0

        # Load future raster
        future_raster = self.parameterAsRasterLayer(parameters, self.INPUTRF, context)
        ds_future = gdal.Open(future_raster.dataProvider().dataSourceUri())
        arr_future = ds_future.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_future[arr_future < 0] = 0

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        # SE valore protezione idrogeologica per lucode
        cn_lucode = {}
        cn_lucode[1] = [64, 76, 84, 88]
        cn_lucode[2] = [64, 76, 84, 88]
        cn_lucode[3] = [71, 81, 87, 90]
        cn_lucode[4] = [57, 70, 78, 82]
        cn_lucode[5] = [57, 70, 78, 82]
        cn_lucode[6] = [30, 58, 70, 77]
        cn_lucode[7] = [83, 89, 92, 93]
        cn_lucode[8] = [98, 98, 98, 98]
        cn_lucode[9] = [43, 65, 76, 82]
        cn_lucode[10] = [43, 65, 76, 82]
        cn_lucode[11] = [98, 98, 98, 98]
        cn_lucode[12] = [72, 82, 87, 89]
        cn_lucode[13] = [98, 98, 98, 98]
        cn_lucode[14] = [72, 82, 87, 89]
        cn_lucode[15] = [98, 98, 98, 98]
        cn_lucode[16] = [72, 82, 87, 89]
        cn_lucode[17] = [43, 65, 76, 82]
        cn_lucode[18] = [98, 98, 98, 98]
        cn_lucode[19] = [77, 86, 91, 94]
        cn_lucode[20] = [98, 98, 98, 98]
        cn_lucode[21] = [43, 61, 76, 82]
        cn_lucode[22] = [43, 61, 76, 82]
        cn_lucode[23] = [74, 84, 88, 90]
        cn_lucode[24] = [74, 84, 88, 90]
        cn_lucode[25] = [98, 98, 98, 98]
        cn_lucode[26] = [49, 69, 79, 84]
        cn_lucode[27] = [49, 69, 79, 84]
        cn_lucode[28] = [100, 100, 100, 100]
        cn_lucode[29] = [60, 72, 81, 84]
        cn_lucode[30] = [60, 72, 81, 84]
        cn_lucode[31] = [100, 100, 100, 100]
        cn_lucode[32] = [68, 79, 86, 89]
        cn_lucode[33] = [68, 79, 86, 89]
        cn_lucode[34] = [50, 70, 80, 85]
        cn_lucode[35] = [81, 88, 91, 93]
        cn_lucode[36] = [60, 74, 83, 87]
        cn_lucode[37] = [57, 70, 78, 82]
        cn_lucode[38] = [73, 83, 88, 91]
        cn_lucode[39] = [73, 83, 88, 91]
        cn_lucode[40] = [64, 76, 84, 88]
        cn_lucode[41] = [64, 76, 84, 88]
        cn_lucode[42] = [64, 76, 84, 88]
        cn_lucode[43] = [77, 85, 90, 92]
        cn_lucode[44] = [98, 98, 98, 98]
        cn_lucode[45] = [100, 100, 100, 100]
        cn_lucode[46] = [98, 98, 98, 98]
        cn_lucode[47] = [98, 98, 98, 98]
        cn_lucode[48] = [77, 85, 90, 92]
        cn_lucode[49] = [77, 85, 90, 92]
        cn_lucode[50] = [98, 98, 98, 98]
        cn_lucode[51] = [98, 98, 98, 98]
        cn_lucode[52] = [98, 98, 98, 98]
        cn_lucode[53] = [77, 85, 90, 92]
        cn_lucode[54] = [77, 85, 90, 92]
        cn_lucode[55] = [98, 98, 98, 98]
        cn_lucode[56] = [98, 98, 98, 98]
        cn_lucode[57] = [0, 72, 81, 84]
        cn_lucode[58] = [0, 72, 81, 84]
        cn_lucode[59] = [64, 76, 84, 88]
        cn_lucode[60] = [98, 98, 98, 98]
        cn_lucode[61] = [35, 56, 70, 77]
        cn_lucode[62] = [35, 56, 70, 77]
        cn_lucode[63] = [35, 56, 70, 77]
        cn_lucode[64] = [60, 72, 81, 84]
        cn_lucode[65] = [60, 72, 81, 84]
        cn_lucode[66] = [98, 98, 98, 98]
        cn_lucode[67] = [98, 98, 98, 98]
        cn_lucode[68] = [30, 58, 70, 77]
        cn_lucode[69] = [35, 56, 70, 77]
        cn_lucode[70] = [35, 56, 70, 77]
        cn_lucode[71] = [77, 85, 90, 92]
        cn_lucode[72] = [98, 98, 98, 98]
        cn_lucode[73] = [64, 76, 84, 88]
        cn_lucode[74] = [64, 76, 84, 88]
        cn_lucode[75] = [64, 76, 84, 88]
        cn_lucode[76] = [64, 76, 84, 88]
        cn_lucode[77] = [98, 98, 98, 98]
        cn_lucode[78] = [100, 100, 100, 100]
        cn_lucode[79] = [77, 86, 91, 94]
        cn_lucode[80] = [92, 92, 92, 92]
        cn_lucode[81] = [92, 92, 92, 92]
        cn_lucode[82] = [40, 63, 75, 81]
        cn_lucode[83] = [36, 60, 73, 79]
        cn_lucode[84] = [36, 60, 73, 79]
        cn_lucode[85] = [45, 66, 77, 83]
        cn_lucode[86] = [45, 66, 77, 83]
        cn_lucode[87] = [36, 60, 73, 79]

        [rows, cols] = arr_present.shape
        # Value euro per cubic meter
        value_coeff = 300
        arr_Pe_present = np.zeros((rows, cols))
        arr_Pn_present = np.zeros((rows, cols))
        for lucode in np.unique(arr_present):
            try:
                S = (25400 / cn_lucode[lucode][gruppo_id]) - 254
                IA = S / 10
                if (IA < rain_tot):
                    Pn = rain_tot - IA
                else:
                    Pn = 0
                Pn = rain_tot - IA
                arr_Pn_present[np.where(arr_present == lucode)] = Pn
                arr_Pe_present[np.where(arr_present == lucode)] = (Pn ** 2) / (Pn + S)
            except:
                pass
        arr_Pe_future = np.zeros((rows, cols))
        arr_Pn_future = np.zeros((rows, cols))
        for lucode in np.unique(arr_future):
            try:
                S = (25400 / cn_lucode[lucode][gruppo_id]) - 254
                IA = S / 10
                if (IA < rain_tot):
                    Pn = rain_tot - IA
                else:
                    Pn = 0
                Pn = rain_tot - IA
                arr_Pn_future[np.where(arr_future == lucode)] = Pn
                arr_Pe_future[np.where(arr_future == lucode)] = (Pn ** 2) / (Pn + S)
            except:
                pass
        # Convert to squared meters and assign value
        arr_value_present = value_coeff * ((arr_Pn_present - arr_Pe_present) / 1000) * area_pixel
        arr_value_future = value_coeff * ((arr_Pn_future - arr_Pe_future) / 1000) * area_pixel
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/04_protezione_idrogeologica_presente_mm.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_Pe_present)
        outdata.FlushCache()
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/04_protezione_idrogeologica_futura_mm.tiff'
        driver = gdal.GetDriverByName("GTiff")
        arr_diff_tot = arr_value_future - arr_value_present
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_Pe_future)
        outdata.FlushCache()
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/SE_04_protezione_idrogeologica_delta_euro.tiff'
        driver = gdal.GetDriverByName("GTiff")
        arr_diff_tot = arr_value_future - arr_value_present
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_diff_tot)
        outdata.FlushCache()
        # Years
        present = self.parameterAsInt(parameters, self.INPUTPRE, context)
        future = self.parameterAsInt(parameters, self.INPUTFUT, context)
        report_output = path_output + '/SE_protezione_idrogeologica.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Sommario dell'analisi della protezione idrogeologica\n")
        f.write("Data: " + today +"\n\n\n")
        f.write("Analisi stato di fatto\n\n")
        f.write("Anno corrente: %i \n" %present)
        f.write("Protezione idrogeologica stato attuale (mm): %f \n" % (np.sum(arr_Pn_present - arr_Pe_present)))
        f.write("Protezione idrogeologica sulla superficie totale - Stato attuale (mc): %f \n" % (
                np.sum(((arr_Pn_present - arr_Pe_present) / 1000) * area_pixel)))
        f.write("Valore totale della protezione idrogeologica (€/anno): %f \n\n" % (np.sum(arr_value_present)))
        f.write("RIEPILOGO DATI INPUT stato di fatto\n")
        f.write("Elenco LuCode area in esame: %s \n\n\n" % (np.unique(arr_present)))
        f.write("Analisi stato di progetto\n\n")
        f.write("Anno progetto: %i \n" % (future))
        f.write("Protezione idrogeologica stato di progetto (mm): %f \n" % (np.sum(arr_Pn_future - arr_Pe_future)))
        f.write("Protezione idrogeologica sulla superficie totale - Stato di progetto (mc): %f \n" % (
                np.sum(((arr_Pn_future - arr_Pe_future) / 1000) * area_pixel)))
        f.write("Valore totale della protezione idrogeologica (€/anno): %f \n\n" % (np.sum(arr_value_future)))
        f.write("RIEPILOGO DATI INPUT stato di progetto\n")
        f.write("Elenco LuCode area in esame: %s \n\n\n" % (np.unique(arr_future)))
        f.write("Differenze tra stato di progetto e stato attuale\n\n")
        f.write("Anno progetto: %i - %i\n" % (present, future))
        f.write("Differenza della protezione idrogeologica (mm): %f \n" % (np.sum(
            (arr_Pn_future - arr_Pe_future) - (arr_Pn_present - arr_Pe_present))))
        f.write("Differenza della protezione idrogeologica sulla superficie totale (mc): %f \n" % (
            np.sum((arr_Pn_future - arr_Pe_future) - (arr_Pn_present - arr_Pe_present))/1000 * area_pixel))
        f.write("Differenza in termini economici del SE di protezione idrogeologica (stato di progetto – stato attuale) (€):%d \n" % (
            np.sum(arr_diff_tot)))
        return {self.OUTPUT: 'Completed'}

        
        # -----------------------------------------------------------------------------------  
        # Copyright (c) 2021 Città di Torino.
        # 
        # This material is free software: you can redistribute it and/or modify
        # it under the terms of the GNU General Public License as published by
        # the Free Software Foundation, either version 2 of the License, or
        # (at your option) any later version.
        # 
        # This program is distributed in the hope that it will be useful,
        # but WITHOUT ANY WARRANTY; without even the implied warranty of
        # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        # GNU General Public License for more details.
        # 
        # You should have received a copy of the GNU General Public License
        # along with this program. If not, see http://www.gnu.org/licenses.
        # -----------------------------------------------------------------------------------  

