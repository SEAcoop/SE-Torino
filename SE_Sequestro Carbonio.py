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

    INPUT1 = 'INPUT1'
    INPUT2 = 'INPUT2'
    INPUT3 = 'INPUT3'
    INPUT4 = 'INPUT4'
    INPUT5 = 'INPUT5'
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
        return 'SE Sequesto Carbonio'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Sequesto Carbonio')

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
        return self.tr("Algoritmo per il calcolo del sequesto del carbonio, nell'ambito del calcolo dei Servizi Ecosistemici per la Città di Torino")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT1,
                self.tr('Raster Stock carbonio Stato attuale'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT2,
                self.tr('Raster Stock carbonio Stato di progetto'),
                [QgsProcessing.TypeRaster]
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
            QgsProcessingParameterNumber(
            self.INPUT3,
            self.tr('Anno attuale'),
            QgsProcessingParameterNumber.Integer,
            2021
            )
        )


        self.addParameter(
            QgsProcessingParameterNumber(
            self.INPUT4,
            self.tr('Anno progetto'),
            QgsProcessingParameterNumber.Integer,
            2030
            )
        )
        
        double_param = QgsProcessingParameterNumber(
            self.INPUT5,
            self.tr('Carbonio in Euro'),
            QgsProcessingParameterNumber.Double,
            81.84
        )
        double_param.setMetadata( {'widget_wrapper': { 'decimals': 2 }} )
        self.addParameter(double_param)
        
        
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
        present_raster = self.parameterAsRasterLayer(parameters, self.INPUT1, context)
        ds_present = gdal.Open(present_raster.dataProvider().dataSourceUri())
        arr_present = ds_present.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_present[arr_present<0] = 0

        # Load future raster
        future_raster = self.parameterAsRasterLayer(parameters, self.INPUT2, context)
        ds_future = gdal.Open(future_raster.dataProvider().dataSourceUri())
        arr_future = ds_future.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_future[arr_future<0] = 0

        print(arr_future)
        print(np.unique(arr_future))
        # Parameters
        V = self.parameterAsDouble(parameters, self.INPUT5, context)

        r = 0

        c = 3

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)
        # Years
        present = self.parameterAsInt(parameters, self.INPUT3, context)
        future = self.parameterAsInt(parameters, self.INPUT4, context)

        # Calculate coeff sequestration
        arr_diff = arr_future - arr_present
        arr_diff_norm = arr_diff / float((future - present))
        arr_years = np.array(range(0, future - present))
        coeff = sum(1 / ((1 + r / 100) ** arr_years * ((1 + c / 100) ** arr_years)))
        carbon_sequestration_value = V * arr_diff_norm * coeff
        carbon_sequestration_difference = arr_future - arr_present
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/SE_01_carbon_sequestration_delta_euro.tiff'
        driver = gdal.GetDriverByName("GTiff")
        [cols, rows] = carbon_sequestration_value.shape
        carbon_sequestration_difference_area = np.sum(carbon_sequestration_difference) / (cols * rows * area_pixel)
        outdata = driver.Create(file_output, rows, cols, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(carbon_sequestration_value)
        print(np.max(outdata.GetRasterBand(1).ReadAsArray()))
        outdata.FlushCache() ##saves to disk!!
        outdata = None
        band = None
        ds = None
        print(np.sum(arr_present))
        report_output = path_output + '/SE_sequestro_carbonio.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Sommario dell'analisi del sequestro di carbonio\n")
        f.write("Data: " + today +"\n\n\n")
        f.write("Analisi stato di fatto\n\n")
        f.write("Anno corrente: %i \n" % (present))
        f.write("Sequestro carbonio Stato attuale (ton Corg): %f \n" % (np.sum(arr_present)))
        f.write("Valore medio del carbonio sequestrato per unità di superficie - Stato attuale (ton Corg/ha): : %f \n" % (
                np.sum(arr_present) / (cols * rows * area_pixel) * 10000))
        f.write("Valore totale del sequestro di carbonio (€): %f \n\n\n" % ((np.sum(arr_present)*V*coeff)/ float((future - present))))
        f.write("Analisi stato di progetto\n\n")
        f.write("Anno progetto: %i \n" % (future))
        f.write("Sequestro carbonio Stato di progetto (ton Corg): %f \n" % (np.sum(arr_future)))
        f.write("Valore medio del carbonio sequestrato per unità di superficie - Stato di progetto (ton Corg/ha): %f \n" % (
                np.sum(arr_future) / (cols * rows * area_pixel) * 10000))
        f.write("Valore totale del sequestro di carbonio (€): %f \n\n\n" % ((np.sum(arr_future)*V*coeff) / float((future - present))))
        f.write("Differenze tra stato di progetto e stato attuale\n\n")
        f.write("Anno progetto: %i - %i\n" % (present, future))
        f.write("Differenza di sequestro carbonio (ton Corg): %f \n" % (np.sum(arr_diff)))
        f.write("Differenza carbonio sequestrato per unità di superficie (ton Corg/ha): %f \n" % (
            carbon_sequestration_difference_area * 10000))
        f.write("Differenza in termini economici del SE di sequestro di carbonio (stato di progetto – stato attuale) (€):%d \n" % (
            np.sum(carbon_sequestration_value)))
        return {self.OUTPUT: carbon_sequestration_value}

        
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

