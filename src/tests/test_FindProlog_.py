import typing

import pytest
import sys

import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.AlignerImproved.CHelperClearnPrologs import CHelper_CleanerTexts, CMergingInfo


def test_function1():
    assert 2==2


def test_function2():
    assert True==True

@pytest.fixture
def data_prolog_v1()->typing.List[typing.Tuple[int,bool,int]]:
    test_data = [(1531, True, 7),
                 (1530, True, 119),
                 (1529, True, 198),
                 (1528, True, 233),
                 (1527, False, 1),
                 (1526, False, 1),
                 (1525, False, 1),
                 (1524, True, 70),
                 (1523, True, 235),
                 (1522, True, 115),
                 (1521, True, 104),
                 (1520, True, 119),
                 (1519, True, 167),
                 (1518, True, 253),
                 (1517, True, 120),
                 (1516, True, 235),
                 (1515, True, 84),
                 (1514, True, 166),
                 (1513, True, 188),
                 (1512, True, 179),
                 (1511, True, 236),
                 (1510, True, 76),
                 (1509, True, 62),
                 (1508, True, 28),
                 (1507, True, 180),
                 (1506, True, 285),
                 (1505, True, 80),
                 (1504, True, 66),
                 (1503, True, 128),
                 (1502, False, 2),
                 (1501, True, 270),
                 (1500, False, 36),
                 (1499, True, 171),
                 (1498, True, 49),
                 (1497, True, 44),
                 (1496, False, 2),
                 (1495, True, 177),
                 (1494, True, 363),
                 (1493, True, 126),
                 (1492, True, 89)]
    return  test_data

@pytest.fixture
def prolog_v2()->typing.List[typing.Tuple[int,bool,int]]:
    test_data = [(0, True, 47, 0),
                 (1, True, 20, 82),
                 (2, True, 112, 6),
                 (3, True, 24, 84),
                 (4, True, 21, 84),
                 (5, True, 34, 13),
                 (6, True, 168, 10),
                 (7, True, 163, 18),
                 (8, True, 180, 10),
                 (9, False, 35, 12),
                 (10, False, 28, 13927),
                 (11, True, 281, 85),
                 (12, True, 195, 86),
                 (13, True, 146, 87),
                 (14, True, 148, 88),
                 (15, True, 100, 89),
                 (16, True, 18, 84),
                 (17, True, 22, 83),
                 (18, True, 21, 91),
                 (19, True, 168, 92),
                 (20, True, 219, 93),
                 (21, True, 139, 92),
                 (22, True, 158, 94),
                 (23, True, 385, 95),
                 (24, True, 144, 96),
                 (25, True, 202, 97),
                 (26, True, 196, 98),
                 (27, True, 87, 99),
                 (28, True, 114, 99),
                 (29, True, 138, 100),
                 (30, True, 188, 100),
                 (31, True, 207, 101),
                 (32, True, 211, 102),
                 (33, False, 16, 10139),
                 (34, True, 66, 104),
                 (35, True, 52, 105),
                 (36, True, 221, 106),
                 (37, True, 300, 108),
                 (38, True, 154, 109),
                 (39, True, 185, 109),]

    return  test_data
@pytest.fixture
def prolog_v3()->typing.List[typing.Tuple[int,bool,int]]:
    test_data =   test_dt = [(0, False, 82, 5),
                             (1, False, 70, 5),
                             (2, False, 18, 5),
                             (3, False, 21, 6),
                             (4, False, 13, 1732),
                             (5, False, 76, 1),
                             (6, False, 77, 3485),
                             (7, False, 69, 4974),
                             (8, False, 26, 6),
                             (9, False, 17, 583),
                             (10, True, 41, 7),
                             (11, True, 71, 7),
                             (12, True, 83, 11),
                             (13, True, 77, 8),
                             (14, True, 67, 13),
                             (15, True, 43, 13),
                             (16, True, 18, 10),
                             (17, True, 58, 13),
                             (18, True, 29, 12),
                             (19, True, 69, 13),
                             (20, True, 34, 15),
                             (21, True, 60, 15),
                             (22, True, 15, 16),
                             (23, True, 131, 18),
                             (24, True, 144, 22),
                             (25, True, 40, 22),
                             (26, True, 41, 21),
                             (27, True, 48, 25),
                             (28, True, 45, 23),
                             (29, True, 41, 27),
                             (30, True, 36, 25),
                             (31, True, 47, 28),
                             (32, True, 53, 27),
                             (33, True, 64, 30),
                             (34, True, 51, 29),
                             (35, True, 71, 30),
                             (36, True, 44, 32),
                             (37, True, 44, 32),
                             (38, True, 53, 33),
                             (39, True, 109, 35), ]

    return  test_data
