# install_twisted_rector must be called before importing  and using the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()


from twisted.internet import reactor
from twisted.internet import protocol
import MySQLdb
import MySQLdb.cursors
import ConfigParser
import RPi.GPIO as GPIO
import time

config = ConfigParser.RawConfigParser()
config.read('ls.cfg')
dbhost = config.get('db','host')
dbuser = config.get('db','user')
dbpass = config.get('db','pass')
dbdatabase = config.get('db','database')

GPIO.setmode(GPIO.BCM)
# Pin Definitons:
r1Pin = 14 # Broadcom pin 14 (P1 pin 8)
r2Pin = 15 # Broadcom pin 15 (P1 pin 10)
GPIO.setup(r1Pin,GPIO.OUT)
GPIO.setup(r2Pin,GPIO.OUT)
GPIO.output(r1Pin, GPIO.HIGH)
GPIO.output(r2Pin, GPIO.HIGH)

class EchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data, self.transport.getPeer().host)
        #if response:
        #    self.transport.write(response)


class EchoFactory(protocol.Factory):
    protocol = EchoProtocol

    def __init__(self, app):
        self.app = app


from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.widget import Widget


class MyKeyboardListener(Widget):

    def __init__(self, app, **kwargs):
	self.app = app
        super(MyKeyboardListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        print(' - modifiers are %r' % modifiers)
        self.app.mainlabel.text = text
        if keycode[1] == 'r':
            self.app.maintext.text = 'reprint'
        if keycode[1] == 'u':
            self.app.maintext.text = 'user'

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        #if keycode[1] == 'q':
        #    keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

class MainScreen(GridLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.cols = 2
        self.mainlabel = Label(text="Server Started\n")
        self.add_widget(self.mainlabel)
        self.maintext = TextInput(multiline=False)
        self.add_widget(self.maintext)
        self.scanmode = ''
        self.maintext.text = self.scanmode

        reactor.listenTCP(5000, EchoFactory(self))
        MyKeyboardListener(self)

    def handle_message(self, msg, addr):
	msg = msg.strip()
        intlmsg = ''

        if msg[0] == "2":
	    GPIO.output(r1Pin, GPIO.LOW)
            time.sleep(.2)
            GPIO.output(r1Pin, GPIO.HIGH)
	    intlmsg = "******INTERNATIONAL******"
        if msg == "r1off":
	    GPIO.output(r1Pin, GPIO.HIGH)
        if msg == "r2on":
	    GPIO.output(r2Pin, GPIO.LOW)
        if msg == "r2off":
	    GPIO.output(r2Pin, GPIO.HIGH)
	
	#if len(msg) > 0:
            #db = MySQLdb.connect(host=dbhost,user=dbuser,passwd=dbpass,db=dbdatabase, cursorclass=MySQLdb.cursors.DictCursor)
            #cur = db.cursor()

            #if len(msg) < 16:
                #cur.execute("insert into barcode set barcode=%s, inserter=%s",(msg,addr))
            #else:
                #cur.execute("insert into barcode set barcode=%s, inserter=%s, special=%s, special2=%s, jobid=%s, seq=%s, runcmd=%s",(msg,addr,msg[0],msg[1],msg[2:10],msg[10:15],msg[15]))
            #db.commit()
            #db.close()

        if len(intlmsg) > 0:
            msg += intlmsg

	screenmsg = self.mainlabel.text + "received: %s (%s)\n" % (msg,addr)
        if len(screenmsg) > 300:
            screenmsg = screenmsg[-300:]
        self.mainlabel.text = screenmsg

        return msg

class TwistedServerApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    TwistedServerApp().run()
