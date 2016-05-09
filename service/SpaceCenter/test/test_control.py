import unittest
import krpctest
import krpc
import time
from krpctest.geometry import normalize

class TestControlMixin(object):

    def test_special_action_groups(self):
        for name in ['rcs', 'gear', 'lights', 'brakes', 'abort']:
            setattr(self.control, name, True)
            self.assertTrue(getattr(self.control, name))
            setattr(self.control, name, False)
            self.assertFalse(getattr(self.control, name))

    def test_numeric_action_groups(self):
        for i in [0,1,2,3,4,5,6,7,8,9]:
            self.control.set_action_group(i, False)
            self.assertFalse(self.control.get_action_group(i))
            self.control.set_action_group(i, True)
            self.assertTrue(self.control.get_action_group(i))
            self.control.toggle_action_group(i)
            self.assertFalse(self.control.get_action_group(i))
        self.assertRaises(krpc.client.RPCError, self.control.set_action_group, 11, False)
        self.assertRaises(krpc.client.RPCError, self.control.get_action_group, 11)
        self.assertRaises(krpc.client.RPCError, self.control.toggle_action_group, 11)

    def test_pitch_control(self):
        self.conn.testing_tools.clear_rotation(self.vessel)

        self.auto_pilot.sas = False
        self.control.pitch = 1
        time.sleep(1)
        self.control.pitch = 0

        # Check flight is pitching in correct direction
        pitch = self.orbital_flight.pitch
        time.sleep(0.1)
        diff = pitch - self.orbital_flight.pitch
        self.assertGreater(diff, 0)

    def test_yaw_control(self):
        self.conn.testing_tools.clear_rotation(self.vessel)

        self.auto_pilot.sas = False
        self.control.yaw = 1
        time.sleep(1)
        self.control.yaw = 0

        # Check flight is yawing in correct direction
        heading = self.orbital_flight.heading
        time.sleep(0.1)
        diff = heading - self.orbital_flight.heading
        self.assertGreater(diff, 0)

    def test_roll_control(self):
        self.conn.testing_tools.clear_rotation(self.vessel)

        pitch = self.orbital_flight.pitch
        heading = self.orbital_flight.heading

        self.auto_pilot.sas = False
        self.control.roll = 0.1
        time.sleep(1)
        self.control.roll = 0

        self.assertClose(pitch, self.orbital_flight.pitch, error=1)
        self.assertCloseDegrees(heading, self.orbital_flight.heading, error=1)

        # Check flight is rolling in correct direction
        roll = self.orbital_flight.roll
        time.sleep(0.1)
        diff = self.orbital_flight.roll - roll
        self.assertGreater(diff, 0)

    def test_sas_mode(self):
        SASMode = self.conn.space_center.SASMode
        self.control.sas = True
        self.control.sas_mode = SASMode.stability_assist
        active = self.vessel == self.conn.space_center.active_vessel
        if active:
            self.vessel.control.add_node(self.conn.space_center.ut + 60, 100, 0, 0)
        self.assertEqual(self.control.sas_mode, SASMode.stability_assist)
        time.sleep(0.25)
        if active:
            self.control.sas_mode = SASMode.maneuver
            self.assertEqual(self.control.sas_mode, SASMode.maneuver)
            time.sleep(0.25)
        self.control.sas_mode = SASMode.prograde
        self.assertEqual(self.control.sas_mode, SASMode.prograde)
        time.sleep(0.25)
        self.control.sas_mode = SASMode.retrograde
        self.assertEqual(self.control.sas_mode, SASMode.retrograde)
        time.sleep(0.25)
        self.control.sas_mode = SASMode.normal
        self.assertEqual(self.control.sas_mode, SASMode.normal)
        time.sleep(0.25)
        self.control.sas_mode = SASMode.anti_normal
        self.assertEqual(self.control.sas_mode, SASMode.anti_normal)
        time.sleep(0.25)
        self.control.sas_mode = SASMode.radial
        self.assertEqual(self.control.sas_mode, SASMode.radial)
        time.sleep(0.25)
        self.control.sas_mode = SASMode.anti_radial
        self.assertEqual(self.control.sas_mode, SASMode.anti_radial)
        time.sleep(0.25)
        # No target set, should not change
        # TODO: test with a target set
        #self.control.sas_mode = SASMode.target
        #self.assertEqual(self.control.sas_mode, SASMode.anti_radial)
        #time.sleep(0.25)
        #self.control.sas_mode = SASMode.anti_target
        #self.assertEqual(self.control.sas_mode, SASMode.anti_radial)
        #time.sleep(0.25)
        self.control.sas_mode = SASMode.stability_assist
        self.control.sas = False

    def test_speed_mode(self):
        SpeedMode = self.conn.space_center.SpeedMode
        self.control.speed_mode = SpeedMode.orbit
        self.assertEqual(self.control.speed_mode, SpeedMode.orbit)
        time.sleep(0.25)
        self.control.speed_mode = SpeedMode.surface
        self.assertEqual(self.control.speed_mode, SpeedMode.surface)
        time.sleep(0.25)
        # No target set, should not change
        # TODO: test with a target set
        #self.control.speed_mode = SpeedMode.target
        #self.assertEqual(self.control.speed_mode, SpeedMode.surface)
        #time.sleep(0.25)
        #self.control.speed_mode = SpeedMode.orbit
        #self.assertEqual(self.control.speed_mode, SpeedMode.orbit)

