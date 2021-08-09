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
    INPUTPRE = 'INPUTPRE'
    INPUTRF = 'INPUTRF'
    INPUTFUT = 'INPUTFUT'
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
        return 'SE Impollinazione'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Impollinazione')

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
        return self.tr("Algoritmo per il calcolo dell'impollinazione, nell'ambito del calcolo dei Servizi Ecosistemici per la Città di Torino")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
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

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        # Clean negative values
        arr_future[arr_future < 0] = 0
        # SE valore impollinazione per lucode
        value_lucode = {}
        value_lucode[1] = 0
        value_lucode[2] = 0
        value_lucode[3] = 0
        value_lucode[4] = 0.0161
        value_lucode[5] = 0
        value_lucode[6] = 0.0161
        value_lucode[7] = 0.0187
        value_lucode[8] = 0
        value_lucode[9] = 0.0187
        value_lucode[10] = 0.0187
        value_lucode[11] = 0
        value_lucode[12] = 0.0161
        value_lucode[13] = 0
        value_lucode[14] = 0.0161
        value_lucode[15] = 0
        value_lucode[16] = 0.0161
        value_lucode[17] = 0.0187
        value_lucode[18] = 0
        value_lucode[19] = 0.0187
        value_lucode[20] = 0
        value_lucode[21] = 0.0187
        value_lucode[22] = 0.0187
        value_lucode[23] = 0.0187
        value_lucode[24] = 0.0161
        value_lucode[25] = 0
        value_lucode[26] = 0.0187
        value_lucode[27] = 0.0161
        value_lucode[28] = 0
        value_lucode[29] = 0.0187
        value_lucode[30] = 0.0161
        value_lucode[31] = 0
        value_lucode[32] = 0.0187
        value_lucode[33] = 0.0161
        value_lucode[34] = 0.0161
        value_lucode[35] = 0
        value_lucode[36] = 0
        value_lucode[37] = 0.02
        value_lucode[38] = 0.0187
        value_lucode[39] = 0.0161
        value_lucode[40] = 0
        value_lucode[41] = 0
        value_lucode[42] = 0
        value_lucode[43] = 0.0187
        value_lucode[44] = 0.0187
        value_lucode[45] = 0
        value_lucode[46] = 0.0187
        value_lucode[47] = 0
        value_lucode[48] = 0.0187
        value_lucode[49] = 0.0187
        value_lucode[50] = 0
        value_lucode[51] = 0
        value_lucode[52] = 0
        value_lucode[53] = 0.0187
        value_lucode[54] = 0
        value_lucode[55] = 0
        value_lucode[56] = 0
        value_lucode[57] = 0.0187
        value_lucode[58] = 0.0196
        value_lucode[59] = 0
        value_lucode[60] = 0
        value_lucode[61] = 0.0161
        value_lucode[62] = 0.0187
        value_lucode[63] = 0.0161
        value_lucode[64] = 0.0161
        value_lucode[65] = 0
        value_lucode[66] = 0
        value_lucode[67] = 0
        value_lucode[68] = 0.0161
        value_lucode[69] = 0.0187
        value_lucode[70] = 0.0161
        value_lucode[71] = 0.0161
        value_lucode[72] = 0
        value_lucode[73] = 0
        value_lucode[74] = 0.0187
        value_lucode[75] = 0
        value_lucode[76] = 0
        value_lucode[77] = 0
        value_lucode[78] = 0
        value_lucode[79] = 0.0161
        value_lucode[80] = 0
        value_lucode[81] = 0
        value_lucode[82] = 0.0187
        value_lucode[83] = 0.0187
        value_lucode[84] = 0.0187
        value_lucode[85] = 0.0187
        value_lucode[86] = 0.0187
        value_lucode[87] = 0.0187
        [rows, cols] = arr_present.shape
        arr_value_present = np.zeros((rows, cols))
        for lucode in np.unique(arr_present):
            try:
                arr_value_present[np.where(arr_present == lucode)] = value_lucode[lucode] * area_pixel
            except:
                pass
        arr_value_future = np.zeros((rows, cols))
        for lucode in np.unique(arr_future):
            try:
                arr_value_future[np.where(arr_future == lucode)] = value_lucode[lucode] * area_pixel
            except:
                pass
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/SE_09_impollinazione_delta_euro.tiff'
        driver = gdal.GetDriverByName("GTiff")
        arr_diff_tot = arr_value_future - arr_value_present
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_diff_tot)
        print(np.max(outdata.GetRasterBand(1).ReadAsArray()))
        outdata.FlushCache()
        print(path_output)
        # Years
        present = self.parameterAsInt(parameters, self.INPUTPRE, context)
        future = self.parameterAsInt(parameters, self.INPUTFUT, context)
        report_output = path_output + '/SE_impollinazione.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Report dell'analisi dell'impollinazione del " + today + "\n")
        f.write("Anno corrente: %i \n" % (present))
        f.write("Anno progetto: %i \n" % (future))
        f.write("Variazione valore totale dell'impollinazione (€): %d \n" % (np.sum(arr_diff_tot)))
        f.write("Impollinazione Stato attuale (€): %f \n" % (np.sum(arr_value_present)))
        f.write("Impollinazione Stato di progetto (€): %f \n" % (np.sum(arr_value_future)))
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

