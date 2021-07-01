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
from qgis import processing
import pandas as pd
import gdal
import numpy as np
import os

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
    CONC='CONC'
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
    FASE = 'FASE'
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
        return 'Calcolo Infiltrazione'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Calcolo Infiltrazione')

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
        return self.tr("Calcolo Infiltrazione")

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

        double_param = QgsProcessingParameterNumber(
            self.CONC,
            self.tr('Totale cumulato delle precipitazioni [mm]'),
            QgsProcessingParameterNumber.Double,
            55.32
        )
        double_param.setMetadata( {'widget_wrapper': { 'decimals': 2 }} )
        self.addParameter(double_param)

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
            QgsProcessingParameterEnum(
                self.FASE,
                self.tr('Fase di lavoro'),
                fasi,
                defaultValue=''
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
        all_species = ['Abete (Picea abies, glauca, omorika, orientalis, pungens)',
                       'Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)',
                       'Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)',
                       'Bagolaro (Celtis australis, occidentalis)',
                       'Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)',
                       'Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)',
                       'Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)',
                       'Frassino (Fraxinus americana, excelsior, excelsior Pendula)',
                       'Ippocastano (Aesculus hippocastanum, pavia)', 'Olmo  (Ulmus laevis, minor,parvifolia,pumila)',
                       'Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)',
                       'Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)',
                       'Platano (Platanus orientalis, occidentalis, hybrida)',
                       'Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)',
                       'Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)']
        # Initialize dicionary of c sequestration per species
        lai_species = {}
        lai_species['Abete (Picea abies, glauca, omorika, orientalis, pungens)'] = 0.18
        lai_species[
            'Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)'] = 0, 41
        lai_species['Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)'] = 0.34
        lai_species['Bagolaro (Celtis australis, occidentalis)'] = 0.75
        lai_species['Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)'] = 0.38
        lai_species['Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)'] = 0.39
        lai_species[
            'Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)'] = 0.2
        lai_species['Frassino (Fraxinus americana, excelsior, excelsior Pendula)'] = 0.35
        lai_species['Ippocastano (Aesculus hippocastanum, pavia)'] = 0.44
        lai_species['Olmo  (Ulmus laevis, minor,parvifolia,pumila)'] = 0.48
        lai_species['Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)'] = 0.31
        lai_species['Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)'] = 0.67
        lai_species['Platano (Platanus orientalis, occidentalis, hybrida)'] = 0.7
        lai_species['Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)'] = 0.44
        lai_species['Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)'] = 0.28

        # Collect species and number of plants
        esempl1 = self.parameterAsInt(parameters, self.ESEMPL1, context)
        specie1 = all_species[self.parameterAsInt(parameters, self.SPECIE1, context)]
        esempl2 = self.parameterAsInt(parameters, self.ESEMPL2, context)
        specie2 = all_species[self.parameterAsInt(parameters, self.SPECIE2, context)]
        esempl3 = self.parameterAsInt(parameters, self.ESEMPL3, context)
        specie3 = all_species[self.parameterAsInt(parameters, self.SPECIE3, context)]
        esempl4 = self.parameterAsInt(parameters, self.ESEMPL4, context)
        specie4 = all_species[self.parameterAsInt(parameters, self.SPECIE4, context)]
        esempl5 = self.parameterAsInt(parameters, self.ESEMPL5, context)
        specie5 = all_species[self.parameterAsInt(parameters, self.SPECIE5, context)]
        conc = self.parameterAsDouble(parameters, self.CONC, context)
        # Load present raster
        lucode_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        lucode = gdal.Open(lucode_raster.dataProvider().dataSourceUri())
        arr_lucode = lucode.GetRasterBand(1).ReadAsArray()
        [rows, cols] = arr_lucode.shape

        arr_R = np.zeros((rows, cols))
        R = {}
        R[1] = 27.60400151
        R[2] = 27.65534109
        R[3] = 27.83315114
        R[4] = 18.55834169
        R[5] = 19.51634168
        R[6] = 10.21394173
        R[7] = 36.28438303
        R[8] = 48.82785829
        R[9] = 15.97138114
        R[10] = 14.51422075
        R[11] = 48.72852875
        R[12] = 28.895582
        R[13] = 48.51622416
        R[14] = 27.37849683
        R[15] = 49.36813124
        R[16] = 27.96605852
        R[17] = 14.11070066
        R[18] = 48.66588942
        R[19] = 36.22383741
        R[20] = 41.17580981
        R[21] = 15.40753778
        R[22] = 15.48867479
        R[23] = 29.70774627
        R[24] = 29.42066395
        R[25] = 48.13092135
        R[26] = 17.76264172
        R[27] = 18.11290607
        R[28] = 1.64163875
        R[29] = 19.36504103
        R[30] = 20.1104968
        R[31] = 0.30421411
        R[32] = 25.66532488
        R[33] = 26.12120455
        R[34] = 20.76559967
        R[35] = 34.38456041
        R[36] = 22.09414157
        R[37] = 14.95357739
        R[38] = 32.49942893
        R[39] = 32.05539278
        R[40] = 26.35653383
        R[41] = 27.56389486
        R[42] = 24.82414581
        R[43] = 33.12276817
        R[44] = 49.44629515
        R[45] = 0.14467594
        R[46] = 49.36724941
        R[47] = 49.02557087
        R[48] = 33.66124269
        R[49] = 33.64659491
        R[50] = 49.19989099
        R[51] = 48.84244489
        R[52] = 48.15353889
        R[53] = 33.81907603
        R[54] = 33.28475863
        R[55] = 48.5761149
        R[56] = 47.62077389
        R[57] = 19.94862889
        R[58] = 21.64782865
        R[59] = 27.17783869
        R[60] = 47.79304172
        R[61] = 9.67848073
        R[62] = 12.39895263
        R[63] = 11.01411266
        R[64] = 22.11736761
        R[65] = 18.29311943
        R[66] = 44.99975679
        R[67] = 49.1108194
        R[68] = 8.11029308
        R[69] = 9.2286522
        R[70] = 11.40581743
        R[71] = 32.50563592
        R[72] = 49.19309454
        R[73] = 28.18575417
        R[74] = 28.25313891
        R[75] = 23.66870937
        R[76] = 28.21083467
        R[77] = 48.10130333
        R[78] = 0.12401461
        R[79] = 33.2333038
        R[80] = 34.07063753
        R[81] = 34.0654219
        R[82] = 13.07725357
        R[83] = 10.47765199
        R[84] = 11.55907612
        R[85] = 14.80240343
        R[86] = 14.46532371
        R[87] = 15.27980652

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        for lucode_key in R.keys():
            arr_R[np.where(arr_lucode == lucode_key)] = R[lucode_key]
        runoff_total = np.sum(arr_R)
        if (esempl1 > 0):
            list_species = [specie1, specie2, specie3, specie4, specie5]
            list_esempl = [esempl1, esempl2, esempl3, esempl4, esempl5]
            Sv = 0
            for specie_id, specie in enumerate(list_species):
                Smax = 0.935 + 0.498 * lai_species[specie] * list_esempl[specie_id] - \
                       0.00575 * lai_species[specie] * list_esempl[specie_id]
                nu = 0.046 * lai_species[specie] * list_esempl[specie_id]
                print('Smax', Smax)
                Sv += Smax * (1 - np.exp(-nu * (conc / Smax)))
        else:
            lai_lucode = {}
            lai_lucode[1] = 0
            lai_lucode[2] = 0
            lai_lucode[3] = 0
            lai_lucode[4] = 0
            lai_lucode[5] = 0
            lai_lucode[6] = 0
            lai_lucode[7] = 0.21
            lai_lucode[8] = 0
            lai_lucode[9] = 0.08
            lai_lucode[10] = 0
            lai_lucode[11] = 0
            lai_lucode[12] = 0
            lai_lucode[13] = 0
            lai_lucode[14] = 0
            lai_lucode[15] = 0
            lai_lucode[16] = 0
            lai_lucode[17] = 0.39
            lai_lucode[18] = 0
            lai_lucode[19] = 0.02
            lai_lucode[20] = 0
            lai_lucode[21] = 0.88
            lai_lucode[22] = 0
            lai_lucode[23] = 0.02
            lai_lucode[24] = 0
            lai_lucode[25] = 0
            lai_lucode[26] = 0.02
            lai_lucode[27] = 0
            lai_lucode[28] = 0
            lai_lucode[29] = 0.02
            lai_lucode[30] = 0
            lai_lucode[31] = 0
            lai_lucode[32] = 0.02
            lai_lucode[33] = 0
            lai_lucode[34] = 0
            lai_lucode[35] = 0
            lai_lucode[36] = 0
            lai_lucode[37] = 0
            lai_lucode[38] = 0.02
            lai_lucode[39] = 0
            lai_lucode[40] = 0
            lai_lucode[41] = 0
            lai_lucode[42] = 0
            lai_lucode[43] = 1.22
            lai_lucode[44] = 1.22
            lai_lucode[45] = 0
            lai_lucode[46] = 0.53
            lai_lucode[47] = 0
            lai_lucode[48] = 0.53
            lai_lucode[49] = 0
            lai_lucode[50] = 0
            lai_lucode[51] = 0
            lai_lucode[52] = 0
            lai_lucode[53] = 0.02
            lai_lucode[54] = 0
            lai_lucode[55] = 0
            lai_lucode[56] = 0
            lai_lucode[57] = 0
            lai_lucode[58] = 0
            lai_lucode[59] = 0
            lai_lucode[60] = 0
            lai_lucode[61] = 0
            lai_lucode[62] = 0.02
            lai_lucode[63] = 0
            lai_lucode[64] = 0
            lai_lucode[65] = 0
            lai_lucode[66] = 0
            lai_lucode[67] = 0
            lai_lucode[68] = 0
            lai_lucode[69] = 0.02
            lai_lucode[70] = 0.02
            lai_lucode[71] = 0
            lai_lucode[72] = 0
            lai_lucode[73] = 0
            lai_lucode[74] = 0.02
            lai_lucode[75] = 0
            lai_lucode[76] = 0
            lai_lucode[77] = 0
            lai_lucode[78] = 0
            lai_lucode[79] = 0
            lai_lucode[80] = 0
            lai_lucode[81] = 0
            lai_lucode[82] = 0.88
            lai_lucode[83] = 0.88
            lai_lucode[84] = 0.88
            lai_lucode[85] = 0.88
            lai_lucode[86] = 0.88
            lai_lucode[87] = 0.88

            Sv = np.zeros((rows, cols))
            for lucode_key in lai_lucode.keys():
                Smax = 0.935 + 0.498 * lai_lucode[lucode_key] * area_pixel - \
                       0.00575 * lai_lucode[lucode_key] * area_pixel
                nu = 0.046 * lai_lucode[lucode_key] * area_pixel
                Sv[np.where(arr_lucode == lucode_key)] = Smax * (1 - np.exp(-nu * (conc / Smax)))
        I = conc - (arr_R + Sv)
        # Initialize and write on output raster
        # Output parameters
        stati_list = ['presente', 'futuro']
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        stato = stati_list[self.parameterAsInt(parameters, self.FASE, context)]
        driver = gdal.GetDriverByName("GTiff")

        file_output = path_output + '/05_infiltrazione_' + stato + '_mm.tiff'
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(lucode.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(lucode.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(I)
        outdata.FlushCache()  ##saves to disk!!
        outdata = None
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

