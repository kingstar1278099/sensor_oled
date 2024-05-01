import rclpy
from std_msgs.msg import Int32
from bfc_msgs.msg import Button, Coordination, HeadMovement
from std_msgs.msg import Int32MultiArray
from sensor_msgs.msg import Imu
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import time

disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_bus=8, gpio=1)
disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, width, height), outline=0, fill=0)

padding = -2
top = padding
x = 0
font = ImageFont.load_default()

r, p, y = "", "", ""
condition, last_condition = 0, 0
strategy, last_strategy = 0, 0
voltage, state, pan, tilt, ball_x, ball_y = "", "", "", "", "", ""

def imu_callback(msg):
    global r, p, y
    r, p, y = str(int(msg.angular_velocity.x)), str(int(msg.angular_velocity.y)), str(int(msg.angular_velocity.z))

def button_callback(msg):
    global condition, strategy
    condition = msg.kill
    strategy = msg.strategy
    update_display()

def voltage_callback(msg):
    global voltage
    voltage = str(msg.data)

def state_callback(msg):
    global state
    state = str(msg.state)

def head_callback(msg):
    global pan, tilt
    pan, tilt = str(round(msg.pan, 2)), str(round(msg.tilt, 2))

def ball_callback(msg):
    global ball_x, ball_y
    ball_x, ball_y = str(msg.data[0]), str(msg.data[1])

def update_display():
    global condition, last_condition, strategy, last_strategy
    if condition != last_condition or strategy != last_strategy:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x+25, top), "BARELANG FC", font=font, fill=255)
        if condition == 0:
            draw.text((x+31.5, top+8), "RUN", font=font, fill=255)
        elif condition == 1:
            draw.text((x+31.5, top+8), "KILL", font=font, fill=255)
        draw_strategy()
        last_condition = condition
        last_strategy = strategy
        disp.image(image)
        disp.display()

def draw_strategy():
    global strategy
    strategies = ["Strategy = 0", "Strategy = 1", "Strategy = 2", "Strategy = 3", "Strategy = 4"]
    if strategy in range(len(strategies)):
        draw.text((x+40, top+14), strategies[strategy], font=font, fill=255)

def main(args=None):
    global condition, strategy
    rclpy.init(args=args)
    node = rclpy.create_node('oled')

    sub_imu = node.create_subscription(Imu, 'imu', imu_callback, 10)
    sub_button = node.create_subscription(Button, 'button', button_callback, 10)
    sub_volt = node.create_subscription(Int32, 'voltage', voltage_callback, 10)
    sub_state = node.create_subscription(Coordination, 'coordination', state_callback, 10)
    sub_head = node.create_subscription(HeadMovement, 'head', head_callback, 10)
    sub_ball = node.create_subscription(Int32MultiArray, 'vision', ball_callback, 10)

    try:
        while rclpy.ok():
            update_display()
            rclpy.spin_once(node)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Exiting Program")

    except Exception as e:
        print("Error occurred. Exiting Program")
        print("Error:", str(e))

    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