class TestControlActiveVessel(krpctest.TestCase, TestControlMixin):

    @classmethod
    def setUpClass(cls):
        krpctest.new_save()
        krpctest.launch_vessel_from_vab('Basic')
        krpctest.remove_other_vessels()
        krpctest.set_circular_orbit('Kerbin', 100000)
        cls.conn = krpctest.connect(name='TestControl')
        cls.vessel = cls.conn.space_center.active_vessel
        cls.control = cls.vessel.control
        cls.auto_pilot = cls.vessel.auto_pilot
        cls.orbital_flight = cls.vessel.flight(cls.vessel.orbital_reference_frame)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_equality(self):
        self.assertEqual(self.conn.space_center.active_vessel.control, self.control)

    def test_maneuver_node_editing(self):
        node = self.control.add_node(self.conn.space_center.ut + 60, 100, 0, 0)
        self.assertEqual(100, node.prograde)
        self.control.remove_nodes()

    def test_clear_on_disconnect(self):
        conn = krpctest.connect(name='TestControlActiveVessel.test_clear_on_disconnect')
        control = conn.space_center.active_vessel.control
        control.pitch = 1
        control.yaw = 1
        control.roll = 1
        time.sleep(0.5)
        conn.close()
        time.sleep(0.5)
        self.assertEqual(self.control.pitch, 0)
        self.assertEqual(self.control.yaw, 0)
        self.assertEqual(self.control.roll, 0)

class TestControlNonActiveVessel(krpctest.TestCase, TestControlMixin):

    @classmethod
    def setUpClass(cls):
        krpctest.new_save()
        krpctest.launch_vessel_from_vab('Multi')
        krpctest.remove_other_vessels()
        krpctest.set_circular_orbit('Kerbin', 100000)
        cls.conn = krpctest.connect(name='TestControlOtherVessel')
        next(iter(cls.conn.space_center.active_vessel.parts.docking_ports)).undock()
        cls.vessel = next(iter(filter(lambda v: v != cls.conn.space_center.active_vessel, cls.conn.space_center.vessels)))
        cls.control = cls.vessel.control
        cls.auto_pilot = cls.vessel.auto_pilot
        cls.orbital_flight = cls.vessel.flight(cls.vessel.orbital_reference_frame)

        # Move the vessels apart
        cls.control.rcs = True
        cls.control.forward = -1
        time.sleep(1)
        cls.control.rcs = False
        cls.control.forward = 0
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_equality(self):
        self.assertNotEqual(self.conn.space_center.active_vessel.control, self.control)

    def test_maneuver_node_editing(self):
        self.assertRaises(krpc.client.RPCError, self.control.add_node, self.conn.space_center.ut + 60, 100, 0, 0)

class TestControlStaging(krpctest.TestCase):

    def setUp(self):
        krpctest.launch_vessel_from_vab('Staging')
        krpctest.remove_other_vessels()
        krpctest.set_circular_orbit('Kerbin', 100000)
        self.conn = krpctest.connect(name='TestStaging')

    def tearDown(self):
        self.conn.close()

    def test_staging(self):
        self.control = self.conn.space_center.active_vessel.control
        for i in reversed(range(12)):
            self.assertEqual(i, self.control.current_stage)
            time.sleep(3)
            self.control.activate_next_stage()
        self.assertEqual(0, self.control.current_stage)

