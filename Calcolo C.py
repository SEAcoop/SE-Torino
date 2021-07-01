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
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFolderDestination)
import pandas as pd
import gdal
import numpy as np

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

    INPUT = 'INPUT'
    FASE = 'FASE'
    PIXEL_RES = 'PIXEL_RES'
    SPECIE1 = 'SPECIE1'
    ESEMPL1 = 'ESEMPL1'
    SPECIE2 = 'SPECIE2'
    ESEMPL2 = 'ESEMPL2'    
    SPECIE3 = 'SPECIE3'
    ESEMPL3 = 'ESEMPL3'
    SPECIE4 = 'SPECIE4'
    ESEMPL4 = 'ESEMPL4'    
    SPECIE5 = 'SPECIE5'
    ESEMPL5 = 'ESEMPL5'
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
        return 'Calcolo Carbonio'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Calcolo Carbonio')

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
        return self.tr("Calcolo Carbonio")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        all_species = ['Abete (Picea abies, glauca, omorika, orientalis, pungens)', 'Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)', 'Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)', 'Bagolaro (Celtis australis, occidentalis)',
                       'Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)', 'Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)', 'Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)', 'Frassino (Fraxinus americana, excelsior, excelsior Pendula)',
                       'Ippocastano (Aesculus hippocastanum, pavia)', 'Olmo  (Ulmus laevis, minor,parvifolia,pumila)', 'Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)', 'Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)',
                       'Platano (Platanus orientalis, occidentalis, hybrida)', 'Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)', 'Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)']

        fasi = ['Stato attuale', 'Stato di progetto']
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Raster Uso suolo'),
                [QgsProcessing.TypeRaster]
            )
        )
    
        self.addParameter(
            QgsProcessingParameterEnum(
                self.FASE,
                self.tr('Fase di lavoro'),
                fasi,
                defaultValue=''
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
            QgsProcessingParameterEnum(
                self.SPECIE1,
                self.tr('Specie 1'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL1,
            self.tr('Numero Esemplari Specie 1'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )
    
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE2,
                self.tr('Specie 2'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL2,
            self.tr('Numero Esemplari Specie 2'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )

    
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE3,
                self.tr('Specie 3'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL3,
            self.tr('Numero Esemplari Specie 3'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE4,
                self.tr('Specie 4'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL4,
            self.tr('Numero Esemplari Specie 4'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )
    
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE5,
                self.tr('Specie 5'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL5,
            self.tr('Numero Esemplari Specie 5'),
            QgsProcessingParameterNumber.Integer,
            0
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
        # List of all species
        all_species = ['Abete (Picea abies, glauca, omorika, orientalis, pungens)', 'Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)', 'Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)', 'Bagolaro (Celtis australis, occidentalis)',
                       'Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)', 'Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)', 'Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)', 'Frassino (Fraxinus americana, excelsior, excelsior Pendula)',
                       'Ippocastano (Aesculus hippocastanum, pavia)', 'Olmo  (Ulmus laevis, minor,parvifolia,pumila)', 'Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)', 'Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)',
                       'Platano (Platanus orientalis, occidentalis, hybrida)', 'Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)', 'Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)']
        # List of all lucodes
        lucode_list = [7, 9, 17, 19, 21, 23, 26, 29, 32, 38, 43, 44, 46, 48, 53, 57, 62, 69, 70, 74, 82, 83, 84, 85, 86, 87]
        # Initialize dicionary of c sequestration per species
        c_sequestration_species = {}
        c_sequestration_species['Abete (Picea abies, glauca, omorika, orientalis, pungens)'] = 0.18
        c_sequestration_species['Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)'] = 0,41
        c_sequestration_species['Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)'] = 0.34
        c_sequestration_species['Bagolaro (Celtis australis, occidentalis)'] = 0.75
        c_sequestration_species['Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)'] = 0.38
        c_sequestration_species['Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)'] = 0.39
        c_sequestration_species['Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)'] = 0.2
        c_sequestration_species['Frassino (Fraxinus americana, excelsior, excelsior Pendula)'] = 0.35
        c_sequestration_species['Ippocastano (Aesculus hippocastanum, pavia)'] = 0.44
        c_sequestration_species['Olmo  (Ulmus laevis, minor,parvifolia,pumila)'] = 0.48
        c_sequestration_species['Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)'] = 0.31
        c_sequestration_species['Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)'] = 0.67
        c_sequestration_species['Platano (Platanus orientalis, occidentalis, hybrida)'] = 0.7
        c_sequestration_species['Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)'] = 0.44
        c_sequestration_species['Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)'] = 0.28
        # c soil lucode specififc
        c_soil = {}
        c_soil[1] = 0.0056
        c_soil[2] = 0.0056
        c_soil[3] = 0
        c_soil[4] = 0.0056
        c_soil[5] = 0.0056
        c_soil[6] = 0.0056
        c_soil[7] = 0.0056
        c_soil[8] = 0
        c_soil[9] = 0.0056
        c_soil[10] = 0
        c_soil[11] = 0
        c_soil[12] = 0
        c_soil[13] = 0
        c_soil[14] = 0
        c_soil[15] = 0
        c_soil[16] = 0
        c_soil[17] = 0
        c_soil[18] = 0
        c_soil[19] = 0.0056
        c_soil[20] = 0
        c_soil[21] = 0.0056
        c_soil[22] = 0.0056
        c_soil[23] = 0.0056
        c_soil[24] = 0.0056
        c_soil[25] = 0
        c_soil[26] = 0.0056
        c_soil[27] = 0
        c_soil[28] = 0
        c_soil[29] = 0.0056
        c_soil[30] = 0.0056
        c_soil[31] = 0
        c_soil[32] = 0.0056
        c_soil[33] = 0.0056
        c_soil[34] = 0.0056
        c_soil[35] = 0
        c_soil[36] = 0
        c_soil[37] = 0.0056
        c_soil[38] = 0.0056
        c_soil[39] = 0.0056
        c_soil[40] = 0.0056
        c_soil[41] = 0.0056
        c_soil[42] = 0.0056
        c_soil[43] = 0.0056
        c_soil[44] = 0.0056
        c_soil[45] = 0
        c_soil[46] = 0
        c_soil[47] = 0
        c_soil[48] = 0.0056
        c_soil[49] = 0.0056
        c_soil[50] = 0
        c_soil[51] = 0
        c_soil[52] = 0
        c_soil[53] = 0.0056
        c_soil[54] = 0.0056
        c_soil[55] = 0
        c_soil[56] = 0
        c_soil[57] = 0.0056
        c_soil[58] = 0.0056
        c_soil[59] = 0.0056
        c_soil[60] = 0
        c_soil[61] = 0.00679
        c_soil[62] = 0.00679
        c_soil[63] = 0.00679
        c_soil[64] = 0.0056
        c_soil[65] = 0.0056
        c_soil[66] = 0
        c_soil[67] = 0
        c_soil[68] = 0.00679
        c_soil[69] = 0.00679
        c_soil[70] = 0.00679
        c_soil[71] = 0
        c_soil[72] = 0
        c_soil[73] = 0.0056
        c_soil[74] = 0.0056
        c_soil[75] = 0.0056
        c_soil[76] = 0.0056
        c_soil[77] = 0
        c_soil[78] = 0
        c_soil[79] = 0.0056
        c_soil[80] = 0
        c_soil[81] = 0
        c_soil[82] = 0.0061
        c_soil[83] = 0.0061
        c_soil[84] = 0.0061
        c_soil[85] = 0.0061
        c_soil[86] = 0.0061
        c_soil[87] = 0.0061

        # Collect species and number of plants
        esempl1 = self.parameterAsInt(parameters, self.ESEMPL1, context)
        specie1 = self.parameterAsInt(parameters, self.SPECIE1, context)
        esempl2 = self.parameterAsInt(parameters, self.ESEMPL2, context)
        specie2 = self.parameterAsInt(parameters, self.SPECIE2, context)
        esempl3 = self.parameterAsInt(parameters, self.ESEMPL3, context)
        specie3 = self.parameterAsInt(parameters, self.SPECIE3, context)
        esempl4 = self.parameterAsInt(parameters, self.ESEMPL4, context)
        specie4 = self.parameterAsInt(parameters, self.SPECIE4, context)
        esempl5 = self.parameterAsInt(parameters, self.ESEMPL5, context)
        specie5 = self.parameterAsInt(parameters, self.SPECIE5, context)

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        if (esempl1 == 0):
            c_above = {}
            c_above[1] = 0
            c_above[2] = 0
            c_above[3] = 0
            c_above[4] = 0
            c_above[5] = 0
            c_above[6] = 0
            c_above[7] = 0.000047
            c_above[8] = 0
            c_above[9] = 0.001439
            c_above[10] = 0
            c_above[11] = 0
            c_above[12] = 0
            c_above[13] = 0
            c_above[14] = 0
            c_above[15] = 0
            c_above[16] = 0
            c_above[17] = 0.000535
            c_above[18] = 0
            c_above[19] = 0.003
            c_above[20] = 0
            c_above[21] = 0.005
            c_above[22] = 0
            c_above[23] = 0.00029
            c_above[24] = 0
            c_above[25] = 0
            c_above[26] = 0.000073
            c_above[27] = 0
            c_above[28] = 0
            c_above[29] = 0.00003
            c_above[30] = 0
            c_above[31] = 0
            c_above[32] = 0.003
            c_above[33] = 0
            c_above[34] = 0
            c_above[35] = 0
            c_above[36] = 0
            c_above[37] = 0
            c_above[38] = 0.005
            c_above[39] = 0
            c_above[40] = 0
            c_above[41] = 0
            c_above[42] = 0
            c_above[43] = 0.0106
            c_above[44] = 0.003
            c_above[45] = 0
            c_above[46] = 0.000756
            c_above[47] = 0
            c_above[48] = 0.000756
            c_above[49] = 0
            c_above[50] = 0
            c_above[51] = 0
            c_above[52] = 0
            c_above[53] = 0.0003
            c_above[54] = 0
            c_above[55] = 0
            c_above[56] = 0
            c_above[57] = 0.00001
            c_above[58] = 0
            c_above[59] = 0
            c_above[60] = 0
            c_above[61] = 0
            c_above[62] = 0.00001
            c_above[63] = 0
            c_above[64] = 0
            c_above[65] = 0
            c_above[66] = 0
            c_above[67] = 0
            c_above[68] = 0
            c_above[69] = 0.00001
            c_above[70] = 0
            c_above[71] = 0
            c_above[72] = 0
            c_above[73] = 0
            c_above[74] = 0.00001
            c_above[75] = 0
            c_above[76] = 0
            c_above[77] = 0
            c_above[78] = 0
            c_above[79] = 0
            c_above[80] = 0
            c_above[81] = 0
            c_above[82] = 0.006
            c_above[83] = 0.02
            c_above[84] = 0.02
            c_above[85] = 0.0218
            c_above[86] = 0.016
            c_above[87] = 0.006

        # Calculate total carbon sequestration
        c_sequestration = c_sequestration_species[all_species[specie1]] * esempl1 +\
            c_sequestration_species[all_species[specie2]] * esempl2 +\
            c_sequestration_species[all_species[specie3]] * esempl3 + \
            c_sequestration_species[all_species[specie4]] * esempl4 +\
            c_sequestration_species[all_species[specie5]] * esempl5
        # Load present raster
        lucode_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        lucode_data_source = gdal.Open(lucode_raster.dataProvider().dataSourceUri())
        arr_lucode = lucode_data_source.GetRasterBand(1).ReadAsArray()
        [rows, cols] = arr_lucode.shape
        n_pixel_lucode = 0
        arr_c_above = np.zeros((rows, cols))
        arr_c_soil = np.zeros((rows, cols))
        arr_c_total = np.zeros((rows, cols))
        for lucode in np.unique(arr_lucode):
            try:
                arr_c_soil[np.where(arr_lucode == lucode)] = c_soil[lucode] * area_pixel
            except:
                pass
            if lucode in lucode_list:
                n_pixel_lucode += np.sum(np.where(arr_lucode == lucode))
                if esempl1 == 0:
                    arr_c_above[np.where(arr_lucode == lucode)] = c_above[lucode] * area_pixel
                else:
                    arr_c_above[np.where(arr_lucode == lucode)] = 1
        if n_pixel_lucode != 0:
            c_sequestration_pixel = c_sequestration / n_pixel_lucode
        else:
            c_sequestration_pixel = 0
        if esempl1 != 0:
            arr_c_above = arr_c_above * c_sequestration_pixel
        arr_c_total = arr_c_soil + arr_c_above
        # Initialize and write on output raster
        # Output parameters
        stati_list = ['Presente', 'Futuro']
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        stato = stati_list[self.parameterAsInt(parameters, self.FASE, context)]
        driver = gdal.GetDriverByName("GTiff")

        file_output = path_output + '/01_carbonio_' + stato + '_ton.tiff'
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(lucode_data_source.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(lucode_data_source.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_c_total)
        outdata.FlushCache()  ##saves to disk!!
        if n_pixel_lucode == 0 and esempl1 > 0:
            output_str = 'Attenzione sono stati inseriti alberi in un LUCODE che non prevede alberi'
        elif n_pixel_lucode == 0:
            output_str = 'Nessun LUCODE accetta alberi'
        elif (esempl1+esempl2+esempl3+esempl4+esempl5) / (n_pixel_lucode*area_pixel) > 1:
            output_str = "Attenzione sono stati inseriti più alberi di quanti l'area ne può contenetere"
        else:
            output_str = 'Completato'
        return {self.OUTPUT: output_str}

        
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

