import sys
import os, os.path
import glob
import json
import pprint
import PIL.Image, PIL.ImageDraw


from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QImageReader
from PyQt5.QtCore import Qt, QSize, QRect

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QLabel,
    
)

DEBUG = False


class Window(QWidget):

    def __init__(self, width, height):
        super().__init__()
        self.screen_width = width
        self.screen_height = height

        self.pointer = 0
        self.images = []

        self.initUI()

        chosen_points = []

        self.imagePixmap = None

        start_point = None
        finish_point = None

        self.rects = {}


        def mousePressEvent(event):
            nonlocal start_point
            try:
                if event.button() == Qt.LeftButton:
                    start_point = event.pos()
            except Exception as err:
                print(err)

        def mouseReleaseEvent(event):
            nonlocal start_point, finish_point
            if start_point is None or finish_point is None:
                return
            try:
                start_width = self.start_width
                start_height = self.start_height
                finish_width = self.imageLabel.frameGeometry().width()
                finish_height = self.imageLabel.frameGeometry().height()

                
                scale_width_koef = finish_width / start_width
                scale_height_koef = finish_height / start_height
                print('finish = ', self.finish_width, self.finish_width)
                print('img label = ', self.imageLabel.frameGeometry().width(), self.imageLabel.frameGeometry().height())
                x0 = start_point.x()
                y0 = start_point.y()  
                xf = finish_point.x()
                yf = finish_point.y()
                w = abs(xf - x0)
                h = abs(yf - y0)
                #print(x0, y0, w, h)
                filename = os.path.split(self.images[self.pointer])[-1]
                #print(start_point, filename)
                if self.rects.get(filename) is None:
                    self.rects[filename] = []
                if w > 0 and h > 0:
                    self.rects[filename].append({
                        "_x": float(min(x0, xf)),
                        "_y": float(min(y0, yf)),
                        "_width": float(w),
                        "_height": float(h),
                        "x": float(min(x0, xf)) / scale_width_koef,
                        "y": float(min(y0, yf)) / scale_height_koef,
                        "width": float(w) / scale_width_koef,
                        "height": float(h) / scale_height_koef,
                        #"class": "rect"
                    })
                print(self.rects[filename])
                start_point = None
                finish_point = None
            except Exception as err:
                print(err)
            

        def mouseMoveEvent(event):
            nonlocal finish_point
            finish_point = event.pos()
            self.imageLabel.update()

        def paintEvent(event=None):
            try:
                if self.imagePixmap is None or not self.images:
                    return
                painter = QPainter(self.imageLabel)
                rect = QRect(0, 0, self.imageLabel.width(), self.imageLabel.height())
                pixmap = QPixmap(self.images[0])
                painter.drawPixmap(rect, self.imagePixmap)

                pen = QPen()
                pen.setWidth(4)
                pen.setColor(QColor('yellow'))
                painter.setPen(pen)
                painter.setRenderHint(QPainter.Antialiasing, True)
                
                painter.drawPoint(300, 300)
                filename = os.path.split(self.images[self.pointer])[-1]

                if start_point and finish_point:
                    x0 = start_point.x()
                    y0 = start_point.y()

                    w = finish_point.x() - x0
                    h = finish_point.y() - y0

                    

                    painter.drawRect(x0, y0, w, h)

                if self.rects.get(filename):
                    for rect in self.rects[filename]:
                        x0 = rect['_x']
                        y0 = rect['_y']
                        w = rect['_width']
                        h = rect['_height']
                        painter.drawRect(x0, y0, w, h)
                    #self.imageLabel.setPixmap(self.imagePixmap)
            except Exception as err:
                print('ERROR = ', err)

        self._paintEvent = paintEvent

        self.imageLabel.mousePressEvent = mousePressEvent
        self.imageLabel.paintEvent = paintEvent
        self.imageLabel.mouseMoveEvent = mouseMoveEvent
        self.imageLabel.mouseReleaseEvent = mouseReleaseEvent

    def initUI(self):
        screen_width = self.screen_width
        screen_height = self.screen_height
        koef = 0.7
        self.width = screen_width * koef
        self.height = screen_height * koef
        x0 = (1 - koef)/2 * screen_width
        y0 = (1 - koef)/2 * screen_height

        self.setGeometry(x0, y0, self.width, self.height)
        self.setWindowTitle('Разметка изображений')
        #self.setWindowIcon(QIcon('web.png'))
        mainLayout = QVBoxLayout()
        #mainLayout.addStretch(1)

        imageLabel = QLabel()
        self.imageLabel = imageLabel
        imageLabel.setObjectName("imageLabel")
        imageLabel.setStyleSheet("QLabel#imageLabel {background-color: #99d;}")
        imageLabel.setScaledContents(True)
            
        folderPathEdit = QLineEdit()
        folderPathEdit.setText(r'C:\ml\computer_vision\aml-hw28\train\OTHER')
        
        folderPathEdit.setPlaceholderText('Путь к папке с рисунками')
        self.folderPathEdit = folderPathEdit

        loadButton = QPushButton('Загрузить')
        loadButton.clicked.connect(self.loadImages)

        clearButton = QPushButton('Очистить')
        clearButton.clicked.connect(self.clearImageRect)

        pointerLabel = QLabel('Картинка - 0')
        pointerLabel.setMaximumHeight(40)
        self.pointerLabel = pointerLabel

        fileLabel = QLabel('Файл не выбран')
        self.fileLabel = fileLabel
        fileLabel.setMaximumHeight(40)
        fileLabel.setMinimumWidth(180)

        saveButton = QPushButton('Сохранить')
        saveButton.clicked.connect(self.saveData)
        
        loadLayout = QHBoxLayout()
        
        loadLayout.addWidget(folderPathEdit)
        loadLayout.addWidget(loadButton)
        loadLayout.addWidget(clearButton)
        #loadLayout.addWidget(fileLabel)
        #loadLayout.addWidget(pointerLabel)
        loadLayout.addWidget(saveButton)
        
        nextImageButton = QPushButton("Следующая картинка")
        nextImageButton.clicked.connect(self.handleNextImageButton)
        
        prevImageButton = QPushButton("Предыдущая картинка")
        prevImageButton.clicked.connect(self.handlePrevImageButton)
        
        navLayout = QHBoxLayout()
        navLayout.addWidget(prevImageButton)
        navLayout.addWidget(nextImageButton)

        headerLayout = QHBoxLayout()
        headerLayout.addWidget(fileLabel)
        headerLayout.addStretch(0.5)
        headerLayout.addWidget(pointerLabel)
        headerLayout.addStretch(1)

        mainLayout.addLayout(headerLayout)
        mainLayout.addWidget(imageLabel)
        mainLayout.addLayout(loadLayout)
        mainLayout.addLayout(navLayout)
        

        self.setLayout(mainLayout)

        self.show()

    def _handleImageButton(self):
        filename = os.path.split(self.images[self.pointer])[-1]
        self.pointerLabel.setText('Картинка - ' + str(self.pointer))
        self.fileLabel.setText(str(filename))
        pathname = self.images[self.pointer % len(self.images)]
        pixmap = QPixmap(pathname)
        self.start_width = pixmap.width()
        self.start_height = pixmap.height()
        self.finish_width = self.width * 0.8
        self.finish_height = self.height * 0.75
        #self.scale_width_koef = finish_width / start_width
        #self.scale_height_koef = finish_height / start_height
        #print('self.scale_width_koef = ', self.scale_width_koef)
        #print('self.scale_height_koef = ', self.scale_height_koef)
        print('===1', self.start_width, self.start_height)
        pixmap = pixmap.scaled(self.finish_width, self.finish_height, Qt.KeepAspectRatio, Qt.FastTransformation)
        print('===2', self.finish_width, self.finish_height)
        self.imagePixmap = pixmap
        self.update()
        

    def handlePrevImageButton(self):
        try:
            if not self.images:
                return
            if self.pointer == 0:
                return
            self.pointer -= 1
            self._handleImageButton()
        except Exception as err:
            print('Error in handlePrevImageButton', err)
            
        
    def handleNextImageButton(self):
        try:
            if not self.images:
                return
            if self.pointer >= len(self.images) - 1:
                return
            self.pointer += 1
            self._handleImageButton()
        except Exception as err:
            print('Error in handleNextImageButton', err)
        
    def loadImages(self):
        path = self.folderPathEdit.text().strip()
        self.path_prefix = path
        print(path)
        if not os.path.isdir(path):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Не правильный путь к папке")
            msg.setWindowTitle("Ошибка доступа к картинкам")
            returnValue = msg.exec()
            return
        try:
            images = glob.glob(os.path.join(path, '*.jpg'))
            self.images = images
            if images:
                self.pointer = -1
                self.handleNextImageButton()
            self.update()
        except Exception as err:
            self.images.clear()
            print(err)

    def clearImageRect(self):
        try:
            if not self.images:
                return
            filename = os.path.split(self.images[self.pointer])[-1]
            if self.rects.get(filename):
                self.rects[filename].clear()
            self.update()
        except Exception as err:
            print('Error in clearImageRect:', err)

    def saveData(self):
        try:
            data = []
            for filename, elems in self.rects.items():
                annotations = []
                if DEBUG:
                    source_img = PIL.Image.open(os.path.join(self.path_prefix, filename)).convert("RGB")
                    draw = PIL.ImageDraw.Draw(source_img, "RGB")
                for elem in elems:
                    annotations.append({
                        "x": elem['x'],
                        "y": elem['y'],
                        "width": elem['width'],
                        "height": elem['height'],
                        "class": "rect"
                    })
                    if DEBUG:
                        draw.rectangle(((elem['x'], elem['y']), (elem['x'] + elem['width'], elem['y'] + elem['height'])), outline="yellow")
                
                item = {
                    "class": "image",
                    "filename": filename,
                    "annotations": annotations
                }
                data.append(item)
                
                if DEBUG:
                    source_img.show()
            
            with open('result.json', 'w') as outfile:
                json.dump(data, outfile)
        except Exception as err:
            print('Error in saveData:', err)
            
            
    
if __name__ == '__main__':

    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    width, height = size.width(), size.height()
    print(width, height)
    window = Window(width, height)
    sys.exit(app.exec_())
