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

    INPUTNP = 'INPUTNP'
    INPUTPP = 'INPUTPP'
    INPUTOP = 'INPUTOP'
    INPUTPRE = 'INPUTPRE'
    INPUTNF = 'INPUTNF'
    INPUTPF = 'INPUTPF'
    INPUTOF = 'INPUTOF'
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
        return 'SE Rimozione Inquinanti'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Rimozione Inquinanti')

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
        return self.tr("Algoritmo per il calcolo della rimozione degli inquinanti, nell'ambito del calcolo dei Servizi Ecosistemici per la Città di Torino")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.

        self.addParameter(
            QgsProcessingParameterNumber(
            self.PIXEL_RES,
            self.tr('Risoluzione spaziale dei raster (m)'),
            QgsProcessingParameterNumber.Integer,
            2
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTNP,
                self.tr('Raster NO2 - Stato attuale'),
                [QgsProcessing.TypeRaster]
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTPP,
                self.tr('Raster PM10 - Stato attuale'),
                [QgsProcessing.TypeRaster]
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTOP,
                self.tr('Raster Ozono - Stato attuale'),
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
                self.INPUTNF,
                self.tr('Raster NO2 - Stato di progetto'),
                [QgsProcessing.TypeRaster]
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTPF,
                self.tr('Raster PM10 - Stato di progetto'),
                [QgsProcessing.TypeRaster]
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTOF,
                self.tr('Raster Ozono - Stato di progetto'),
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
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                self.tr('Salva nella cartella')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        NO2_present_raster = self.parameterAsRasterLayer(parameters, self.INPUTNP, context)
        NO2_present_data_source = gdal.Open(NO2_present_raster.dataProvider().dataSourceUri())
        arr_NO2_present = NO2_present_data_source.GetRasterBand(1).ReadAsArray()

        PM10_present_raster = self.parameterAsRasterLayer(parameters, self.INPUTPP, context)
        PM10_present_data_source = gdal.Open(PM10_present_raster.dataProvider().dataSourceUri())
        arr_PM10_present = PM10_present_data_source.GetRasterBand(1).ReadAsArray()

        ozono_present_raster = self.parameterAsRasterLayer(parameters, self.INPUTOP, context)
        ozono_present_data_source = gdal.Open(ozono_present_raster.dataProvider().dataSourceUri())
        arr_ozono_present = ozono_present_data_source.GetRasterBand(1).ReadAsArray()

        arr_present = arr_ozono_present + arr_PM10_present + arr_NO2_present

        NO2_future_raster = self.parameterAsRasterLayer(parameters, self.INPUTNF, context)
        NO2_future_data_source = gdal.Open(NO2_future_raster.dataProvider().dataSourceUri())
        arr_NO2_future = NO2_future_data_source.GetRasterBand(1).ReadAsArray()

        PM10_future_raster = self.parameterAsRasterLayer(parameters, self.INPUTPF, context)
        PM10_future_data_source = gdal.Open(PM10_future_raster.dataProvider().dataSourceUri())
        arr_PM10_future = PM10_future_data_source.GetRasterBand(1).ReadAsArray()

        ozono_future_raster = self.parameterAsRasterLayer(parameters, self.INPUTOF, context)
        ozono_future_data_source = gdal.Open(ozono_future_raster.dataProvider().dataSourceUri())
        arr_ozono_future = ozono_future_data_source.GetRasterBand(1).ReadAsArray()

        arr_future = arr_ozono_future + arr_PM10_future + arr_NO2_future

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        NO2_euro_coeff = 77641.89
        ozono_euro_coeff = 14658.11
        PM10_euro_coeff = 17132.56

        arr_euro_present_NO2 = arr_NO2_present * NO2_euro_coeff
        arr_euro_present_ozono = arr_ozono_present * ozono_euro_coeff
        arr_euro_present_PM10 = arr_PM10_present * PM10_euro_coeff
        arr_value_present = arr_euro_present_PM10 + arr_euro_present_ozono + arr_euro_present_NO2

        arr_euro_future_NO2 = arr_NO2_future * NO2_euro_coeff
        arr_euro_future_ozono = arr_ozono_future * ozono_euro_coeff
        arr_euro_future_PM10 = arr_PM10_future * PM10_euro_coeff
        arr_value_future = arr_euro_future_PM10 + arr_euro_future_ozono + arr_euro_future_NO2

        arr_diff_NO2 = arr_euro_future_NO2 - arr_euro_present_NO2
        arr_diff_PM10 = arr_euro_future_PM10 - arr_euro_present_PM10
        arr_diff_ozono = arr_euro_future_ozono - arr_euro_present_ozono

        arr_diff_tot = arr_diff_NO2 + arr_diff_PM10 + arr_diff_ozono

        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/SE_02_rimozione_inquinanti_delta_euro.tiff'
        driver = gdal.GetDriverByName("GTiff")
        [cols, rows] = arr_NO2_present.shape
        diff_tot = np.sum(arr_diff_tot) / (cols * rows )
        outdata = driver.Create(file_output, rows, cols, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(NO2_present_data_source.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(NO2_present_data_source.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_diff_tot)
        print(np.max(outdata.GetRasterBand(1).ReadAsArray()))
        outdata.FlushCache()

        # Years
        present = self.parameterAsInt(parameters, self.INPUTPRE, context)
        future = self.parameterAsInt(parameters, self.INPUTFUT, context)
        report_output = path_output + '/SE_rimozione_inquinanti.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Sommario dell'analisi della rimozione inquinanti\n")
        f.write("Data: " + today +"\n\n\n")
        f.write("Analisi stato di fatto\n\n")
        f.write("Anno corrente: %i \n" % (present))
        f.write("Rimozione NO2 Stato attuale (ton): %f \n" % (np.sum(arr_NO2_present)))
        f.write("Rimozione PM10 Stato attuale (ton): %f \n" % (np.sum(arr_PM10_present)))
        f.write("Rimozione ozono Stato attuale (ton): %f \n" % (np.sum(arr_ozono_present)))
        f.write("Valore totale della rimozione inquinanti (€): %f \n\n\n" % (np.sum(arr_value_present)))
        f.write("Analisi stato di progetto\n\n")
        f.write("Anno progetto: %i \n" % (future))
        f.write("Rimozione NO2 Stato di progetto (ton): %f \n" % (np.sum(arr_NO2_future)))
        f.write("Rimozione PM10 Stato di progetto (ton): %f \n" % (np.sum(arr_PM10_future)))
        f.write("Rimozione ozono Stato di progetto (ton): %f \n" % (np.sum(arr_ozono_future)))
        f.write("Valore totale della rimozione inquinanti (€): %f \n\n\n" % (np.sum(arr_value_future)))
        f.write("Differenze tra stato di progetto e stato attuale\n\n")
        f.write("Anno progetto: %i - %i\n" % (present, future))
        f.write("Differenza della rimozione inquinanti (ton):: %f \n" % (np.sum(arr_future - arr_present)))
        f.write("Differenza sequestro inquinanti per unità di superficie (ton/ha): %f \n" % (
             np.sum(arr_future - arr_present) / (cols * rows * area_pixel) * 10000))
        f.write("Differenza in termini economici del SE Rimozione inquinanti (stato di progetto – stato attuale) (€):%d \n" % (
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