class TestControlRover(krpctest.TestCase):

    @classmethod
    def setUpClass(cls):
        krpctest.new_save()
        krpctest.launch_vessel_from_vab('Rover')
        krpctest.remove_other_vessels()
        cls.conn = krpctest.connect(name='TestControlRover')
        cls.vessel = cls.conn.space_center.active_vessel
        cls.control = cls.vessel.control
        cls.flight = cls.vessel.flight(cls.vessel.orbit.body.reference_frame)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_move_forward(self):
        self.control = self.conn.space_center.active_vessel.control

        # Check the rover is stationary
        self.assertClose(0, self.flight.horizontal_speed, error=0.01)

        # Forward throttle for 1 second
        self.control.wheel_steer = 0
        self.control.wheel_throttle = 0.5
        self.control.brakes = False
        time.sleep(1)

        # Check the rover is moving north
        self.assertGreater(self.flight.horizontal_speed, 0)
        direction = normalize(self.flight.velocity)
        # In the body's reference frame, y-axis points from CoM to north pole
        # As we are close to the equator, this is very close to the north direction
        self.assertClose((0,1,0), direction, 0.2)

        # Apply brakes
        self.control.wheel_throttle = 0
        self.control.brakes = True

        # Wait until the rover has stopped
        while self.flight.horizontal_speed > 0.01:
            time.sleep(0.1)

    def test_move_backward(self):
        self.control = self.conn.space_center.active_vessel.control

        # Check the rover is stationary
        self.assertClose(0, self.flight.horizontal_speed, error=0.01)

        # Reverse throttle for 1 second
        self.control.wheel_steer = 0
        self.control.wheel_throttle = -0.5
        self.control.brakes = False
        time.sleep(1)

        # Check the rover is moving south
        self.assertGreater(self.flight.horizontal_speed, 0)
        direction = normalize(self.flight.velocity)
        # In the body's reference frame, y-axis points from CoM to north pole
        # As we are close to the equator, this is very close to the north direction
        self.assertClose((0,-1,0), direction, 0.2)

        # Apply brakes
        self.control.wheel_throttle = 0
        self.control.brakes = True

        # Wait until the rover has stopped
        while self.flight.horizontal_speed > 0.01:
            time.sleep(0.1)

    def test_steer_left(self):
        self.control = self.conn.space_center.active_vessel.control

        # Check the rover is stationary
        self.assertClose(0, self.flight.horizontal_speed, error=0.01)

        # Forward throttle and steering
        self.control.wheel_steering = -1
        self.control.wheel_throttle = 0.5
        self.control.brakes = False
        time.sleep(1)

        # Check the rover is moving in an anti-clockwise circle
        self.assertGreater(self.flight.horizontal_speed, 0)
        prev_roll = self.flight.roll
        time.sleep(0.25)
        for i in range(3):
            roll = self.flight.roll
            self.assertGreater(roll, prev_roll)
            prev_roll = roll
            time.sleep(0.25)

        # Apply brakes
        self.control.wheel_steering = 0
        self.control.wheel_throttle = 0
        self.control.brakes = True

        # Wait until the rover has stopped
        while self.flight.horizontal_speed > 0.01:
            time.sleep(0.1)

    def test_steer_right(self):
        self.control = self.conn.space_center.active_vessel.control

        # Check the rover is stationary
        self.assertClose(0, self.flight.horizontal_speed, error=0.01)

        # Forward throttle and steering
        self.control.wheel_steering = 1
        self.control.wheel_throttle = 0.5
        self.control.brakes = False
        time.sleep(0.5)

        # Check the rover is moving in a clockwise circle
        self.assertGreater(self.flight.horizontal_speed, 0)
        prev_roll = self.flight.roll
        time.sleep(0.25)
        for i in range(3):
            roll = self.flight.roll
            self.assertLess(roll, prev_roll)
            prev_roll = roll
            time.sleep(0.25)

        # Apply brakes
        self.control.wheel_steering = 0
        self.control.wheel_throttle = 0
        self.control.brakes = True

        # Wait until the rover has stopped
        while self.flight.horizontal_speed > 0.01:
            time.sleep(0.1)

if __name__ == "__main__":
    unittest.main()