@pytest.fixture
def prolog_v4()->typing.List[typing.Tuple[int,bool,int]]:
    test_data =[(5213, True, 125, 5236),
                (5212, False, 39, 4266),
                (5208, True, 26, 5232),
                (5207, True, 109, 5231),
                (5206, True, 137, 5230),
                (5205, True, 263, 5229),
                (5204, True, 91, 5228),
                (5203, False, 54, 551),
                (5202, True, 210, 5227),
                (5201, True, 119, 5226),
                (5198, True, 29, 5223),
                (5197, True, 186, 5222),
                (5194, True, 83, 5220),
                (5193, True, 33, 5219),
                (5192, True, 70, 5218),
                (5191, True, 82, 5217),
                (5190, True, 162, 5216),
                (5189, True, 238, 5215),
                (5188, True, 51, 5213),
                (5187, True, 31, 5213),
                (5186, True, 67, 5212),
                (5185, True, 106, 5211),
                ]
    return  test_data

@pytest.fixture
def data_prolog_v6()->typing.List[typing.Tuple[int,bool,int]]:
    res = [
        (5246, False, 183, 3474),
         (5245, False, 7, 1232),
        (5244, False, 122, 894),
    (5243, False, 7, 1232),
    (5242, False, 69, 1755),
    (5241, False, 13, 1232),
    (5240, False, 182, 595),
    (5239, False, 13, 3670),
    (5238, False, 6, 5152),
    (5237, False, 37, 4708),
    (5236, True, 96, 5213),
    (5235, False, 8, 174),
    (5234, False, 4, 1419),
    (5233, True, 10, 5210),
    (5232, True, 34, 5209),
    (5231, True, 136, 5207),
    (5230, True, 106, 5206),
    (5229, True, 249, 5205),
    (5228, True, 145, 5204),
    (5227, True, 162, 5202),
    (5226, True, 122, 5201),
    (5225, True, 16, 5200),
    (5224, True, 15, 5199),
    (5223, False, 15, 5179),
    (5222, True, 127, 5197),
    (5221, True, 3, 5196),
    (5220, True, 82, 5194),
    (5219, True, 23, 5193),
    (5218, True, 68, 5192),
    (5217, True, 59, 5191),
    (5216, True, 157, 5190),
    (5215, True, 223, 5189),
    (5214, True, 45, 5188),
    (5213, True, 27, 5188),
    (5212, True, 58, 5186),
    (5211, True, 96, 5185),
    (5210, True, 158, 5184),
    (5209, False, 14, 5118),
    (5208, False, 14, 5118),
    (5207, True, 16, 5181),
    ]
    return res


@pytest.fixture
def data_prolog_v5():
    data = [
    (8173, False, 83, 3435),
    (8170, False, 27, 2561),

    (8166, False, 87, 6225),
    (8165, False, 113, 1130),
    (8163, True, 34, 4288),
    (8161, True, 34, 4288),
    (8159, True, 34, 4288),
    (8154, False, 181, 888),
    (8152, False, 189, 859),
    (8150, False, 86, 3708),
    (8147, False, 65, 5357),
    (8146, False, 127, 5880),
    (8145, False, 67, 4106),
    (8144, False, 251, 1196),
    (8143, False, 103, 1119),
    (8142, False, 32, 740),
    (8141, False, 46, 842),
    (8138, False, 74, 1517),
    (8135, False, 46, 3009)
    ]
    return data

