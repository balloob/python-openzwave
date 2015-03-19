# -*- coding: utf-8 -*-
"""
.. module:: openzwave.option

This file is part of **python-openzwave** project https://github.com/bibi21000/python-openzwave.
    :platform: Unix, Windows, MacOS X
    :sinopsis: openzwave API

.. moduleauthor: bibi21000 aka Sébastien GALLET <bibi21000@gmail.com>

License : GPL(v3)

**python-openzwave** is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

**python-openzwave** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with python-openzwave. If not, see http://www.gnu.org/licenses.

"""
import logging
import os
import libopenzwave
from libopenzwave import PyLogLevels

from openzwave.object import ZWaveException

logging.getLogger('openzwave').addHandler(logging.NullHandler())

class ZWaveOption(libopenzwave.PyOptions):
    """
    Represents a Zwave option used to start the manager.

    """
    def __init__(self, device=None, config_path=None, user_path=".", cmd_line=""):
        """
        Create an option object and check that parameters are valid.

        :param device: The device to use
        :type device: str
        :param config_path: The openzwave config directory. If None, try to configure automatically.
        :type config_path: str
        :param user_path: The user directory
        :type user_path: str
        :param cmd_line: The "command line" options of the openzwave library
        :type cmd_line: str

        """
        try:
            if os.path.exists(device):
                if os.access(device, os.R_OK):
                    self._device = device
                else:
                    raise ZWaveException("Can't write to device %s" % device)
            else:
                raise ZWaveException("Can't find device %s" % device)
        except:
            raise ZWaveException("Can't find device %s" % device)
        try:
            if config_path is None:
                config_path = self.getConfigPath()
            if os.path.exists(config_path):
                self._config_path = config_path
                if not os.path.exists(os.path.join(config_path,"zwcfg.xsd")):
                    raise ZWaveException("Can't retrieve zwcfg.xsd from %s" % config_path)
            else:
                raise ZWaveException("Can't retrieve config from %s" % config_path)
        except:
            raise ZWaveException("Can't retrieve config from %s" % config_path)
        try:
            if os.path.exists(user_path):
                if os.access(user_path, os.W_OK):
                    self._user_path = user_path
                else:
                    raise ZWaveException("Can't write in user directory %s" % user_path)
            else:
                raise ZWaveException("Can't find user directory %s" % user_path)
        except:
            raise ZWaveException("Can't find user directory %s" % user_path)
        self._cmd_line = cmd_line

        self.create(
            self._config_path.encode("UTF-8"),
            self._user_path.encode("UTF-8"),
            self._cmd_line.encode("UTF-8"))

    def set_log_file(self, logfile):
        """
        Set the log file location.

        :param logfile: The location of the log file
        :type logfile: str

        """
        return self.addOptionStringUTF8("LogFileName", logfile, False)

    def set_logging(self, status):
        """
        Set the status of logging.

        :param status: True to activate logs, False to disable
        :type status: bool

        """
        return self.addOptionBoolUTF8("Logging", status)

    def set_append_log_file(self, status):
        """
        Append new session logs to existing log file (false = overwrite).

        :param status:
        :type status: bool

        """
        return self.addOptionBoolUTF8("AppendLogFile", status)

    def set_console_output(self, status):
        """
        Display log information on console (as well as save to disk).

        :param status:
        :type status: bool

        """
        return self.addOptionBoolUTF8("ConsoleOutput", status)

    def set_save_log_level(self, level):
        """
        Save (to file) log messages equal to or above LogLevel_Detail.

        :param level:
        :type level: PyLogLevels

            * 'None':"Disable all logging"
            * 'Always':"These messages should always be shown"
            * 'Fatal':"A likely fatal issue in the library"
            * 'Error':"A serious issue with the library or the network"
            * 'Warning':"A minor issue from which the library should be able to recover"
            * 'Alert':"Something unexpected by the library about which the controlling application should be aware"
            * 'Info':"Everything Is working fine...these messages provide streamlined feedback on each message"
            * 'Detail':"Detailed information on the progress of each message" /
            * 'Debug':"Very detailed information on progress that will create a huge log file quickly"
            * 'StreamDetail':"Will include low-level byte transfers from controller to buffer to application and back"
            * 'Internal':"Used only within the log class (uses existing timestamp, etc.)"

        """
        return self.addOptionIntUTF8("SaveLogLevel", PyLogLevels[level])

    def set_queue_log_level(self, level):
        """
        Save (in RAM) log messages equal to or above LogLevel_Debug.

        :param level:
        :type level: PyLogLevels

            * 'None':"Disable all logging"
            * 'Always':"These messages should always be shown"
            * 'Fatal':"A likely fatal issue in the library"
            * 'Error':"A serious issue with the library or the network"
            * 'Warning':"A minor issue from which the library should be able to recover"
            * 'Alert':"Something unexpected by the library about which the controlling application should be aware"
            * 'Info':"Everything Is working fine...these messages provide streamlined feedback on each message"
            * 'Detail':"Detailed information on the progress of each message" /
            * 'Debug':"Very detailed information on progress that will create a huge log file quickly"
            * 'StreamDetail':"Will include low-level byte transfers from controller to buffer to application and back"
            * 'Internal':"Used only within the log class (uses existing timestamp, etc.)"

        """
        return self.addOptionIntUTF8("QueueLogLevel", PyLogLevels[level])

    def set_dump_trigger_level(self, level):
        """
        Default is to never dump RAM-stored log messages.

        :param level:
        :type level: PyLogLevels

            * 'None':"Disable all logging"
            * 'Always':"These messages should always be shown"
            * 'Fatal':"A likely fatal issue in the library"
            * 'Error':"A serious issue with the library or the network"
            * 'Warning':"A minor issue from which the library should be able to recover"
            * 'Alert':"Something unexpected by the library about which the controlling application should be aware"
            * 'Info':"Everything Is working fine...these messages provide streamlined feedback on each message"
            * 'Detail':"Detailed information on the progress of each message" /
            * 'Debug':"Very detailed information on progress that will create a huge log file quickly"
            * 'StreamDetail':"Will include low-level byte transfers from controller to buffer to application and back"
            * 'Internal':"Used only within the log class (uses existing timestamp, etc.)"

        """
        return self.addOptionIntUTF8("DumpTriggerLevel", PyLogLevels[level])

    def set_associate(self, status):
        """
        Enable automatic association of the controller with group one of every device.

        :param status: True to enable logs, False to disable
        :type status: bool

        """
        return self.addOptionBoolUTF8("Associate", status)

    def set_exclude(self, commandClass):
        """
        Remove support for the seted command classes.

        :param commandClass: The command class to exclude
        :type commandClass: str

        """
        return self.addOptionStringUTF8("Exclude", commandClass, True)

    def set_include(self, commandClass):
        """
        Only handle the specified command classes.  The Exclude option is ignored if anything is seted here.

        :param commandClass: The location of the log file
        :type commandClass: str

        """
        return self.addOptionStringUTF8("Include", commandClass, True)

    def set_notify_transactions(self, status):
        """
        Notifications when transaction complete is reported.

        :param status: True to enable, False to disable
        :type status: bool

        """
        return self.addOptionBoolUTF8("NotifyTransactions", status)

    def set_interface(self, port):
        """
        Identify the serial port to be accessed (TODO: change the code so more than one serial port can be specified and HID).

        :param port: The serial port
        :type port: str

        """
        return self.addOptionStringUTF8("Interface", port, True)

    def set_save_configuration(self, status):
        """
        Save the XML configuration upon driver close.

        :param status: True to enable, False to disable
        :type status: bool

        """
        return self.addOptionBoolUTF8("SaveConfiguration", status)

    def set_driver_max_attempts(self, attempts):
        """
        Set the driver max attempts before raising an error.

        :param attempts: Number of attempts
        :type attempts: int

        """
        return self.addOptionIntUTF8("DriverMaxAttempts", attempts)

    def set_poll_interval(self, interval):
        """
        30 seconds (can easily poll 30 values in this time; ~120 values is the effective limit for 30 seconds).

        :param interval: interval in seconds
        :type interval: int

        """
        return self.addOptionIntUTF8("PollInterval", interval)

    def set_interval_between_polls(self, status):
        """
        Notifications when transaction complete is reported.

        :param status: if false, try to execute the entire poll set within the PollInterval time frame. If true, wait for PollInterval milliseconds between polls
        :type status: bool

        """
        return self.addOptionBoolUTF8("IntervalBetweenPolls", status)

    def set_suppress_value_refresh(self, status):
        """
        if true, notifications for refreshed (but unchanged) values will not be sent.

        :param status: True to enable, False to disable
        :type status: bool

        """
        return self.addOptionBoolUTF8("SuppressValueRefresh", status)

    @property
    def device(self):
        """
        The device used by the controller.

        :rtype: str

        """
        return self._device

    @property
    def config_path(self):
        """
        The config path.

        :rtype: str

        """
        return self._config_path

    @property
    def user_path(self):
        """
        The config path.

        :rtype: str

        """
        return self._user_path

    def addOptionIntUTF8(self, option, value):
        return self.addOptionInt(option.encode("UTF-8"), value)

    def addOptionBoolUTF8(self, option, value):
        return self.addOptionBool(option.encode("UTF-8"), value)

    def addOptionStringUTF8(self, option, value, someBool):
        """ Add an UTF-8 option string. """
        return self.addOptionString(
            option.encode("UTF-8"), value.encode("UTF-8"), someBool)
