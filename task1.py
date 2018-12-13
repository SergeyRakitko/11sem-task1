import math
import random
import copy
import sys  # sys нужен для передачи argv в QApplication

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import QMainWindow


# import test

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Speed:
    def __init__(self, u, v, w):
        self.u = u
        self.v = v
        self.w = w


class SpeedUp:
    def __init__(self, ax, ay, az):
        self.ax = ax
        self.ay = ay
        self.az = az


class Particle(Position, Speed, Color):
    def __init__(self, position, speed, color, mass, lifetime):
        Position.__init__(self, position.x, position.y, position.z)
        Speed.__init__(self, speed.u, speed.v, speed.w)
        Color.__init__(self, color.r, color.g, color.b)

        self.mass = mass
        self.lifetime = lifetime


timerStep = 10
t = 0
G = 6.67e-11
positions = [[], []]
speeds = [[], []]
speedups = [[], []]
particleList = [Particle(Position(0.3, 0, 0), Speed(-0.1, 0, 0), Color(1, 0, 0), 5.97e+24, 20000),
                Particle(Position(0.2, 0.3, 0), Speed(-0.05, 0, 0), Color(0, 1, 0), 7.3e+22, 20000),
                Particle(Position(0.5, -0.3, 0), Speed(0.5, -0.3, 0), Color(0, 1, 1), 7.3e+23, 20000),
                Particle(Position(-0.2, 0.5, 0), Speed(0.4, 0, 0), Color(1, 1, 0), 7.3e+21, 20000),
                Particle(Position(-0.2, -0.3, 0), Speed(0, 0, 0), Color(0, 0, 1), 4.3e+24, 21000)]
for part in particleList:
    positions[0].append(Position(part.x, part.y, part.z))
    positions[1].append(Position(part.x, part.y, part.z))
    speeds[0].append(Speed(part.u, part.v, part.w))
    speeds[1].append(Speed(part.u, part.v, part.w))
    speedups[0].append(SpeedUp(0, 0, 0))
    speedups[1].append(SpeedUp(0, 0, 0))


