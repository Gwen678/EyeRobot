# Copyright 2011 Brown University Robotics.
# Copyright 2017 Open Source Robotics Foundation, Inc.
# All rights reserved.
#
# Software License Agreement (BSD License 2.0)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of the Willow Garage nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys
import threading

import geometry_msgs.msg
import rclpy
from std_msgs.msg import Float32

if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty


msg = """
EyeRobot teleop — keypresses to Twist (wheels) + Float32 (fans/belt).
---------------------------
Driving:
   w/s : forward / backward
   a/d : turn left / turn right
 space : STOP everything (wheels + fans + belt)
 anything else : stop wheels

Latched toggles (tap again to stop):
   q/e : fans forward / reverse
   r/t : belt forward / reverse

Speed:
   u/j : increase/decrease max speeds by 10%
   i/k : increase/decrease only linear speed by 10%
   o/l : increase/decrease only angular speed by 10%

CTRL-C to quit
"""

moveBindings = {
    'w': (1, 0, 0, 0),    # forward
    's': (-1, 0, 0, 0),   # backward
    'a': (0, 0, 0, 1),    # turn left (CCW, +yaw)
    'd': (0, 0, 0, -1),   # turn right (CW, -yaw)
}

speedBindings = {
    'u': (1.1, 1.1),
    'j': (.9, .9),
    'i': (1.1, 1),
    'k': (.9, 1),
    'o': (1, 1.1),
    'l': (1, .9),
}

# Fans/belt latched toggles — tap to activate, tap same key again to stop.
# +value = forward, -value = reverse; cmd_vel_bridge applies motor coupling.
fanBindings = {
    'q': 1.0,   # fans forward
    'e': -1.0,  # fans reverse
}

beltBindings = {
    'r': 1.0,   # belt forward
    't': -1.0,  # belt reverse
}


def getKey(settings):
    if sys.platform == 'win32':
        key = msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def vels(speed, turn):
    return 'currently:\tspeed %s\tturn %s ' % (speed, turn)


def main():
    settings = saveTerminalSettings()

    rclpy.init()

    node = rclpy.create_node('teleop_twist_keyboard')

    # parameters
    stamped = node.declare_parameter('stamped', False).value
    frame_id = node.declare_parameter('frame_id', '').value
    fan_speed = node.declare_parameter('fan_command_rad_s', 8.0).value
    belt_speed = node.declare_parameter('belt_command_rad_s', 8.0).value
    # diff_drive_controller's ~/cmd_vel_unstamped subscription is remapped to
    # /cmd_vel in manual_controller.launch.py, so teleop and Nav2 share one
    # topic and drive the controller directly (no topic_tools relay).
    cmd_vel_topic = node.declare_parameter('cmd_vel_topic', '/cmd_vel').value
    if not stamped and frame_id:
        raise Exception("'frame_id' can only be set when 'stamped' is True")

    if stamped:
        TwistMsg = geometry_msgs.msg.TwistStamped
    else:
        TwistMsg = geometry_msgs.msg.Twist

    pub      = node.create_publisher(TwistMsg, cmd_vel_topic, 10)
    pub_fans = node.create_publisher(Float32, '/cmd_fans', 10)
    pub_belt = node.create_publisher(Float32, '/cmd_belt', 10)

    spinner = threading.Thread(target=rclpy.spin, args=(node,))
    spinner.start()

    speed = 0.5
    turn = 1.0
    x = 0.0
    y = 0.0
    z = 0.0
    th = 0.0
    status = 0.0

    # Fans/belt latched state, republished at 5 Hz by a node timer (spinner
    # thread): the firmware zeroes any motor command not refreshed within
    # 500 ms (comms-loss safety net), so a single publish per keypress only
    # produces a half-second pulse instead of a latched motor.
    latched = {'fans': 0.0, 'belt': 0.0}

    def _republish_latched():
        pub_fans.publish(Float32(data=latched['fans']))
        pub_belt.publish(Float32(data=latched['belt']))

    node.create_timer(0.2, _republish_latched)

    twist_msg = TwistMsg()

    if stamped:
        twist = twist_msg.twist
        twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist_msg.header.frame_id = frame_id
    else:
        twist = twist_msg

    try:
        print(msg)
        print(vels(speed, turn))
        while True:
            key = getKey(settings)
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                y = moveBindings[key][1]
                z = moveBindings[key][2]
                th = moveBindings[key][3]
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]

                print(vels(speed, turn))
                if (status == 14):
                    print(msg)
                status = (status + 1) % 15
                # Same stale-twist hazard as the fan keys: adjust the scale
                # without re-sending the last motion command.
                continue
            elif key in fanBindings.keys():
                # Latched toggle: same key again = off, other key = flip
                # direction. The timer above keeps republishing the value.
                # Do NOT fall through to the twist publish below — that would
                # re-send the LAST move command (stale x/th) and the robot
                # would lurch/spin every time a fan key is tapped.
                target = fanBindings[key] * fan_speed
                latched['fans'] = 0.0 if latched['fans'] == target else target
                print('fans: %s' % ('+' if latched['fans'] > 0 else ('-' if latched['fans'] < 0 else 'off')))
                pub_fans.publish(Float32(data=latched['fans']))
                continue
            elif key in beltBindings.keys():
                target = beltBindings[key] * belt_speed
                latched['belt'] = 0.0 if latched['belt'] == target else target
                print('belt: %s' % ('+' if latched['belt'] > 0 else ('-' if latched['belt'] < 0 else 'off')))
                pub_belt.publish(Float32(data=latched['belt']))
                continue
            else:
                x = 0.0
                y = 0.0
                z = 0.0
                th = 0.0
                if key == ' ':
                    # Emergency stop: wheels (zero twist below) + fans + belt.
                    latched['fans'] = 0.0
                    latched['belt'] = 0.0
                    pub_fans.publish(Float32(data=0.0))
                    pub_belt.publish(Float32(data=0.0))
                    print('STOP — wheels, fans and belt off')
                if (key == '\x03'):
                    break

            if stamped:
                twist_msg.header.stamp = node.get_clock().now().to_msg()

            twist.linear.x = x * speed
            twist.linear.y = y * speed
            twist.linear.z = z * speed
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = th * turn
            pub.publish(twist_msg)

    except Exception as e:
        print(e)

    finally:
        if stamped:
            twist_msg.header.stamp = node.get_clock().now().to_msg()

        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = 0.0
        pub.publish(twist_msg)
        pub_fans.publish(Float32(data=0.0))
        pub_belt.publish(Float32(data=0.0))
        rclpy.shutdown()
        spinner.join()

        restoreTerminalSettings(settings)


if __name__ == '__main__':
    main()
