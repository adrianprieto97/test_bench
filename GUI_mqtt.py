import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Signal, Slot, Qt, QObject, Property
from PySide6.QtGui import QOpenGLFunctions, QSurfaceFormat
from gui2 import Ui_MainWindow
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import paho.mqtt.client as mqtt
import json

class MqttClient(QObject):
    Disconnected = 0
    Connecting = 1
    Connected = 2
    MQTT_3_1 = mqtt.MQTTv31
    MQTT_3_1_1 = mqtt.MQTTv311
    MQTT_5 = mqtt.MQTTv5

    connected = Signal()
    disconnected = Signal()
    stateChanged = Signal(int)
    hostnameChanged = Signal(int)
    portChanged = Signal(int)
    keepAliveChanged = Signal(int)
    cleanSessionChanged = Signal(int)
    protocolVersionChanged = Signal(int)
    messageSignal = Signal(object)

    def __init__(self, parent=None):
        super(MqttClient, self).__init__(parent)

        self.m_hostname = ''
        self.m_port = 1883
        self.m_keepAlive = 60
        self.m_cleanSession = True
        self.m_protocolVersion = MqttClient.MQTT_3_1

        self.m_state = MqttClient.Disconnected

        self.m_client = mqtt.Client(clean_session=self.m_cleanSession, protocol=self.m_protocolVersion)
        
        self.m_client.on_connect = self.on_connect
        self.m_client.on_message = self.on_message
        self.m_client.on_disconnect = self.on_disconnect

    @Property(int, notify=stateChanged)
    def state(self):
        return self.m_state
    
    @state.setter
    def state(self, state):
        if self.m_state == state : return
        self.m_state = state
        self.stateChanged.emit(state)

    @Property(str, notify=hostnameChanged)
    def hostname(self):
        return self.m_hostname
    
    @hostname.setter
    def hostname(self, hostname):
        if self.m_hostname == hostname: return
        self.m_hostname = hostname
        self.hostnameChanged.emit(hostname)

    @Property(int, notify=portChanged)
    def port(self):
        return self.m_port
    
    @port.setter
    def port(self, port):
        if self.m_port == port: return
        self.m_port = port
        self.portChanged.emit(port)

    @Property(int, notify=keepAliveChanged)
    def keepAlive(self):
        return self.m_keepAlive
    
    @keepAlive.setter
    def keepAlive(self, keepAlive):
        if self.m_keepAlive == keepAlive: return
        self.m_keepAlive = keepAlive
        self.keepAliveChanged.emit(keepAlive)

    @Property(bool, notify=cleanSessionChanged)
    def cleanSession(self):
        return self.m_cleanSession
    
    @cleanSession.setter
    def cleanSession(self, cleanSession):
        if self.m_cleanSession == cleanSession: return
        self.m_cleanSession = cleanSession
        self.cleanSessionChanged.emit(cleanSession)

    @Property(int, notify=protocolVersionChanged)
    def protocolVersion(self):
        return self.m_protocolVersion
    
    @protocolVersion.setter
    def protocolVersion(self, protocolVersion):
        if self.m_protocolVersion == protocolVersion: return
        if protocolVersion in (MqttClient.MQTT_3_1, MqttClient.MQTT_3_1_1, MqttClient.MQTT_5):
            self.m_protocolVersion = protocolVersion
            self.protocolVersionChanged.emit(protocolVersion)

    @Slot()
    def connectToHost(self):
        if self.m_hostname:
            self.m_client.connect(self.m_hostname, port=self.port, keepalive=self.keepAlive)
            self.state = MqttClient.Connecting
            self.m_client.loop_start()

    @Slot()
    def disconnectFromHost(self):
        self.m_client.disconnect()

    def subscribe(self, path):
        if self.state == MqttClient.Connected:
            self.m_client.subscribe(path)

    def publish(self, topic,payload=None,qos=0):
       if self.state == MqttClient.Connected:
           self.m_client.publish(topic,payload,qos)

    def on_message(self, mqttc, obj, msg):
        mstr=msg.payload.decode('utf-8')
        self.messageSignal.emit(msg)

    def on_connect(self, *args):
        self.state = MqttClient.Connected
        self.connected.emit()

    def on_disconnect(self, *args):
        self.state = MqttClient.Disconnected
        self.disconnected.emit()
                    