class MainWindow(QMainWindow):
    def __init__(self):
        global timerStep
        super(MainWindow, self).__init__()

        uic.loadUi('test1.ui', self)
        self.GLWidget = glWidget(self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.draw)
        self.timer.start(timerStep)

        self.button1.clicked.connect(self.addSphere)
        self.button2.clicked.connect(self.deleteSphere)
        self.closeButton.clicked.connect(self.close)
        self.slider_m.valueChanged.connect(self.sliderValueChange)

        self.initializeInput()

        # фиксация размеров, задание цвета фона
        self.setFixedSize(self.size())
        background_color = QColor()
        background_color.setNamedColor('#aee6cd')
        p = self.palette()
        p.setColor(self.backgroundRole(), background_color)
        self.setPalette(p)

    def initializeInput(self):
        self.slider_m.setValue(random.randint(20, 1000))
        self.input_lifetime.setPlainText(str(random.randint(1000, 10000)))
        self.input_x.setPlainText(str(round(-0.5 + random.random(), 3)))
        self.input_y.setPlainText(str(round(-0.5 + random.random(), 3)))
        self.input_z.setPlainText(str(round(-0.5 + random.random(), 3)))
        self.input_u.setPlainText(str(round(-0.25 + 0.5 * random.random(), 3)))
        self.input_v.setPlainText(str(round(-0.25 + 0.5 * random.random(), 3)))
        self.input_w.setPlainText(str(round(-0.25 + 0.5 * random.random(), 3)))
        self.input_r.setPlainText(str(round(0.5 + 0.5 * random.random(), 3)))
        self.input_g.setPlainText(str(round(0.5 + 0.5 * random.random(), 3)))
        self.input_b.setPlainText(str(round(0.5 + 0.5 * random.random(), 3)))

    def sliderValueChange(self):
        self.input_m.setPlainText(str(self.slider_m.value()) + "e+21")

    def draw(self):
        global t, particleList, speeds, speedups, positions, timerStep
        t += 0.001
        delta = 0.001
        k1 = 0.9e+5

        deleteNums = []
        for i in range(len(particleList)):
            particleList[i].lifetime -= timerStep
            if particleList[i].lifetime == 0:
                deleteNums.append(i)

        deleteNums.sort(reverse=True)
        for i in deleteNums:
            del particleList[i]
            del positions[0][i]
            del positions[1][i]
            del speeds[0][i]
            del speeds[1][i]
            del speedups[0][i]
            del speedups[1][i]

        deleteNums = []

        for part1 in particleList:
            for part2 in particleList:
                if particleList.index(part2) > particleList.index(part1):  # part1 != part2:
                    r1 = (part1.mass / (4 / 3 * math.pi * 1e+27)) ** (1 / 3)
                    r2 = (part2.mass / (4 / 3 * math.pi * 1e+27)) ** (1 / 3)
                    distance = ((part1.x - part2.x) ** 2 +
                                (part1.y - part2.y) ** 2 +
                                (part1.z - part2.z) ** 2) ** 0.5
                    if distance < math.fabs(r2 + r1):
                        alpha = 1.8
                        if r1 > r2:
                            part1.mass += part2.mass
                            part1.r = (alpha * part1.r + (2 - alpha) * part2.r) / 2
                            part1.g = (alpha * part1.g + (2 - alpha) * part2.g) / 2
                            part1.b = (alpha * part1.b + (2 - alpha) * part2.b) / 2
                            deleteNums.append(particleList.index(part2))
                        else:
                            part2.mass += part1.mass
                            part2.r = ((2 - alpha) * part1.r + alpha * part2.r) / 2
                            part2.g = ((2 - alpha) * part1.g + alpha * part2.g) / 2
                            part2.b = ((2 - alpha) * part1.b + alpha * part2.b) / 2
                            deleteNums.append(particleList.index(part1))

        deleteNums.sort(reverse=True)
        for i in deleteNums:
            del particleList[i]
            del positions[0][i]
            del positions[1][i]
            del speeds[0][i]
            del speeds[1][i]
            del speedups[0][i]
            del speedups[1][i]

        for i in range(len(particleList)):
            for j in range(len(particleList)):
                if i != j:
                    # ускорения
                    speedups[0][i] = SpeedUp(speedups[1][i].ax, speedups[1][i].ay, speedups[1][i].az)
                    distance = ((positions[0][j].x - positions[0][i].x) ** 2 +
                                (positions[0][j].y - positions[0][i].y) ** 2 +
                                (positions[0][j].z - positions[0][i].z) ** 2) ** 0.5 * k1
                    # if distance < 100:
                    #    distance = 0.1e+50
                    # distance = 0.1e+5
                    speedups[1][i].ax = G * particleList[j].mass * (
                            positions[0][j].x - positions[0][i].x) * 1 / distance ** 3
                    speedups[1][i].ay = G * particleList[j].mass * (
                            positions[0][j].y - positions[0][i].y) * 1 / distance ** 3
                    speedups[1][i].az = G * particleList[j].mass * (
                            positions[0][j].z - positions[0][i].z) * 1 / distance ** 3

                    # координаты
                    positions[0][i] = Position(positions[1][i].x, positions[1][i].y, positions[1][i].z)
                    positions[1][i].x = positions[0][i].x + speeds[0][i].u * delta + 0.5 * speedups[0][
                        i].ax * delta ** 2
                    positions[1][i].y = positions[0][i].y + speeds[0][i].v * delta + 0.5 * speedups[0][
                        i].ay * delta ** 2
                    positions[1][i].z = positions[0][i].z + speeds[0][i].w * delta + 0.5 * speedups[0][
                        i].az * delta ** 2

                    # скорости
                    speeds[0][i] = Speed(speeds[1][i].u, speeds[1][i].v, speeds[1][i].w)
                    speeds[1][i].u = speeds[0][i].u + 0.5 * (speedups[1][i].ax + speedups[0][i].ax) * delta
                    speeds[1][i].v = speeds[0][i].v + 0.5 * (speedups[1][i].ay + speedups[0][i].ay) * delta
                    speeds[1][i].w = speeds[0][i].w + 0.5 * (speedups[1][i].az + speedups[0][i].az) * delta

                    particleList[i].x = positions[1][i].x
                    particleList[i].y = positions[1][i].y
                    particleList[i].z = positions[1][i].z

        self.output_count.setText(str(len(particleList)))
        self.GLWidget.update()
        # particleList[0].x = 0.5 * math.sin(t)
        # particleList[0].y = 0.5 * math.cos(t)
        # particleList[1].x = 0.5 * math.cos(t) * math.sin(t)
        # particleList[1].y = 0.5 * (math.cos(t) + math.sin(t))

    def addSphere(self):
        global positions, speeds, speedups, particleList
        x = float(self.input_x.toPlainText())
        y = float(self.input_y.toPlainText())
        z = float(self.input_z.toPlainText())
        u = float(self.input_u.toPlainText())
        v = float(self.input_v.toPlainText())
        w = float(self.input_w.toPlainText())
        r = float(self.input_r.toPlainText())
        g = float(self.input_g.toPlainText())
        b = float(self.input_b.toPlainText())
        mass = float(self.slider_m.value())
        lifetime = float(self.input_lifetime.toPlainText())

        particleList.append(Particle(Position(x, y, z), Speed(u, v, w), Color(r, g, b), mass * 1e+22, lifetime))
        positions[0].append(Position(x, y, z))
        positions[1].append(Position(x, y, z))
        speeds[0].append(Speed(u, v, w))
        speeds[1].append(Speed(u, v, w))
        speedups[0].append(SpeedUp(0, 0, 0))
        speedups[1].append(SpeedUp(0, 0, 0))

        self.initializeInput()

        self.GLWidget.update()

    def deleteSphere(self):
        if particleList:
            del particleList[len(particleList) - 1]
        self.GLWidget.update()


