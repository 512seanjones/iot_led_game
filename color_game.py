import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import RPi.GPIO as GPIO
from time import sleep

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

# red is 18
# yellow is 17
# blue is 22
# green is 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)

@ask.intent("YesIntent")
def next_round():
    leds = {0:'red', 1:'yellow', 2:'green', 3:'blue', 'red':18, 'yellow':17, 'blue':22, 'green':27}
    numbers = [randint(0, 3) for _ in range(3)]
    colors = []
    for i in numbers:
        colors.append(leds[i])
    for i in colors:
        GPIO.output(leds[i], True)
        sleep(1)
        GPIO.output(leds[i], False)
        sleep(0.5)
    round_msg = render_template('round')
    session.attributes['colors'] = colors[::-1]  # reverse
    return question(round_msg)

@ask.intent("NoIntent")
def end_game():
    GPIO.cleanup()
    msg = render_template('goodbye')
    return statement(msg)

@ask.intent("AnswerIntent", convert={'first': str, 'second': str, 'third': str})
def answer(first, second, third):
    winning_colors = session.attributes['colors']
    if [first, second, third] == winning_colors:
        msg = render_template('win')
    else:
        msg = render_template('lose')
    return question(msg)

@ask.intent("AMAZON.StopIntent")
def stop():
    GPIO.cleanup()
    msg = render_template('goodbye')
    return statement(msg)

@ask.intent("AMAZON.CancelIntent")
def cancel():
    GPIO.cleanup()
    msg = render_template('goodbye')
    return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)
