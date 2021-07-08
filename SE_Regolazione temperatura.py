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
                       QgsProcessingParameterEnum,
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
        return 'SE Regolazione temperatura'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Regolazione temperatura')

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
        return self.tr("Algoritmo per il calcolo della Regolazione della temperatura, nell'ambito del calcolo dei Servizi Ecosistemici per la Città di Torino")

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
                self.tr('Raster Uso Suolo Stato attuale'),
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
                self.tr('Raster Uso Suolo Stato di progetto'),
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
        arr_present[arr_present<0] = 0

        # Load future raster
        future_raster = self.parameterAsRasterLayer(parameters, self.INPUTRF, context)
        ds_future = gdal.Open(future_raster.dataProvider().dataSourceUri())
        arr_future = ds_future.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_future[arr_future<0] = 0

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        # HM dictionary
        HM_lucode = {}
        HM_lucode[1] = 0.10
        HM_lucode[2] = 0.10
        HM_lucode[3] = 0
        HM_lucode[4] = 0.10
        HM_lucode[5] = 0.10
        HM_lucode[6] = 0.10
        HM_lucode[7] = 0.10
        HM_lucode[8] = 0
        HM_lucode[9] = 0.10
        HM_lucode[10] = 0.10
        HM_lucode[11] = 0
        HM_lucode[12] = 0.10
        HM_lucode[13] = 0
        HM_lucode[14] = 0.10
        HM_lucode[15] = 0
        HM_lucode[16] = 0.10
        HM_lucode[17] = 0.10
        HM_lucode[18] = 0.10
        HM_lucode[19] = 0.10
        HM_lucode[20] = 0
        HM_lucode[21] = 0.10
        HM_lucode[22] = 0.10
        HM_lucode[23] = 0.10
        HM_lucode[24] = 0.10
        HM_lucode[25] = 0
        HM_lucode[26] = 0.10
        HM_lucode[27] = 0
        HM_lucode[28] = 0
        HM_lucode[29] = 0.10
        HM_lucode[30] = 0.10
        HM_lucode[31] = 0
        HM_lucode[32] = 0.10
        HM_lucode[33] = 0.10
        HM_lucode[34] = 0.10
        HM_lucode[35] = 0
        HM_lucode[36] = 0
        HM_lucode[37] = 0.10
        HM_lucode[38] = 0.10
        HM_lucode[39] = 0.10
        HM_lucode[40] = 0.10
        HM_lucode[41] = 0.10
        HM_lucode[42] = 0.10
        HM_lucode[43] = 0.10
        HM_lucode[44] = 0.10
        HM_lucode[45] = 0
        HM_lucode[46] = 0.10
        HM_lucode[47] = 0
        HM_lucode[48] = 0.10
        HM_lucode[49] = 0.10
        HM_lucode[50] = 0
        HM_lucode[51] = 0
        HM_lucode[52] = 0
        HM_lucode[53] = 0.10
        HM_lucode[54] = 0.10
        HM_lucode[55] = 0
        HM_lucode[56] = 0
        HM_lucode[57] = 0.10
        HM_lucode[58] = 0.10
        HM_lucode[59] = 0.10
        HM_lucode[60] = 0
        HM_lucode[61] = 0.10
        HM_lucode[62] = 0.10
        HM_lucode[63] = 0.10
        HM_lucode[64] = 0.10
        HM_lucode[65] = 0.10
        HM_lucode[66] = 0
        HM_lucode[67] = 0
        HM_lucode[68] = 0.10
        HM_lucode[69] = 0.10
        HM_lucode[70] = 0.10
        HM_lucode[71] = 0
        HM_lucode[72] = 0
        HM_lucode[73] = 0.10
        HM_lucode[74] = 0.10
        HM_lucode[75] = 0.10
        HM_lucode[76] = 0.10
        HM_lucode[77] = 0
        HM_lucode[78] = 0
        HM_lucode[79] = 0.10
        HM_lucode[80] = 0
        HM_lucode[81] = 0.10
        HM_lucode[82] = 0.10
        HM_lucode[83] = 0.10
        HM_lucode[84] = 0.10
        HM_lucode[85] = 0.10
        HM_lucode[86] = 0.10
        HM_lucode[87] = 0.10

        [rows, cols] = arr_present.shape

        # Assigning scores for each distinct lucode
        arr_HM_pres = np.zeros((rows, cols))
        arr_HM_fut = np.zeros((rows, cols))
        for lucode in np.unique(arr_present):
            if lucode in HM_lucode.keys():
                arr_HM_pres[np.where(arr_present == lucode)] = HM_lucode[lucode] * area_pixel
        value_pres = arr_HM_pres * 1.6 * 0.1
        for lucode in np.unique(arr_future):
            if lucode in HM_lucode.keys():
                arr_HM_fut[np.where(arr_future == lucode)] = HM_lucode[lucode] * area_pixel
        value_fut = arr_HM_fut * 1.6 * 0.1
        delta_value = value_fut - value_pres
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)
        # Years
        present = self.parameterAsInt(parameters, self.INPUTPRE, context)
        future = self.parameterAsInt(parameters, self.INPUTFUT, context)
        # Store raster present
        file_output = path_output + '/03_regolazione_temperatura_presente.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output,  cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_HM_pres)
        print(np.max(outdata.GetRasterBand(1).ReadAsArray()))
        outdata.FlushCache() ##saves to disk!!
        outdata = None
        band = None
        ds = None
        file_output = path_output + '/03_regolazione_temperatura_futuro.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output,  cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_HM_fut)
        print(np.max(outdata.GetRasterBand(1).ReadAsArray()))
        outdata.FlushCache() ##saves to disk!!
        outdata = None
        band = None
        ds = None
        file_output = path_output + '/03_regolazione_temperatura_delta_euro.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output,  cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(delta_value)
        print(np.max(outdata.GetRasterBand(1).ReadAsArray()))
        outdata.FlushCache() ##saves to disk!!
        outdata = None
        band = None
        ds = None
        report_output = path_output + '/SE_regolazione_temperatura.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Sommario dell'analisi della regolazione della temperatura\n")
        f.write("Data: " + today +"\n\n\n")
        f.write("Analisi stato di fatto\n\n")
        f.write("Anno corrente: %i \n" % (present))
        f.write("Regolazione della temperatura Stato attuale: %f \n" % (np.sum(arr_HM_pres)))
        f.write("Valore totale della regolazione della temperatura (€): %f \n\n\n" % ((np.sum(value_pres))))
        f.write("Analisi stato di progetto\n\n")
        f.write("Anno progetto: %i \n" % (future))
        f.write("Regolazione della temperatura Stato di progetto: %f \n" % (np.sum(arr_HM_fut)))
        f.write("Valore totale della regolazione della temperatura (€): %f \n\n\n" % ((np.sum(value_fut))))
        f.write("Differenze tra stato di progetto e stato attuale\n\n")
        f.write("Anno progetto: %i - %i\n" % (present, future))
        f.write("Differenza di regolazione della temperatura: %f \n" % (np.sum(arr_HM_fut - arr_HM_pres)))
        f.write("Differenza in termini economici del SE di regolazione della temperatura (stato di progetto – stato attuale) (€):%d \n" % (
            np.sum(delta_value)))
        return {self.OUTPUT: delta_value}
        
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