class MainWindow(QMainWindow):
    phiSignal = Signal(float)
    thetaSignal = Signal(float)
    motor1signal = Signal(float)
    motor2signal = Signal(float)
    motor3signal = Signal(float)
    motor4signal = Signal(float)
    def __init__(self, transparent):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        if transparent:
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.glwidget = OpenGLWidget(transparent)

        self.client = MqttClient(self)
        self.client.stateChanged.connect(self.on_stateChanged)
        self.client.messageSignal.connect(self.on_messageSignal)
        self.client.hostname='192.168.0.13'
        self.client.connectToHost()

        # initialize buttons and sliders
        self.ui.tar_button.clicked.connect(self.tare)
        self.ui.weight_button.clicked.connect(self.weigh)
        self.ui.start_button.clicked.connect(self.startIMU)
        self.ui.stop_button.clicked.connect(self.stop)
        self.ui.pushButton.clicked.connect(self.saveToFile)
        self.ui.autolevel_button.clicked.connect(self.autoLevel)
        self.ui.angle_button.clicked.connect(self.angle)
        self.ui.GL_layout.addWidget(self.glwidget)
        self.ui.weight_val_label.setText(str(0.0))
        self.ui.roll_val_label.setText(str(0.0))
        self.ui.pitch_val_label.setText(str(0.0))
        self.ui.m1_val_label.setText(str(0.00))
        self.ui.m2_val_label.setText(str(0.00))
        self.ui.m3_val_label.setText(str(0.00))
        self.ui.m4_val_label.setText(str(0.00))
        self.ui.force_val_label.setText(str(0.00))
        self.ui.label_2ratio_val.setText(str(0.00))
        self.ui.time_val_label.setText('00:00:00.00')
        self.ui.phi_slider.valueChanged.connect(self.updateSliders)
        self.ui.theta_slider.valueChanged.connect(self.updateSliders)
        self.phiSignal.connect(self.glwidget.phiRotation)
        self.thetaSignal.connect(self.glwidget.thetaRotation)
        self.motor1signal.connect(self.glwidget.motor1)
        self.motor2signal.connect(self.glwidget.motor2)
        self.motor3signal.connect(self.glwidget.motor3)
        self.motor4signal.connect(self.glwidget.motor4)
        self.angleflag=False

    def phiSignalemit(self,phi):
        self.phiSignal.emit(phi)

    def thetaSignalemit(self, theta):
        self.thetaSignal.emit(theta)

    def motor1signalemit(self,motor1):
        self.motor1signal.emit(motor1)

    def motor2signalemit(self,motor2):
        self.motor2signal.emit(motor2)

    def motor3signalemit(self,motor3):
        self.motor3signal.emit(motor3)

    def motor4signalemit(self,motor4):
        self.motor4signal.emit(motor4)

    @Slot(int)
    def on_stateChanged(self, state):
        if state == MqttClient.Connected:
            print(state)
            self.client.subscribe('weight')
            self.client.subscribe('loadcell')
            self.client.subscribe('IMU')
            self.client.subscribe('time')
            self.client.subscribe('ratio')

    @Slot(str)
    def on_messageSignal(self, msg):
        if msg.topic == 'weight':
            try:
                mstr=msg.payload.decode('utf-8')
                self.ui.weight_val_label.setText(str(mstr))
            except ValueError:
                print('error: Not a number')
        if msg.topic == 'loadcell':
            try:
                val=msg.payload.decode('utf-8')
                val=json.loads(val)
                self.ui.force_val_label.setText(str(val[4]))
                self.ui.m1_val_label.setText(str(val[0]))
                self.ui.m2_val_label.setText(str(val[1]))
                self.ui.m3_val_label.setText(str(val[2]))
                self.ui.m4_val_label.setText(str(val[3]))
                self.motor1signalemit(val[0])
                self.motor2signalemit(val[1])
                self.motor3signalemit(val[2])
                self.motor4signalemit(val[3])
                #self.ui.label_2ratio_val.setText(str(round((val[4]/float(str(self.ui.weight_val_label.text()))),2)))
            except ValueError:
                print('error: Not a number')
        if msg.topic == 'IMU':
            try:
                val=msg.payload.decode('utf-8')
                val=json.loads(val)
                self.ui.pitch_val_label.setText(str(round(val[0],4)))
                self.ui.roll_val_label.setText(str(round(val[1],4)))
                self.phiSignalemit(val[0])
                self.thetaSignalemit(val[1])
            except ValueError:
                print('error: Not a number')
        if msg.topic == 'time':
                val=msg.payload.decode('utf-8')
                self.ui.time_val_label.setText(val)

    def tare(self):
        self.client.publish('tare')

    def weigh(self):
        self.client.publish('weigh')
    def startIMU(self):
        self.client.publish('start')
        self.ui.pushButton.setEnabled(False)
        self.autoLevel()

    def stop(self):
        self.client.publish('stop')
        self.ui.pushButton.setEnabled(True)

    def updateSliders(self):
        msg=(self.ui.phi_slider.value()/10,self.ui.theta_slider.value()/10)
        msg=json.dumps(msg)
        self.client.publish(topic='updateSliders',payload=msg)

    def autoLevel(self):
        self.client.publish('autolevel')
        self.ui.angle_button.setEnabled(True)
        self.ui.autolevel_button.setEnabled(False)
        self.ui.phi_slider.setEnabled(False)
        self.ui.theta_slider.setEnabled(False)
        self.angleflag=False
                    
    def angle(self):
        self.client.publish('angle')
        self.ui.autolevel_button.setEnabled(True)
        self.ui.angle_button.setEnabled(False)
        self.ui.phi_slider.setEnabled(True)
        self.ui.theta_slider.setEnabled(True)
        self.ui.phi_slider.setValue(0.0)
        self.ui.theta_slider.setValue(0.0)
        self.angleflag=True

    def saveToFile(self):
        self.client.publish('savetofile')