@pytest.fixture
def data_prolog_v7():
    res = [
        (350, False, 130, 522),
        (351, False, 348, 527),
        (352, False, 1, 937),
    (353, False, 360, 526),
    (354, False, 94, 519),
    (355, False, 55, 810),
    (356, False, 239, 207),
    (357, False, 155, 307),
    (358, False, 101, 588),
    (359, False, 161, 713),
    (360, False, 254, 581),
    (361, False, 173, 816),
    (362, False, 1, 470),
    (363, False, 170, 588),
    (364, False, 151, 728),
    (365, False, 329, 808),
    (366, False, 137, 905),
    (367, False, 75, 407),
    (368, False, 117, 471),
    (369, False, 416, 808),
    (370, False, 144, 886),
    (371, False, 188, 911),
    (372, False, 117, 1042),
    (373, False, 120, 325),
    (374, False, 209, 722),
    (375, False, 70, 814),
    (376, True, 258, 778),
    (377, True, 154, 779),
    (378, True, 125, 779),
    (379, True, 256, 780),
    (380, True, 197, 781),
    (381, False, 50, 544),
    (382, True, 162, 778),
    (383, True, 56, 779),
    (384, True, 154, 779),
    (385, True, 98, 779),
    (386, True, 258, 780),
    (387, False, 197, 787),
    (388, False, 37, 451),
    (389, True, 163, 778),
    (390, False, 61, 779),
    (391, True, 125, 779),
    (392, False, 65, 462),
    (393, False, 191, 852),
    (394, True, 198, 463),
    (395, True, 101, 1019),
    (396, True, 3, 1021),
    (397, True, 85, 1051),
    (398, True, 12, 470),
    (399, True, 3, 470),
    (400, False, 94, 1051),
    (401, False, 37, 1046),
    (402, False, 2, 888),
    (403, False, 3, 888),
    (404, False, 97, 267),
    (405, False, 9, 1042),
    (406, False, 2, 888),
    (407, False, 3, 888),
    (408, False, 91, 454),
    (409, False, 304, 521),
    (410, False, 203, 326),
    (411, False, 271, 522),
    (412, False, 1, 888),
    (413, False, 3, 888),
    (414, False, 61, 754),
    (415, False, 138, 521),
    (416, False, 228, 522),
    (417, False, 157, 1033),
    (418, False, 202, 614),
    (419, True, 24, 959),
    (420, False, 348, 715),
    (421, False, 238, 715),
    (422, False, 2, 1021),
    (423, False, 3, 1021),
    (424, False, 102, 521),
    (425, False, 56, 1023),
    (426, False, 2, 470),
    (427, False, 3, 470),
    (428, False, 114, 521),
    (429, False, 19, 940),
    ]
    return res

def test_Prolog_v1(data_prolog_v1):
    cl_hlp = CHelper_CleanerTexts()
    info_test = CMergingInfo.makeMergeInfoCollectionFromTestList(data_prolog_v1)
    res = cl_hlp.SplitFromStart(info_test, isTestOld=True)
    assert res == 1
    return

def test_Prolog_v2(prolog_v2):
    cl_hlp = CHelper_CleanerTexts()
    info_test = CMergingInfo.makeMergeInfoCollectionFromTestList(prolog_v2)
    res = cl_hlp.SplitFromStart(info_test, isTestOld=True)
    assert res==0
    return

def test_Prolog_v3(prolog_v3):
    cl_hlp = CHelper_CleanerTexts()
    info_test = CMergingInfo.makeMergeInfoCollectionFromTestList(prolog_v3)
    res = cl_hlp.SplitFromStart(info_test,isTestOld=True)
    assert res==11
    return

def test_Prolog_v4(prolog_v4):
    cl_hlp = CHelper_CleanerTexts()
    info_test = CMergingInfo.makeMergeInfoCollectionFromTestList(prolog_v4)
    res = cl_hlp.SplitFromStart(info_test,isTestOld=True)
    assert res==0
    return

def test_Prolog_v5(data_prolog_v5:typing.List[typing.Tuple[int,bool,int]]):
    cl_hlp = CHelper_CleanerTexts()
    info_test = CMergingInfo.makeMergeInfoCollectionFromTestList( data_prolog_v5 )
    res = cl_hlp.SplitFromStart(info_test,isTestOld=True)
    assert res==-1
    return

def test_Prolog_v6(data_prolog_v6):
    cl_hlp = CHelper_CleanerTexts()
    info_test = CMergingInfo.makeMergeInfoCollectionFromTestList(data_prolog_v6)
    res = cl_hlp.SplitFromStart(info_test, isTestOld=True)
    print(res)
    assert res==10
    return

def test_Prolog_v7(data_prolog_v7):
    cl_hlp = CHelper_CleanerTexts()
    info_test = CMergingInfo.makeMergeInfoCollectionFromTestList(data_prolog_v7)
    res = cl_hlp.SplitFromStart(info_test)
    print(res)
    assert res==-1
    return
