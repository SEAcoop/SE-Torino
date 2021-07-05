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
    INPUTPRE = 'INPUTPRE'
    INPUTFUT = 'INPUTFUT'
    INPUTRP = 'INPUTRP'
    INPUTRF = 'INPUTRF'
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
        HM_lucode[1] = 4.62718336
        HM_lucode[2] = 3.83420036
        HM_lucode[3] = 0.4823722
        HM_lucode[4] = 4.42937216
        HM_lucode[5] = 4.93675407
        HM_lucode[6] = 4.15857601
        HM_lucode[7] = 3.03540913
        HM_lucode[8] = 0.86425104
        HM_lucode[9] = 2.82585889
        HM_lucode[10] = 1.91524496
        HM_lucode[11] = 0.67386976
        HM_lucode[12] = 1.85691874
        HM_lucode[13] = 0.57390328
        HM_lucode[14] = 2.44235093
        HM_lucode[15] = 0.78460174
        HM_lucode[16] = 2.25657445
        HM_lucode[17] = 2.00661297
        HM_lucode[18] = 1.11856046
        HM_lucode[19] = 2.96848245
        HM_lucode[20] = 0.51584438
        HM_lucode[21] = 3.66727253
        HM_lucode[22] = 2.15298825
        HM_lucode[23] = 2.79566511
        HM_lucode[24] = 3.28726693
        HM_lucode[25] = 1.11711756
        HM_lucode[26] = 2.74429667
        HM_lucode[27] = 2.11703174
        HM_lucode[28] = 3.31600525
        HM_lucode[29] = 4.1666852
        HM_lucode[30] = 4.14721283
        HM_lucode[31] = 2.22970933
        HM_lucode[32] = 0.8684379
        HM_lucode[33] = 0.95477925
        HM_lucode[34] = 3.57055523
        HM_lucode[35] = 0.21495761
        HM_lucode[36] = 0.38677367
        HM_lucode[37] = 5.20694318
        HM_lucode[38] = 3.81729612
        HM_lucode[39] = 3.3219752
        HM_lucode[40] = 4.45037633
        HM_lucode[41] = 4.73611724
        HM_lucode[42] = 4.30607209
        HM_lucode[43] = 2.13796834
        HM_lucode[44] = 1.81924634
        HM_lucode[45] = 2.48564168
        HM_lucode[46] = 1.07186001
        HM_lucode[47] = 0.53461912
        HM_lucode[48] = 1.95442937
        HM_lucode[49] = 1.11875979
        HM_lucode[50] = 1.1334159
        HM_lucode[51] = 0.91150442
        HM_lucode[52] = 1.95317116
        HM_lucode[53] = 3.5382051
        HM_lucode[54] = 3.30428226
        HM_lucode[55] = 1.92616705
        HM_lucode[56] = 0.39094275
        HM_lucode[57] = 2.41044505
        HM_lucode[58] = 3.20739734
        HM_lucode[59] = 4.38517119
        HM_lucode[60] = 0.64614399
        HM_lucode[61] = 4.16470902
        HM_lucode[62] = 4.29626227
        HM_lucode[63] = 4.28313385
        HM_lucode[64] = 4.45815007
        HM_lucode[65] = 3.35787101
        HM_lucode[66] = 1.57321618
        HM_lucode[67] = 1.99595624
        HM_lucode[68] = 3.06093165
        HM_lucode[69] = 4.0867662
        HM_lucode[70] = 4.37100281
        HM_lucode[71] = 2.09081137
        HM_lucode[72] = 0.84961896
        HM_lucode[73] = 4.6212141
        HM_lucode[74] = 4.92998582
        HM_lucode[75] = 3.88542519
        HM_lucode[76] = 5.09573919
        HM_lucode[77] = 2.57326408
        HM_lucode[78] = 2.31943221
        HM_lucode[79] = 2.1070807
        HM_lucode[80] = 4.42278093
        HM_lucode[81] = 3.59365177
        HM_lucode[82] = 4.43509066
        HM_lucode[83] = 5.37128195
        HM_lucode[84] = 5.01703229
        HM_lucode[85] = 5.24431647
        HM_lucode[86] = 5.16957513
        HM_lucode[87] = 4.71936258

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