class glWidget(QGLWidget):
    vertexShaderSource = """
            varying vec4 vertex_color;
            varying vec3 l;
            varying vec3 n;

            uniform vec4 lightPos;
            uniform vec4 eyePos;
            void main(){

                vec3 p = vec3 ( gl_ModelViewMatrix * gl_Vertex );           // transformed point to world space

                l = normalize ( vec3 ( lightPos ) - p );                    // vector to light source
                n = normalize ( gl_NormalMatrix * gl_Normal );              // transformed n

                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                vertex_color = gl_Color;
            }"""

    fragmentShaderSource = """

            varying vec3 l;
            varying vec3 n;
            varying vec4 vertex_color;
            void main() {

                const vec4 diffColor = vertex_color; //vec4 ( 0.0, 0.5, 0.0, 1.0 );

                vec3 n2   = normalize ( n );
                vec3 l2   = normalize ( l );
                vec4 diff = diffColor * max ( dot ( n2, l2 ), 0.0 );

                gl_FragColor = diff;

                //gl_FragColor = vertex_color;
            }"""

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(900, 900)
        self.move(0, 0)

    def initializeGL(self):
        glClearColor(0.1, 0.2, 0.3, 1.0)
        # self.program = QtGui.QOpenGLShaderProgram(self)
        # self.program.AddShaderFromSourceCode(QtGui.QOpenGLShader.Vertex, self.vertexShaderSource)
        # self.program.AddShaderFromSourceCode(QtGui.QOpenGLShader.Fragment, self.fragmentShaderSource)
        # self.program.link()
        # self.program.bind()

    def resizeGL(self, width, height):
        # this tells openGL how many pixels it should be drawing into
        glViewport(0, 0, width, height)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        for a in particleList:
            qobj = gluNewQuadric()
            gluQuadricDrawStyle(qobj, GLU_FILL)
            glTranslatef(a.x, a.y, a.z)
            glColor3f(a.r, a.g, a.b)
            gluSphere(qobj, (a.mass / (4 / 3 * math.pi * 1e+27)) ** (1 / 3), 50, 50)
            gluDeleteQuadric(qobj)
            glTranslatef(-a.x, -a.y, -a.z)

        # glBegin(GL_LINES)
        # glColor3f(1, 0, 0)
        # glVertex3d(0, 0, 0)
        # glVertex3d(20, 0, 0)
        # glColor3d(0, 1, 0)
        # glVertex3d(0, 0, 0)
        # glVertex3d(0, 20, 0)
        # glColor3f(0, 0, 1)
        # glVertex3d(0, 0, 0)
        # glVertex3d(0, 0, 20)
        # glEnd()


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
