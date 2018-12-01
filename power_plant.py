#!/usr/bin/env python3
"""
Main PowerPlant Application
"""

from time import sleep
from math import sqrt
from math import atan2
from math import degrees

from ad_interface import AD
from ad_mcp import AdMcp3008
from DirectionFinder import DirectionFinder
from prox_reader import ProxReader
from CartMoveController import CartMoveController

def wake_and_shake(cart):
    """
    This function provides feedback that the cart is powered and booted
    by moving around in a simple pattern.
    """
    cart.make_a_move(3, 0)
    cart.make_a_move(-3, 0)
    cart.make_a_move(3, 0)
    cart.make_a_move(-3, 0)
    cart.make_a_move(3, 0)
    cart.make_a_move(-3, 0)
    cart.make_a_move(0, 5)
    cart.make_a_move(0, -5)


def power_plant_main():
    """
    This function defines the basic behavior of the PowerPlant embedded system.

    The specific implementations are encapsulated within the concrete classes
    created here, but no matter the implementation the basic procedure followed
    by the PowerPlant is:
    - Capture Light data
    - Determine next maneuver
    - Capture proximity data
    - Make next maneuver if safe
    - Capture Light data
    - If at optimal location, sleep for a while
    - Repeat above forever
    """

    # Initialize the interface to the A/D
    concrete_ad = AdMcp3008()
    ad_interface = AD(concrete_ad, 8)

    # Initialize the locations of the light sensors
    root_two_over_two = sqrt(2) / 2
    light_sensor_positions = [
        (0, 30),
        (30 * root_two_over_two, 30 * root_two_over_two),
        (30, 0),
        (30 * root_two_over_two, -30 * root_two_over_two),
        (0, -30),
        (-30 * root_two_over_two, -30 * root_two_over_two),
        (-30, 0),
        (-30 * root_two_over_two, 30 * root_two_over_two),
        ]

    # Instantiate the DirectionFinder
    dfer = DirectionFinder()

    # Initialize the peak light intensity
    peak_intensity = 0

    # Instantiate the proximity sensor reader
    proximity = ProxReader('mm')

    cart = CartMoveController(20)

    wake_and_shake(cart)

    while True:
        # Get all the light sample data
        current_light_intensity = ad_interface.get_samples()
        if peak_intensity < sum(current_light_intensity):
            peak_intensity = sum(current_light_intensity)

        # Reformat the light sample data to append the sensor location so the
        # DirectionFinder can use it
        formatted_light_intensity = []
        for index, sample in enumerate(current_light_intensity):
            formatted_light_intensity.append({
                'amp':sample, 'location':light_sensor_positions[index]
                })

        next_move = dfer.FindDirection(formatted_light_intensity)

        # Get the latest proximity data
#        clearances = proximity.measure()

        if all(distance > 30 for distance in clearances):
            turn_angle = degrees(atan2(next_move[0], next_move[1]))
            if turn_angle > 180:
                turn_angle = turn_angle - 360
            cart.make_a_move(turn_angle, 5)

        current_light_intensity = ad_interface.get_samples()

        if sum(current_light_intensity) < peak_intensity:
            # We are a little off the peak, so hang out here for a while
#            sleep(15 * 60)
            sleep(15)
            # Reset peak intensity so our algorithm searches again
            peak_intensity = 0


if __name__ == "__main__":
    power_plant_main()