class OpenGLWidget(QOpenGLWidget, QOpenGLFunctions):
    def __init__(self, transparent, parent=None):
        QOpenGLWidget.__init__(self, parent)
        QOpenGLFunctions.__init__(self)
        self._transparent = transparent
        self._core = QSurfaceFormat.defaultFormat().profile() == QSurfaceFormat.CoreProfile
        self.phi_rotation=0
        self.theta_rotation=0
        self.motor1_val=0
        self.motor2_val=0
        self.motor3_val=0
        self.motor4_val=0

    def phiRotation(self):
        return self.phi_rotation
    def thetaRotation(self):
        return self.theta_rotation
    def motor1(self):
        return self.motor1_val
    def motor2(self):
        return self.motor2_val
    def motor3(self):
        return self.motor3_val
    def motor4(self):
        return self.motor4_val
    
    @Slot(int)
    def phiRotation(self, angle):
        if angle != self.phi_rotation:
            self.phi_rotation=angle
            self.update()

    @Slot(int)
    def thetaRotation(self, angle):
        if angle != self.theta_rotation:
            self.theta_rotation=angle
            self.update()

    @Slot(int)
    def motor1(self, val):
        if val != self.motor1_val:
            self.motor1_val=val/196.2 #check normalization operation according to loadcell range and units (max value must be 0.5)
            self.update()

    @Slot(int)
    def motor2(self, val):
        if val != self.motor2_val:
            self.motor2_val=val/196.2
            self.update()
    
    @Slot(int)
    def motor3(self, val):
        if val != self.motor3_val:
            self.motor3_val=val/196.2
            self.update()

    @Slot(int)
    def motor4(self, val):
        if val != self.motor4_val:
            self.motor4_val=val/196.2
            self.update()

    def initializeGL(self):
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0,0.0,0.0,0.0 if self._transparent else 1)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0,0.0,-2)
        # rotate with IMU values
        glRotate(90-self.phi_rotation,-1,0,0) # x axis
        glRotate(self.theta_rotation,0,-1,0) # y axis

        # GL graphic definition
        # MAIN PLATE
        plate_top=((0.5,-1.0,0.0),(1.0,-0.5,0.0),(1.0,0.5,0.0),(0.5,1.0,0.0),(-0.5,1.0,0.0),(-1.0,0.5,0.0),(-1.0,-0.5,0.0),(-0.5,-1.0,0.0))
        plate_bottom=((0.5,-1.0,-0.05),(1.0,-0.5,-0.05),(1.0,0.5,-0.05),(0.5,1.0,-0.05),(-0.5,1.0,-0.05),(-1.0,0.5,-0.05),(-1.0,-0.5,-0.05),(-0.5,-1.0,-0.05))
        #MOTOR TOWERS
        tower1_bottom=((0.65,-0.65,0.0),(0.65,-0.55,0.0),(0.55,-0.55,0.0),(0.55,-0.65,0.0))
        tower1_top=((0.65,-0.65,0.1),(0.65,-0.55,0.1),(0.55,-0.55,0.1),(0.55,-0.65,0.1))
        tower2_bottom=((0.65,0.65,0.0),(0.65,0.55,0.0),(0.55,0.55,0.0),(0.55,0.65,0.0))
        tower2_top=((0.65,0.65,0.1),(0.65,0.55,0.1),(0.55,0.55,0.1),(0.55,0.65,0.1))
        tower3_bottom=((-0.65,0.65,0.0),(-0.65,0.55,0.0),(-0.55,0.55,0.0),(-0.55,0.65,0.0))
        tower3_top=((-0.65,0.65,0.1),(-0.65,0.55,0.1),(-0.55,0.55,0.1),(-0.55,0.65,0.1))
        tower4_bottom=((-0.65,-0.65,0.0),(-0.65,-0.55,0.0),(-0.55,-0.55,0.0),(-0.55,-0.65,0.0))
        tower4_top=((-0.65,-0.65,0.1),(-0.65,-0.55,0.1),(-0.55,-0.55,0.1),(-0.55,-0.65,0.1))
        # MOTORS
        motor1_bottom=((0.6,-0.8,0.1),(0.74142,-0.74142,0.1),(0.8,-0.6,0.1),(0.74142,-0.45858,0.1),(0.6,-0.4,0.1),(0.45858,-0.45858,0.1),(0.4,-0.6,0.1),(0.45858,-0.74142,0.1))
        motor1_top=((0.6,-0.8,0.15),(0.74142,-0.74142,0.15),(0.8,-0.6,0.15),(0.74142,-0.45858,0.15),(0.6,-0.4,0.15),(0.45858,-0.45858,0.15),(0.4,-0.6,0.15),(0.45858,-0.74142,0.15))
        motor2_bottom=((0.6,0.8,0.1),(0.74142,0.74142,0.1),(0.8,0.6,0.1),(0.74142,0.45858,0.1),(0.6,0.4,0.1),(0.45858,0.45858,0.1),(0.4,0.6,0.1),(0.45858,0.74142,0.1))
        motor2_top=((0.6,0.8,0.15),(0.74142,0.74142,0.15),(0.8,0.6,0.15),(0.74142,0.45858,0.15),(0.6,0.4,0.15),(0.45858,0.45858,0.15),(0.4,0.6,0.15),(0.45858,0.74142,0.15))
        motor3_bottom=((-0.6,0.8,0.1),(-0.74142,0.74142,0.1),(-0.8,0.6,0.1),(-0.74142,0.45858,0.1),(-0.6,0.4,0.1),(-0.45858,0.45858,0.1),(-0.4,0.6,0.1),(-0.45858,0.74142,0.1))
        motor3_top=((-0.6,0.8,0.15),(-0.74142,0.74142,0.15),(-0.8,0.6,0.15),(-0.74142,0.45858,0.15),(-0.6,0.4,0.15),(-0.45858,0.45858,0.15),(-0.4,0.6,0.15),(-0.45858,0.74142,0.15))
        motor4_bottom=((-0.6,-0.8,0.1),(-0.74142,-0.74142,0.1),(-0.8,-0.6,0.1),(-0.74142,-0.45858,0.1),(-0.6,-0.4,0.1),(-0.45858,-0.45858,0.1),(-0.4,-0.6,0.1),(-0.45858,-0.74142,0.1))
        motor4_top=((-0.6,-0.8,0.15),(-0.74142,-0.74142,0.15),(-0.8,-0.6,0.15),(-0.74142,-0.45858,0.15),(-0.6,-0.4,0.15),(-0.45858,-0.45858,0.15),(-0.4,-0.6,0.15),(-0.45858,-0.74142,0.15))
        # LOADCELL VALUES
        loadcell1_bottom=((0.7,-0.7,0.15),(0.7,-0.5,0.15),(0.5,-0.5,0.15),(0.5,-0.7,0.15))
        loadcell1_top=((0.7,-0.7,self.motor1_val+0.15),(0.7,-0.5,self.motor1_val+0.15),(0.5,-0.5,self.motor1_val+0.15),(0.5,-0.7,self.motor1_val+0.15))
        loadcell2_bottom=((0.7,0.7,0.15),(0.7,0.5,0.15),(0.5,0.5,0.15),(0.5,0.7,0.15))
        loadcell2_top=((0.7,0.7,self.motor2_val+0.15),(0.7,0.5,self.motor2_val+0.15),(0.5,0.5,self.motor2_val+0.15),(0.5,0.7,self.motor2_val+0.15))
        loadcell3_bottom=((-0.7,0.7,0.15),(-0.7,0.5,0.15),(-0.5,0.5,0.15),(-0.5,0.7,0.15))
        loadcell3_top=((-0.7,0.7,self.motor3_val+0.15),(-0.7,0.5,self.motor3_val+0.15),(-0.5,0.5,self.motor3_val+0.15),(-0.5,0.7,self.motor3_val+0.15))
        loadcell4_bottom=((-0.7,-0.7,0.15),(-0.7,-0.5,0.15),(-0.5,-0.5,0.15),(-0.5,-0.7,0.15))
        loadcell4_top=((-0.7,-0.7,self.motor4_val+0.15),(-0.7,-0.5,self.motor4_val+0.15),(-0.5,-0.5,self.motor4_val+0.15),(-0.5,-0.7,self.motor4_val+0.15))

        # PLATE TOP FACE
        glBegin(GL_POLYGON)
        glColor(0.0,1.0,0.0)
        for vertex in plate_top:
            glVertex3fv(vertex)
        glEnd()
        # PLATE BOTTOM FACE
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in plate_bottom:
            glVertex3fv(vertex)
        glEnd()
        # PLATE SIDE FACES
        glBegin(GL_POLYGON)
        glColor(0.5,0.5,0.5)
        glVertex3fv(plate_top[0])
        glVertex3fv(plate_top[1])
        glVertex3fv(plate_bottom[1])
        glVertex3fv(plate_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.5,0.5,0.5)
        glVertex3fv(plate_top[1])
        glVertex3fv(plate_top[2])
        glVertex3fv(plate_bottom[2])
        glVertex3fv(plate_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.5,0.5,0.5)
        glVertex3fv(plate_top[2])
        glVertex3fv(plate_top[3])
        glVertex3fv(plate_bottom[3])
        glVertex3fv(plate_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.5,0.5,0.5)
        glVertex3fv(plate_top[3])
        glVertex3fv(plate_top[4])
        glVertex3fv(plate_bottom[4])
        glVertex3fv(plate_bottom[3])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.5,0.5,0.5)
        glVertex3fv(plate_top[4])
        glVertex3fv(plate_top[5])
        glVertex3fv(plate_bottom[5])
        glVertex3fv(plate_bottom[4])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.5,0.5,0.5)
        glVertex3fv(plate_top[5])
        glVertex3fv(plate_top[6])
        glVertex3fv(plate_bottom[6])
        glVertex3fv(plate_bottom[5])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.5,0.5,0.5)
        glVertex3fv(plate_top[6])
        glVertex3fv(plate_top[7])
        glVertex3fv(plate_bottom[7])
        glVertex3fv(plate_bottom[6])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.5,0.5,0.5)
        glVertex3fv(plate_top[7])
        glVertex3fv(plate_top[0])
        glVertex3fv(plate_bottom[0])
        glVertex3fv(plate_bottom[7])
        glEnd()

        # TOWER 1
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower1_bottom[0])
        glVertex3fv(tower1_bottom[1])
        glVertex3fv(tower1_top[1])
        glVertex3fv(tower1_top[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower1_bottom[1])
        glVertex3fv(tower1_bottom[2])
        glVertex3fv(tower1_top[2])
        glVertex3fv(tower1_top[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower1_bottom[2])
        glVertex3fv(tower1_bottom[3])
        glVertex3fv(tower1_top[3])
        glVertex3fv(tower1_top[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower1_bottom[3])
        glVertex3fv(tower1_bottom[0])
        glVertex3fv(tower1_top[0])
        glVertex3fv(tower1_top[3])
        glEnd()

        # TOWER 2
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower2_bottom[0])
        glVertex3fv(tower2_bottom[1])
        glVertex3fv(tower2_top[1])
        glVertex3fv(tower2_top[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower2_bottom[1])
        glVertex3fv(tower2_bottom[2])
        glVertex3fv(tower2_top[2])
        glVertex3fv(tower2_top[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower2_bottom[2])
        glVertex3fv(tower2_bottom[3])
        glVertex3fv(tower2_top[3])
        glVertex3fv(tower2_top[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower2_bottom[3])
        glVertex3fv(tower2_bottom[0])
        glVertex3fv(tower2_top[0])
        glVertex3fv(tower2_top[3])
        glEnd()

        # TOWER 3
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower3_bottom[0])
        glVertex3fv(tower3_bottom[1])
        glVertex3fv(tower3_top[1])
        glVertex3fv(tower3_top[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower3_bottom[1])
        glVertex3fv(tower3_bottom[2])
        glVertex3fv(tower3_top[2])
        glVertex3fv(tower3_top[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower3_bottom[2])
        glVertex3fv(tower3_bottom[3])
        glVertex3fv(tower3_top[3])
        glVertex3fv(tower3_top[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower3_bottom[3])
        glVertex3fv(tower3_bottom[0])
        glVertex3fv(tower3_top[0])
        glVertex3fv(tower3_top[3])
        glEnd()

        # TOWER 4
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower4_bottom[0])
        glVertex3fv(tower4_bottom[1])
        glVertex3fv(tower4_top[1])
        glVertex3fv(tower4_top[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower4_bottom[1])
        glVertex3fv(tower4_bottom[2])
        glVertex3fv(tower4_top[2])
        glVertex3fv(tower4_top[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower4_bottom[2])
        glVertex3fv(tower4_bottom[3])
        glVertex3fv(tower4_top[3])
        glVertex3fv(tower4_top[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,1.0,0.0)
        glVertex3fv(tower4_bottom[3])
        glVertex3fv(tower4_bottom[0])
        glVertex3fv(tower4_top[0])
        glVertex3fv(tower4_top[3])
        glEnd()

        # MOTOR 1
        # Motor 1 top face
        glBegin(GL_POLYGON)
        glColor(0.0,1.0,0.0)
        for vertex in motor1_top:
            glVertex3fv(vertex)
        glEnd()
        # Motor 1 bottom face
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in motor1_bottom:
            glVertex3fv(vertex)
        glEnd()
        # Motor 1 side faces
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor1_top[0])
        glVertex3fv(motor1_top[1])
        glVertex3fv(motor1_bottom[1])
        glVertex3fv(motor1_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor1_top[1])
        glVertex3fv(motor1_top[2])
        glVertex3fv(motor1_bottom[2])
        glVertex3fv(motor1_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor1_top[2])
        glVertex3fv(motor1_top[3])
        glVertex3fv(motor1_bottom[3])
        glVertex3fv(motor1_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor1_top[3])
        glVertex3fv(motor1_top[4])
        glVertex3fv(motor1_bottom[4])
        glVertex3fv(motor1_bottom[3])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor1_top[4])
        glVertex3fv(motor1_top[5])
        glVertex3fv(motor1_bottom[5])
        glVertex3fv(motor1_bottom[4])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor1_top[5])
        glVertex3fv(motor1_top[6])
        glVertex3fv(motor1_bottom[6])
        glVertex3fv(motor1_bottom[5])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor1_top[6])
        glVertex3fv(motor1_top[7])
        glVertex3fv(motor1_bottom[7])
        glVertex3fv(motor1_bottom[6])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor1_top[7])
        glVertex3fv(motor1_top[0])
        glVertex3fv(motor1_bottom[0])
        glVertex3fv(motor1_bottom[7])
        glEnd()

        # MOTOR 2
        # Motor 2 top face
        glBegin(GL_POLYGON)
        glColor(0.0,1.0,0.0)
        for vertex in motor2_top:
            glVertex3fv(vertex)
        glEnd()
        # Motor 2 bottom face
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in motor2_bottom:
            glVertex3fv(vertex)
        glEnd()
        # Motor 2 side faces
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor2_top[0])
        glVertex3fv(motor2_top[1])
        glVertex3fv(motor2_bottom[1])
        glVertex3fv(motor2_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor2_top[1])
        glVertex3fv(motor2_top[2])
        glVertex3fv(motor2_bottom[2])
        glVertex3fv(motor2_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor2_top[2])
        glVertex3fv(motor2_top[3])
        glVertex3fv(motor2_bottom[3])
        glVertex3fv(motor2_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor2_top[3])
        glVertex3fv(motor2_top[4])
        glVertex3fv(motor2_bottom[4])
        glVertex3fv(motor2_bottom[3])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor2_top[4])
        glVertex3fv(motor2_top[5])
        glVertex3fv(motor2_bottom[5])
        glVertex3fv(motor2_bottom[4])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor2_top[5])
        glVertex3fv(motor2_top[6])
        glVertex3fv(motor2_bottom[6])
        glVertex3fv(motor2_bottom[5])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor2_top[6])
        glVertex3fv(motor2_top[7])
        glVertex3fv(motor2_bottom[7])
        glVertex3fv(motor2_bottom[6])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor2_top[7])
        glVertex3fv(motor2_top[0])
        glVertex3fv(motor2_bottom[0])
        glVertex3fv(motor2_bottom[7])
        glEnd()

        # MOTOR 3
        # Motor 3 top face
        glBegin(GL_POLYGON)
        glColor(0.0,1.0,0.0)
        for vertex in motor3_top:
            glVertex3fv(vertex)
        glEnd()
        # Motor 3 bottom face
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in motor3_bottom:
            glVertex3fv(vertex)
        glEnd()
        # Motor 3 side faces
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor3_top[0])
        glVertex3fv(motor3_top[1])
        glVertex3fv(motor3_bottom[1])
        glVertex3fv(motor3_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor3_top[1])
        glVertex3fv(motor3_top[2])
        glVertex3fv(motor3_bottom[2])
        glVertex3fv(motor3_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor3_top[2])
        glVertex3fv(motor3_top[3])
        glVertex3fv(motor3_bottom[3])
        glVertex3fv(motor3_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor3_top[3])
        glVertex3fv(motor3_top[4])
        glVertex3fv(motor3_bottom[4])
        glVertex3fv(motor3_bottom[3])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor3_top[4])
        glVertex3fv(motor3_top[5])
        glVertex3fv(motor3_bottom[5])
        glVertex3fv(motor3_bottom[4])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor3_top[5])
        glVertex3fv(motor3_top[6])
        glVertex3fv(motor3_bottom[6])
        glVertex3fv(motor3_bottom[5])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor3_top[6])
        glVertex3fv(motor3_top[7])
        glVertex3fv(motor3_bottom[7])
        glVertex3fv(motor3_bottom[6])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor3_top[7])
        glVertex3fv(motor3_top[0])
        glVertex3fv(motor3_bottom[0])
        glVertex3fv(motor3_bottom[7])
        glEnd()

        # MOTOR 4
        # Motor 4 top face
        glBegin(GL_POLYGON)
        glColor(0.0,1.0,0.0)
        for vertex in motor4_top:
            glVertex3fv(vertex)
        glEnd()
        # Motor 4 bottom face
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in motor4_bottom:
            glVertex3fv(vertex)
        glEnd()
        # Motor 4 side faces
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor4_top[0])
        glVertex3fv(motor4_top[1])
        glVertex3fv(motor4_bottom[1])
        glVertex3fv(motor4_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor4_top[1])
        glVertex3fv(motor4_top[2])
        glVertex3fv(motor4_bottom[2])
        glVertex3fv(motor4_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor4_top[2])
        glVertex3fv(motor4_top[3])
        glVertex3fv(motor4_bottom[3])
        glVertex3fv(motor4_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor4_top[3])
        glVertex3fv(motor4_top[4])
        glVertex3fv(motor4_bottom[4])
        glVertex3fv(motor4_bottom[3])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor4_top[4])
        glVertex3fv(motor4_top[5])
        glVertex3fv(motor4_bottom[5])
        glVertex3fv(motor4_bottom[4])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor4_top[5])
        glVertex3fv(motor4_top[6])
        glVertex3fv(motor4_bottom[6])
        glVertex3fv(motor4_bottom[5])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor4_top[6])
        glVertex3fv(motor4_top[7])
        glVertex3fv(motor4_bottom[7])
        glVertex3fv(motor4_bottom[6])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(0.7,0.7,0.7)
        glVertex3fv(motor4_top[7])
        glVertex3fv(motor4_top[0])
        glVertex3fv(motor4_bottom[0])
        glVertex3fv(motor4_bottom[7])
        glEnd()

        # LOADCELL TOWERS
        # Loadcell 1 top face
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in loadcell1_top:
            glVertex3fv(vertex)
        glEnd()
        # Loadcell 1 side faces
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell1_top[0])
        glVertex3fv(loadcell1_top[1])
        glVertex3fv(loadcell1_bottom[1])
        glVertex3fv(loadcell1_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell1_top[1])
        glVertex3fv(loadcell1_top[2])
        glVertex3fv(loadcell1_bottom[2])
        glVertex3fv(loadcell1_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell1_top[2])
        glVertex3fv(loadcell1_top[3])
        glVertex3fv(loadcell1_bottom[3])
        glVertex3fv(loadcell1_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell1_top[3])
        glVertex3fv(loadcell1_top[0])
        glVertex3fv(loadcell1_bottom[0])
        glVertex3fv(loadcell1_bottom[3])
        glEnd()
        # Loadcell 2 top face
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in loadcell2_top:
            glVertex3fv(vertex)
        glEnd()
        # Loadcell 2 side faces
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell2_top[0])
        glVertex3fv(loadcell2_bottom[1])
        glVertex3fv(loadcell2_bottom[1])
        glVertex3fv(loadcell2_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell2_top[1])
        glVertex3fv(loadcell2_top[2])
        glVertex3fv(loadcell2_bottom[2])
        glVertex3fv(loadcell2_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell2_top[2])
        glVertex3fv(loadcell2_top[3])
        glVertex3fv(loadcell2_bottom[3])
        glVertex3fv(loadcell2_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell2_top[3])
        glVertex3fv(loadcell2_top[0])
        glVertex3fv(loadcell2_bottom[0])
        glVertex3fv(loadcell2_bottom[3])
        glEnd()
        # Loadcell 3 top face
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in loadcell3_top:
            glVertex3fv(vertex)
        glEnd()
        # Loadcell 3 side faces
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell3_top[0])
        glVertex3fv(loadcell3_top[1])
        glVertex3fv(loadcell3_bottom[1])
        glVertex3fv(loadcell3_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell3_top[1])
        glVertex3fv(loadcell3_top[2])
        glVertex3fv(loadcell3_bottom[2])
        glVertex3fv(loadcell3_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell3_top[2])
        glVertex3fv(loadcell3_top[3])
        glVertex3fv(loadcell3_bottom[3])
        glVertex3fv(loadcell3_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell3_top[3])
        glVertex3fv(loadcell3_top[0])
        glVertex3fv(loadcell3_bottom[0])
        glVertex3fv(loadcell3_bottom[3])
        glEnd()
        # Loadcell 4 top face
        glBegin(GL_POLYGON)
        glColor(0.0,0.0,1.0)
        for vertex in loadcell4_top:
            glVertex3fv(vertex)
        glEnd()
        # Loadcell 4 side faces
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell4_top[0])
        glVertex3fv(loadcell4_top[1])
        glVertex3fv(loadcell4_bottom[1])
        glVertex3fv(loadcell4_bottom[0])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell4_top[1])
        glVertex3fv(loadcell4_top[2])
        glVertex3fv(loadcell4_bottom[2])
        glVertex3fv(loadcell4_bottom[1])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell4_top[2])
        glVertex3fv(loadcell4_top[3])
        glVertex3fv(loadcell4_bottom[3])
        glVertex3fv(loadcell4_bottom[2])
        glEnd()
        glBegin(GL_POLYGON)
        glColor(1.0,0.1,0.1)
        glVertex3fv(loadcell4_top[3])
        glVertex3fv(loadcell4_top[0])
        glVertex3fv(loadcell4_bottom[0])
        glVertex3fv(loadcell4_bottom[3])
        glEnd()        

    def resizeGL(self,w,h):
        glViewport(0,0,w,h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45,1.0*960/540, 0.1,100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = ArgumentParser(description="hellogl2", formatter_class=RawTextHelpFormatter)
    parser.add_argument('--multisample', '-m', action='store_true',help='Use Multisampling')
    parser.add_argument('--coreprofile', '-c', action='store_true',help='Use Core Profile')
    parser.add_argument('--transparent', '-t', action='store_true',help='Transparent Windows')
    options = parser.parse_args()

    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    if options.multisample:
        fmt.setSamples(4)
    if options.coreprofile:
        fmt.setVersion(3, 2)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)
    window = MainWindow(options.transparent)
    window.show()
    sys.exit(app.exec())