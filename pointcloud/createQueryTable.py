# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 13:55:14 2016

@author: Stella Psomadaki
"""
from ConfigParser import ConfigParser
from pointcloud.CommonOracle import Oracle
import pointcloud.oracleTools as ora
import time
import sys


class Query(Oracle):
    def __init__(self, configuration):
        Oracle.__init__(self, configuration)
        
        config = ConfigParser()
        config.read(configuration)
        
        self.queriesTable = config.get('Querier', 'table')
        
    def createQueriesTable(self):
        """ Creates the query table where the actual queries posed to the 
        database are stored. Each query has and id, a dataset it belongs to,
        a type, geometry, the date ranges, the type of date querying and the
        range of heights."""
        connection = self.getConnection(False)
        cursor = connection.cursor()
        ora.mogrifyExecute(cursor, """CREATE TABLE {0} (
ID INTEGER PRIMARY KEY,
DATASET VARCHAR2(50),
TYPE VARCHAR2(50),
GEOMETRY SDO_GEOMETRY,
START_DATE DATE,
END_DATE DATE,
DATE_TYPE VARCHAR(20),
Z_MIN NUMBER,
Z_MAX NUMBER
)""".format(self.queriesTable))

    def getInsertInto(self, lst):
        connection = self.getConnection()
        cursor = connection.cursor()
        for i in lst:
            if i[3] != '':
                cursor.execute("INSERT INTO {0} VALUES (:1, :2, :3, SDO_UTIL.FROM_WKTGEOMETRY(:4), TO_DATE(:5, 'yyyy-mm-dd'), TO_DATE(:6, 'yyyy-mm-dd'), :7, :8, :9)".format(self.queriesTable), i)
            else:
                cursor.execute("INSERT INTO {0} (ID, DATASET, TYPE, START_DATE, END_DATE, DATE_TYPE, Z_MIN, Z_MAX) VALUES (:1, :2, :3, TO_DATE(:4, 'yyyy-mm-dd'), TO_DATE(:5, 'yyyy-mm-dd'), :6, :7, :8)".format(self.queriesTable), [i[0], i[1], i[2], i[4], i[5], i[6], i[7], i[8]])
        connection.commit()


if __name__ == "__main__":
    querier = Query(sys.argv[1])
    start = time.clock()
    querier.createQueriesTable()
    lst = [[1, 'zandmotor', 'space - time', 'POLYGON ((71028.591 451007.796, 71027.169 451654.613, 71715.212 451656.034, 71716.634 451006.374, 71028.591 451007.796))', '2000-1-3', '2000-1-28', 'discrete', None, None], #Whole January 2000
[2, 'zandmotor', 'space - time', 'POLYGON ((72453.010 451358.925, 72097.616 451671.672, 72755.806 452405.205, 73099.827 452119.468, 72453.010 451358.925))', '2001-11-10', None, 'discrete', None, None], #Two days in November
[3, 'zandmotor', 'space', 'POLYGON ((73205.024 452445.009, 73465.172 452762.020, 73537.673 452698.050, 73281.789 452379.617, 73205.024 452445.009))', None, None, None, None, None],
[4, 'zandmotor', 'space - time', """POLYGON ((73646.068 453916.696, 73719.990 454070.226, 73879.206 454132.775, 74038.423 454058.853, 74135.090 453933.754, 
74027.050 453837.087, 73896.265 453774.538, 73771.167 453723.361, 73651.754 453672.185, 73629.009 453649.439, 73543.714 453734.734, 73492.538 453831.401, 73646.068 453916.696))""", '2000-11-1', '2000-11-15', 'continuous', None, None], #one day in May 2007
[5, 'zandmotor', 'time', '', '2002-10-25', '2002-10-26', 'continuous', None, None], 
[6, 'zandmotor', 'space - time', 'POLYGON ((72346.747 453487.380, 72429.199 453578.360, 72702.141 453348.065, 72585.572 453265.614, 72346.747 453487.380))', '2001-8-1', '2001-8-31', 'continuous', None, None], #Whole August
[7, 'zandmotor', 'space', 'POLYGON ((72466.515 453045.625, 72498.501 453076.189, 72526.221 453048.468, 72493.525 453017.904, 72466.515 453045.625))', None, None, None, None, None],
[8, 'zandmotor', 'space', """POLYGON ((71813.546 452319.91, 71813.30523633362 452315.0091429835, 71812.58526402016 452310.1554838992, 71811.39301678661 452305.3957661372, 71809.73997662557 452300.7758283817,
71807.64206321743 452296.3401631587, 71805.11948061513 452292.131488349, 71802.19652266814 452288.1903357918, 71798.90133905933 452284.5546609407, 
71795.26566420819 452281.2594773318, 71791.32451165098 452278.3365193849, 71787.1158368413 452275.8139367825, 71782.68017161825 452273.7160233744, 
71778.06023386272 452272.0629832133, 71773.3005161008 452270.8707359798, 71768.44685701648 452270.1507636664, 71763.546 452269.91, 71758.64514298353 452270.1507636664, 
71753.7914838992 452270.8707359798, 71749.03176613728 452272.0629832133, 71744.41182838175 452273.7160233744, 71739.9761631587 452275.8139367825, 71735.76748834903 452278.3365193849, 
71731.82633579182 452281.2594773318, 71728.19066094067 452284.5546609407, 71724.89547733187 452288.1903357918, 71721.97251938487 452292.131488349, 71719.44993678258 452296.3401631587, 
71717.35202337444 452300.7758283817, 71715.6989832134 452305.3957661372, 71714.50673597984 452310.1554838992, 71713.78676366639 452315.0091429835, 71713.546 452319.91, 
71713.78676366639 452324.8108570165, 71714.50673597984 452329.6645161008, 71715.6989832134 452334.4242338627, 71717.35202337444 452339.0441716182, 71719.44993678258 452343.4798368413, 
71721.97251938487 452347.688511651, 71724.89547733187 452351.6296642082, 71728.19066094067 452355.2653390593, 71731.82633579182 452358.5605226681, 71735.76748834903 452361.4834806151, 
71739.9761631587 452364.0060632174, 71744.41182838175 452366.1039766255, 71749.03176613728 452367.7570167866, 71753.7914838992 452368.9492640201, 71758.64514298353 452369.6692363336, 
71763.546 452369.91, 71768.44685701648 452369.6692363336, 71773.3005161008 452368.9492640201, 71778.06023386272 452367.7570167866, 71782.68017161825 452366.1039766255, 
71787.1158368413 452364.0060632174, 71791.32451165098 452361.4834806151, 71795.26566420819 452358.5605226681, 71798.90133905933 452355.2653390593, 71802.19652266814 452351.6296642082, 
71805.11948061513 452347.688511651, 71807.64206321743 452343.4798368413, 71809.73997662557 452339.0441716182, 71811.39301678661 452334.4242338627, 71812.58526402016 452329.6645161008, 
71813.30523633362 452324.8108570165, 71813.546 452319.91))""", None, None, None, None, None], 
[9, 'zandmotor', 'space - time', """POLYGON ((70819.21379240759415552 451505.81215621629962698, 70818.19844500652106944 451507.00221665191929787, 
70817.60054114335798658 451508.44779098610160872, 70817.47860781406052411 451510.00737633113749325, 70817.84458070249820594 451511.52830960717983544, 70818.66263583242835011 451512.86171126819681376, 
70819.85269626801891718 451513.87705866928445175, 70821.29827060220122803 451514.47496253240387887, 70822.85785594723711256 451514.59689586173044518, 70824.37878922327945475 451514.23092297330731526, 
70825.71219088431098498 451513.41286784334806725, 71854.93321416419348679 450633.45732445898465812, 71855.94856156526657287 450632.26726402336498722, 71856.54646542842965573 450630.82168968918267637, 
71856.66839875772711821 450629.26210434414679185, 71856.30242586928943638 450627.74117106810444966, 71855.4843707393592922 450626.40776940708747134, 71854.29431030376872513 450625.39242200599983335, 
71852.84873596958641429 450624.79451814288040623, 71851.28915062455052976 450624.67258481355383992, 71849.76821734850818757 450625.03855770197696984, 71848.43481568747665733 450625.85661283193621784, 
70819.21379240759415552 451505.81215621629962698))""", '2001-8-1', '2001-8-31', 'continuous', None, None], 
[10, 'zandmotor', 'time', '', '2002-9-1', '2002-9-5', 'continuous', None, None],
[11, 'zandmotor', 'space', """POLYGON ((71973.22844887715473305 452196.72475540084997192, 71973.62372175263590179 452198.23833841446321458, 71974.46737147017847747 452199.55569536658003926, 
71975.67681571739376523 452200.54787418019259349, 71977.13366566465992946 452201.11775348003720865, 71978.69531468866625801 452201.2095495096873492, 
71980.20889770229405258 452200.81427663419162855, 71981.52625465442542918 452199.97062691661994904, 71982.51843346800887957 452198.76118266943376511, 
71983.08831276785349473 452197.30433272215304896, 71983.1801087975181872 452195.7426836981321685, 71897.88554885718622245 451331.42447630281094462, 
71897.49027598170505371 451329.91089328919770196, 71896.64662626416247804 451328.59353633708087727, 71895.43718201694719028 451327.60135752346832305, 
71893.98033206968102604 451327.03147822362370789, 71892.4186830456746975 451326.93968219397356734, 71890.90510003204690292 451327.33495506946928799, 
71889.58774307991552632 451328.17860478704096749, 71888.59556426633207593 451329.38804903422715142, 71888.02568496648746077 451330.84489898150786757, 
71887.9338889368227683 451332.40654800552874804, 71973.22844887715473305 452196.72475540084997192))""", None, None, None, None, None],
[12, 'zandmotor', 'space - time', """POLYGON ((74462.25559625300229527 454421.51267539517721161, 74463.47397299861768261 454422.49386461800895631, 74464.93592228640045505 454423.05053190211765468, 
74466.49833833402954042 454423.12818677531322464, 74468.00828097280464135 454422.71922783739864826, 74469.31794649682706222 454421.86368683871114627, 
74470.299135719644255 454420.64531009312486276, 74470.8558030037820572 454419.1833608053275384, 74470.9334578769194195 454417.62094475771300495, 
74470.52449893903394695 454416.11100211890880018, 74469.66895794036099687 454414.80133659491548315, 73110.64230289137049112 452913.61708164535230026, 
73109.42392614575510379 452912.63589242252055556, 73107.96197685797233135 452912.07922513841185719, 73106.39956081034324598 452912.00157026521628723, 
73104.88961817156814504 452912.41052920313086361, 73103.57995264754572418 452913.2660702018183656, 73102.59876342472853139 452914.48444694740464911, 
73102.04209614059072919 452915.94639623520197347, 73101.96444126745336689 452917.50881228281650692, 73102.37340020533883944 452919.01875492162071168, 
73103.22894120401178952 452920.32842044561402872, 74462.25559625300229527 454421.51267539517721161))""", '2002-1-1', '2002-1-15', 'continuous', None, None],
[13, 'coastline', 'space-time', 'Polygon ((66851.65212216849613469 444813.01858679699944332, 66854.90659376935218461 445061.81774144159862772, 67140.0075518303347053 445059.62822892342228442, 67137.70727960603835527 444810.49114539328729734, 66851.65212216849613469 444813.01858679699944332))', '2012-1-1', '2015-1-1', 'discrete', None, None],
[14, 'coastline', 'space', 'Polygon ((68211.07290297294093762 446131.93240472121397033, 68211.07290297400322743 446169.7294939233106561, 68269.15135712825576775 446171.5732543739140965, 68267.30759667788515799 446131.01052450120914727, 68211.07290297294093762 446131.93240472121397033))', None, None, None, None, None],
[15, 'coastline', 'space - time', 'Polygon ((68739.31027173917391337 447295.34524793160380796, 68901.56119128532009199 447453.90864653018070385, 68938.43640027171932161 447431.78352114791050553, 68787.24804342121933587 447262.157559854676947, 68739.31027173917391337 447295.34524793160380796))', '2012-1-1', '2013-1-1', 'continuous', None, None],
[16, 'coastline', 'space - time', 'Polygon ((70711.21207237253838684 449756.7654471262358129, 70740.71223956291214563 449791.79689565300941467, 70834.74402247759280726 449721.73399860528297722, 70801.55633438868972007 449690.39007097081048414, 70711.21207237253838684 449756.7654471262358129))', '2013-1-1', '2015-1-1', 'continuous', None, None],
[17, 'coastline', 'space - time', 'Polygon ((73130.39952723562601022 452632.01089005719404668, 73423.64996279755723663 452379.20879051234805956, 73282.0807870017742971 452200.56197349308058619, 72992.20104610147245694 452449.99337837909115478, 73130.39952723562601022 452632.01089005719404668))', '2014-1-1', None, 'discrete', None, None],
[18, 'coastline', 'space', 'Polygon ((74252.84084960828477051 453735.91339146654354408, 74303.40126953480648808 453776.36172739759786054, 74359.01773145154584199 453725.8013074878253974, 74310.14265885601344053 453685.3529715544427745, 74252.84084960828477051 453735.91339146654354408))', None, None, None, None, None],
[19, 'coastline', 'space - time', 'Polygon ((75674.4313232162676286 455278.84887242905097082, 75845.49407730204984546 455470.13579443347407505, 75856.44883495230169501 455458.3383631159667857, 75694.65549118620401714 455262.83807279309257865, 75674.4313232162676286 455278.84887242905097082))', '2012-1-1', '2015-1-1', 'continuous', None, None],
[20, 'coastline', 'space - time', 'Polygon ((68216.31 447065.11, 68215.16 447066.17, 68214.40 447067.54, 68214.10 447069.07, 68214.28 447070.63, 68214.94 447072.05, 68216.00 447073.19, 68217.37 447073.96, 68218.90 447074.26, 68220.45 447074.08, 68221.87 447073.42, 69210.92 446411.33, 69212.07 446410.26, 69212.83 446408.90, 69213.14 446407.36, 69212.95 446405.81, 69212.30 446404.39, 69211.23 446403.24, 69209.87 446402.48, 69208.33 446402.18, 69206.78 446402.36, 69205.36 446403.02, 68216.31 447065.11))', '2012-1-1', '2015-1-1', 'continuous', None, None],
[21, 'coastline', 'space - time', 'Polygon ((68927.10 447779.62, 68925.99 447780.72, 68925.28 447782.12, 68925.03 447783.66, 68925.26 447785.21, 68925.97 447786.60, 68927.07 447787.71, 68928.46 447788.43, 68930.01 447788.68, 68931.55 447788.44, 68932.95 447787.74, 69884.94 447102.19, 69886.05 447101.09, 69886.77 447099.70, 69887.02 447098.16, 69886.78 447096.61, 69886.08 447095.21, 69884.97 447094.10, 69883.58 447093.39, 69882.04 447093.14, 69880.49 447093.37, 69879.10 447094.08, 68927.10 447779.62))', '2014-1-1', '2015-1-1', 'continuous', None, None],
[22, 'coastline', 'space', 'Polygon ((69427.56 448685.49, 69426.41 448686.55, 69425.65 448687.91, 69425.34 448689.44, 69425.52 448691.00, 69426.17 448692.42, 69427.23 448693.57, 69428.59 448694.34, 69430.13 448694.64, 69431.68 448694.46, 69433.10 448693.81, 70446.17 448019.59, 70447.32 448018.53, 70448.08 448017.17, 70448.39 448015.64, 70448.21 448014.08, 70447.56 448012.66, 70446.50 448011.51, 70445.13 448010.74, 70443.60 448010.44, 70442.05 448010.62, 70440.62 448011.27, 69427.56 448685.49))', None, None, None, None, None],
[23, 'coastline', 'space - time', 'Polygon ((70162.10 449493.18, 70161.07 449494.37, 70160.47 449495.81, 70160.34 449497.37, 70160.69 449498.89, 70161.50 449500.23, 70162.69 449501.25, 70164.13 449501.86, 70165.69 449501.99, 70167.21 449501.63, 70168.55 449500.82, 71094.35 448718.84, 71095.37 448717.65, 71095.98 448716.21, 71096.11 448714.65, 71095.75 448713.13, 71094.94 448711.79, 71093.76 448710.77, 71092.32 448710.16, 71090.76 448710.03, 71089.23 448710.39, 71087.90 448711.20, 70162.10 449493.18))', '2013-1-1', '2014-1-1', 'continuous', None, None],
[24, 'coastline', 'space - time', 'Polygon ((70677.81 450159.10, 70676.79 450160.29, 70676.19 450161.73, 70676.07 450163.29, 70676.43 450164.81, 70677.24 450166.15, 70678.43 450167.17, 70679.88 450167.77, 70681.43 450167.89, 70682.96 450167.53, 70684.29 450166.72, 71676.08 449323.03, 71677.10 449321.84, 71677.70 449320.40, 71677.83 449318.84, 71677.46 449317.32, 71676.65 449315.98, 71675.46 449314.96, 71674.02 449314.36, 71672.46 449314.24, 71670.94 449314.60, 71669.60 449315.41, 70677.81 450159.10))', '2012-1-1', '2014-1-1', 'continuous', None, None],
[25, 'coastline', 'space - time', 'Polygon ((71268.91 450667.28, 71267.86 450668.44, 71267.22 450669.87, 71267.05 450671.42, 71267.37 450672.96, 71268.15 450674.31, 71269.31 450675.36, 71270.73 450676.00, 71272.29 450676.17, 71273.82 450675.85, 71275.18 450675.07, 72231.60 449905.15, 72232.65 449903.99, 72233.29 449902.56, 72233.46 449901.01, 72233.14 449899.47, 72232.36 449898.12, 72231.20 449897.07, 72229.77 449896.43, 72228.22 449896.26, 72226.69 449896.58, 72225.33 449897.36, 71268.91 450667.28))', '2013-1-1', '2015-1-1', 'continuous', None, None],
[26, 'coastline', 'space - time', 'Polygon ((71690.81335704486991744 451384.11627048836089671, 71689.80015979999734554 451385.30816206405870616, 71689.20486671032267623 451386.75481348118046299, 71689.08574921109538991 451388.31461641954956576, 71689.45446735309087671 451389.83488649985520169, 71690.27492843555228319 451391.16680909419665113, 71691.46682001126464456 451392.18000633909832686, 71692.91347142837184947 451392.77529942878754809, 71694.47327436675550416 451392.8944169280002825, 71695.99354444704658817 451392.52569878601934761, 71697.32546704141714144 451391.70523770351428539, 72679.89100693447107915 450548.56351720605744049, 72680.90420417934365105 450547.37162563035963103, 72681.49949726901832037 450545.92497421323787421, 72681.61861476824560668 450544.36517127486877143, 72681.24989662625011988 450542.8449011945631355, 72680.4294355437887134 450541.51297860022168607, 72679.23754396807635203 450540.49978135532001033, 72677.79089255096914712 450539.9044882656307891, 72676.23108961258549243 450539.7853707664180547, 72674.71081953229440842 450540.15408890839898959, 72673.37889693792385515 450540.97454999090405181, 71690.81335704486991744 451384.11627048836089671))', '2012-1-1', '2013-1-1', 'continuous', None, None],
[27, 'coastline', 'space - time', 'Polygon ((71723.35579855591640808 452341.8033829721971415, 71722.32947805018920917 452342.98399315541610122, 71721.71821785575593822 452344.42397064133547246, 71721.58185237935686018 452345.98236040066694841, 71721.93373002392763738 452347.5066163859446533, 71722.73940655394108035 452348.84753380104666576, 71723.92001673717459198 452349.87385430681752041, 71725.35999422309396323 452350.48511450120713562, 71726.918383982454543 452350.62147997762076557, 71728.44263996767404024 452350.2696023330790922, 71729.78355738281970844 452349.46392580302199349, 72775.58556857962685172 451471.9591252842801623, 72776.61188908535405062 451470.77851510106120259, 72777.22314927978732157 451469.33853761514183134, 72777.35951475618639961 451467.7801478558103554, 72777.00763711161562242 451466.2558918705326505, 72776.20196058160217945 451464.91497445543063805, 72775.02135039836866781 451463.88865394965978339, 72773.58137291244929656 451463.27739375527016819, 72772.02298315308871679 451463.14102827885653824, 72770.49872716786921956 451463.4929059233982116, 72769.15780975272355136 451464.29858245345531031, 71723.35579855591640808 452341.8033829721971415))', '2013-1-1', '2015-1-1', 'continuous', None, None],
[28, 'coastline', 'space - time', 'Polygon ((72111.31630785080778878 452766.83259373676264659, 72110.27965050304192118 452768.00413790089078248, 72109.6557578336505685 452769.43868735013529658, 72109.50570080404577311 452770.99581838928861544, 72109.84416804178908933 452772.52310818311525509, 72110.63802801541169174 452773.87105496524600312, 72111.80957217955437955 452774.9077123129973188, 72113.24412162879889365 452775.53160498238867149, 72114.80125266796676442 452775.68166201200801879, 72116.32854246174974833 452775.3431947742938064, 72117.67648924390960019 452774.54933480062754825, 73148.67243266705190763 451924.79667866963427514, 73149.70909001481777523 451923.62513450550613925, 73150.33298268420912791 451922.19058505626162514, 73150.4830397138139233 451920.63345401710830629, 73150.14457247607060708 451919.10616422328166664, 73149.35071250244800467 451917.7582174411509186, 73148.17916833830531687 451916.72156009339960292, 73146.74461888906080276 451916.09766742400825024, 73145.18748784989293199 451915.94761039438890293, 73143.66019805610994808 451916.28607763210311532, 73142.31225127395009622 451917.07993760576937348, 72111.31630785080778878 452766.83259373676264659))', '2012-1-1', '2015-1-1', 'continuous', None, None],
[29, 'coastline', 'space - time', 'Polygon ((72558.11664289236068726 453257.77836956264218315, 72557.08923889676225372 453258.95803697977680713, 72556.47665691150177736 453260.39745265862438828, 72556.33886072938912548 453261.95571656356332824, 72556.68933880081749521 453263.48029496648814529, 72557.49378389022604097 453264.82195151102496311, 72558.67345130737521686 453265.84935550659429282, 72560.11286698623734992 453266.46193749184021726, 72561.67113089117628988 453266.59973367396742105, 72563.19570929411565885 453266.24925560253905132, 72564.53736583859426901 453265.44481051311595365, 73619.32529395185702015 452382.04909962497185916, 73620.35269794745545369 452380.86943220783723518, 73620.96527993271593004 452379.43001652898965403, 73621.10307611482858192 452377.87175262405071408, 73620.75259804340021219 452376.34717422112589702, 73619.94815295399166644 452375.0055176765890792, 73618.76848553684249055 452373.97811368101974949, 73617.32906985798035748 452373.36553169577382505, 73615.77080595304141752 452373.22773551364662126, 73614.24622755010204855 452373.57821358507499099, 73612.9045710056234384 452374.38265867449808866, 72558.11664289236068726 453257.77836956264218315))', '2012-1-1', '2013-1-1', 'continuous', None, None],
[30, 'coastline', 'space - time', 'Polygon ((73342.42693827686889563 453575.68044414313044399, 73341.34167072892887518 453576.80710670782718807, 73340.65767783494084142 453578.21399259736062959, 73340.44191358503303491 453579.76338601857423782, 73340.71549848729046062 453581.30362154811155051, 73341.45165214533335529 453582.68393020093208179, 73342.57831471000099555 453583.76919774885755032, 73343.98520059954898898 453584.45319064287468791, 73345.53459402076259721 453584.66895489278249443, 73347.07482955031446181 453584.39536999049596488, 73348.45513820312044118 453583.65921633248217404, 74359.54340819633216597 452819.75192709424300119, 74360.62867574427218642 452818.62526452954625711, 74361.31266863826022018 452817.21837864001281559, 74361.52843288816802669 452815.66898521879920736, 74361.25484798591060098 452814.12874968926189467, 74360.51869432786770631 452812.74844103644136339, 74359.39203176320006605 452811.66317348851589486, 74357.98514587365207262 452810.97918059449875727, 74356.43575245243846439 452810.76341634459095076, 74354.89551692288659979 452811.0370012468774803, 74353.51520827008062042 452811.77315490489127114, 73342.42693827686889563 453575.68044414313044399))', '2014-1-1', '2015-1-1', 'continuous', None, None],
[31, 'coastline', 'space - time', 'Polygon ((74353.66838127527444158 454170.81510975171113387, 74352.66030010585382115 454172.01133152929833159, 74352.071210799011169 454173.46052025881363079, 74351.95877752055821475 454175.02081925037782639, 74352.33400602312758565 454176.53949556750012562, 74353.16016632654645946 454177.86789059091825038, 74354.35638810409000143 454178.87597176036797464, 74355.80557683363440447 454179.46506106719607487, 74357.36587582521315198 454179.57749434566358104, 74358.88455214230634738 454179.20226584305055439, 74360.21294716575357597 454178.37610553967533633, 75261.40703643298184033 453398.33016149653121829, 75262.41511760240246076 453397.13393971894402057, 75263.00420690924511291 453395.68475098942872137, 75263.11664018769806717 453394.12445199786452577, 75262.74141168512869626 453392.60577568074222654, 75261.91525138170982245 453391.27738065732410178, 75260.71902960416628048 453390.26929948787437752, 75259.26984087462187745 453389.68021018104627728, 75257.70954188304312993 453389.56777690257877111, 75256.19086556594993453 453389.94300540519179776, 75254.86247054250270594 453390.76916570856701583, 74353.66838127527444158 454170.81510975171113387))', '2013-1-1', '2014-1-1', 'continuous', None, None],
[32, 'coastline', 'space - time', 'Polygon ((74974.06265912330127321 455099.80001361685572192, 74972.97670905906124972 455100.92601834295783192, 74972.29186377019505017 455102.33248949999688193, 74972.07516068518452812 455103.88175189163303003, 74972.3478122118540341 455105.42215292068431154, 74973.08312931908585597 455106.80290740175405517, 74974.20913404518796597 455107.88885746599407867, 74975.61560520222701598 455108.57370275486027822, 74977.16486759387771599 455108.79040583985624835, 74978.70526862289989367 455108.51775431318674237, 74980.08602310399874114 455107.7824372059549205, 75967.03465316125948448 454363.05237337190192193, 75968.12060322549950797 454361.92636864579981193, 75968.80544851436570752 454360.51989748876076192, 75969.02215159937622957 454358.97063509712461382, 75968.74950007270672359 454357.43023406807333231, 75968.01418296547490172 454356.04947958700358868, 75966.88817823937279172 454354.96352952276356518, 75965.48170708233374171 454354.27868423389736563, 75963.9324446906830417 454354.0619811489013955, 75962.39204366166086402 454354.33463267557090148, 75961.01128918056201655 454355.06994978280272335, 74974.06265912330127321 455099.80001361685572192))','2012-1-1', '2013-1-1', 'continuous', None, None],
[33, 'coastline', 'space - time', 'Polygon ((75518.84863087696430739 456062.41342190181603655, 75517.83093675720738247 456063.60147613618755713, 75517.23018108167161699 456065.04586763557745144, 75517.10517000159597956 456066.60520929639460519, 75517.46814047251245938 456068.12686189223313704, 75518.28356241574510932 456069.4618754651164636, 75519.47161665013118181 456070.47956958488794044, 75520.91600814953562804 456071.080325260409154, 75522.47534981033822987 456071.20533634047023952, 75523.99700240619131364 456070.84236586955375969, 75525.33201597906008828 456070.02694392629200593, 76426.54666167963296175 455302.58690909104188904, 76427.56435579938988667 455301.39885485667036846, 76428.16511147492565215 455299.95446335728047416, 76428.29012255500128958 455298.3951216964633204, 76427.92715208408480976 455296.87346910062478855, 76427.11173014085215982 455295.53845552774146199, 76425.92367590646608733 455294.52076140796998516, 76424.4792844070616411 455293.9200057324487716, 76422.91994274625903927 455293.79499465238768607, 76421.3982901504059555 455294.1579651233041659, 76420.06327657753718086 455294.97338706656591967, 75518.84863087696430739 456062.41342190181603655))', '2014-1-1', '2015-1-1', 'continuous', None, None]
]

    querier.getInsertInto(lst)
    
    print 'query table: {0:.2f} seconds'.format(time.clock() - start)

    