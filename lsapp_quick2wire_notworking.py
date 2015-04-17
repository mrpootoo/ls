# install_twisted_rector must be called before importing  and using the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()


from twisted.internet import reactor
from twisted.internet import protocol
import MySQLdb
import MySQLdb.cursors
import ConfigParser
import time

config = ConfigParser.RawConfigParser()
config.read('ls.cfg')
dbhost = config.get('db','host')
dbuser = config.get('db','user')
dbpass = config.get('db','pass')
dbdatabase = config.get('db','database')

#GPIO.setmode(GPIO.BCM)
#wiringpi2.wiringPiSetupGpio()
from quick2wire.gpio import pins, In, Out
# Pin Definitons:
#r1Pin = 14 # Broadcom pin 14 (P1 pin 8)
#r2Pin = 15 # Broadcom pin 15 (P1 pin 10)
r1Pin = pins.pin(3, direction=Out)
r2Pin = pins.pin(4, direction=Out)
with r1Pin:
    r1Pin.value = 0
    print('r1Pin set to out, value 0')
    time.sleep(2)
    Print('exiting')
with r2Pin:
    r2Pin.value = 0
    print('r1Pin set to out, value 0')
    time.sleep(2)
    Print('exiting')
#GPIO.setup(r1Pin,GPIO.OUT)
#GPIO.setup(r2Pin,GPIO.OUT)
#wiringpi2.pinMode(r1Pin,1) # Set pin 6 to 1 ( OUTPUT )
#wiringpi2.pinMode(r2Pin,1) # Set pin 6 to 1 ( OUTPUT )
#GPIO.output(r1Pin, GPIO.HIGH)
#GPIO.output(r2Pin, GPIO.HIGH)
#wiringpi2.digitalWrite(r1Pin,1) #set HIGH
#wiringpi2.digitalWrite(r2Pin,1) #set HIGH
r1Pin.value = 1
r2Pin.value = 1

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

    def __init__(self, **kwargs):
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

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'q':
            keyboard.release()

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

        reactor.listenTCP(5000, EchoFactory(self))
        MyKeyboardListener()

    def handle_message(self, msg, addr):
	msg = msg.strip()
        intlmsg = ''

        if msg[0] == "2":
	    #GPIO.output(r1Pin, GPIO.LOW)
            #wiringpi2.digitalWrite(r1Pin,0)
            r1Pin.value = 0
            time.sleep(.2)
            r1Pin.value = 1
            #GPIO.output(r1Pin, GPIO.HIGH)
            #wiringpi2.digitalWrite(r1Pin,1)
	    intlmsg = "******INTERNATIONAL******"
        if msg == "r1off":
	    #GPIO.output(r1Pin, GPIO.HIGH)
            #wiringpi2.digitalWrite(r1Pin,1)
            r1Pin.value = 1
        if msg == "r2on":
	    #GPIO.output(r2Pin, GPIO.LOW)
            #wiringpi2.digitalWrite(r2Pin,0)
            r2Pin.value = 0
        if msg == "r2off":
	    #GPIO.output(r2Pin, GPIO.HIGH)
            #wiringpi2.digitalWrite(r2Pin,1)
            r1Pin.value = 1
	
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
