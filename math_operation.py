import math

def centeroidPinHoleMode(height, focal, altitude, theta, yCoordinate):
    height = float(height)  # jumlah baris (baris)
    focal = float(focal)    # panjang focal (baris)
    theta = float(theta)    # sudut kemiringan
    yCoordinate = float(yCoordinate)    # indek piksel y objek
    delta = math.degrees(math.atan(math.fabs(yCoordinate - (height / 2)) / focal))
    if yCoordinate >= height / 2:
        lCentroid = altitude * math.tan(math.radians(theta + delta))
    else:
        lCentroid = altitude * math.tan(math.radians(theta - delta))
    lCentroid = round(lCentroid, 4)
    delta = round(delta, 4)
    return lCentroid

def vertikalPinHoleModel(height, focal, altitude, theta, y1, y2, maxHighLV, maxHighHV, maxLengthLV):
    # y1' : indeks piksel terdepan kendaraan (kordinat y)
    # y2' : indeks piksel terbelakang kendaraan (kordinat y)
    delta1 = math.degrees(math.atan(math.fabs((height / 2) - y1) / focal))
    delta2 = math.degrees(math.atan(math.fabs((height / 2) - y2) / focal))
    if y1 >= height / 2:
        Ly1 = altitude * math.tan(math.radians(theta + delta1))
    else:
        Ly1 = altitude * math.tan(math.radians(theta - delta1))
    if y2 >= height / 2:
        Ly2 = altitude * math.tan(math.radians(theta + delta2))
    else:
        Ly2 = altitude * math.tan(math.radians(theta - delta2))
    Lv = math.fabs(Ly1 - Ly2)
    if y2 >= height / 2:
        Y2G_LV = maxHighLV * math.tan(math.radians(theta + delta2))
        Y2G_HV = maxHighHV * math.tan(math.radians(theta + delta2))
    else:
        Y2G_LV = maxHighLV * math.tan(math.radians(theta - delta2))
        Y2G_HV = maxHighHV * math.tan(math.radians(theta - delta2))
    LengthLV = (Ly2 - (Ly1 + Y2G_LV))
    LengthHV = (Ly2 - (Ly1 + Y2G_HV))
    if LengthLV <= maxLengthLV:
        Lv = LengthLV
    else:
        Lv = LengthLV
    Lv = round(Lv, 3)
    return Lv

def horizontalPinHoleModel(width, focal, altitude, x1, x2, lengthObject):
    # width : jumlah kolom (piksel)
    # focal -> |A'O| : focal length (piksel)
    # altitude -> |O'O| : tinggi kamera (m)
    # theta : sudut kemiringan kamera (derajat)
    # lengthObject : jarak objek dengan kamera (m)
    # x1' : indeks piksel kanan kendaraan (kordinat x)
    # x2' : indeks piksel kiri kendaraan (kordinat x)
    # Lw1 -> |O'X1| : jarak titik kanan kendaraan dengan titik tengah kamera (m)
    # Lw2 -> |O'X2| : jarak titik kiri kendaraan dengan titik tengah kamera (m)
    # X2G -> |X2G| : jarak belakang kendaraan dengan titik blindspot belakang kendaraan (m)
    delta1 = math.degrees(math.atan(math.fabs(x1 - (width / 2)) / focal))
    delta2 = math.degrees(math.atan(math.fabs(x2 - (width / 2)) / focal))
    OX = math.sqrt(math.pow(lengthObject, 2) + math.pow(altitude, 2))
    Lx1 = math.tan(math.radians(delta1)) * OX
    Lx2 = math.tan(math.radians(delta2)) * OX
    if (x1 <= width / 2) and (x2 >= width / 2):
        Lx = round((Lx2 + Lx1), 3)
    else:
        Lx = round(math.fabs(Lx2 - Lx1), 3)
    return Lx

def funcY_line(x1, y1, x2, y2, X):
    # m : line gradient
    # y - y1 = m (x -x1)
    # y = m (x - x1) + y
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)
    X = float(X)
    m = (y1 - y2) / (x1 - x2)
    Y = ((m * X) - (m * x1)) + y1
    Y = int(round(Y))
    return Y

def funcX_line(x1, y1, x2, y2, Y):
    # m : line gradient
    # y - y1 = m (x -x1)
    # x = ((y - y1) + (m * x1)) /m
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)
    Y = float(Y)
    m = (y1 - y2) / (x1 - x2)
    X = ((Y - y1) + (m * x1)) / m
    X = int(round(X))
    return X

def getFocalfromFOV(width, fov):
    focal = (width / 2) / math.tan(math.radians(fov / 2))
    return focal

def transformDiagonalFOV(fov):
    if fov == 90.0:
        horizontalFOV = 78.4
        verticalFOV = 44.1
    elif fov == 127.0:
        horizontalFOV = 113.3
        verticalFOV = 63.7
    elif fov == 160.0:
        horizontalFOV = 139.5
        verticalFOV = 78.4
    else:
        horizontalFOV, verticalFOV = fov
    return horizontalFOV, verticalFOV

def euclideanDistance(x1, y1, x2, y2):
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)
    distance = math.sqrt((math.pow(math.fabs(x1 - x2), 2) + (math.pow(math.fabs(y1 - y2), 2))))
    distance = int(distance)
    return distance

def determineCropFactor(sensorwidth, sensorheight):
    # Comparison between 35mm lens
    # FX : 35mm * 26mm sensor size
    cropfactor = math.sqrt(math.pow(36, 2) + math.pow(24, 2)) / math.sqrt(math.pow(sensorheight, 2) + math.pow(sensorwidth, 2))
    return cropfactor

def getCoordinateFromDistance(height, focal, altitude, theta, distance):
    # height    : jumlah baris (piksel)
    # focal     : panjang focal length kamera (piksel)
    # altitude  : ketinggian kamera
    # theta     : kemiringan kamera
    # distance  : jarak yang ingin diketahui lokasinya
    distance = float(distance)
    altitude = float(altitude)
    focal = float(focal)
    alpha = math.degrees(math.atan(distance / altitude))
    delta = theta - alpha
    yCoordinate = focal * math.tan(math.radians(delta))
    yCoordinate += (height / 2)
    return yCoordinate