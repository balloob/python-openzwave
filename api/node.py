# -*- coding: utf-8 -*-
"""
.. module:: openzwave.node

This file is part of **python-openzwave** project http://code.google.com/p/python-openzwave.
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
import libopenzwave
from collections import namedtuple
import thread
import time
import logging
from openzwave.object import ZWaveException, ZWaveCommandClassException
from openzwave.object import ZWaveObject, NullLoggingHandler, ZWaveNodeInterface
from openzwave.group import ZWaveGroup
from openzwave.value import ZWaveValue
from openzwave.command import ZWaveNodeBasic, ZWaveNodeSwitch
from openzwave.command import ZWaveNodeSensor, ZWaveNodeSecurity

logging.getLogger('openzwave').addHandler(logging.NullHandler())

class ZWaveNode( ZWaveObject,
                 ZWaveNodeBasic, ZWaveNodeSwitch,
                 ZWaveNodeSensor, ZWaveNodeSecurity
                 ):
    """
    Represents a single Node within the Z-Wave Network.

    """

    _isReady = False

    def __init__(self, node_id, network ):
        """
        Initialize zwave node

        :param node_id: ID of the node
        :type node_id: int
        :param network: The network object to access the manager
        :type network: ZWaveNetwork

        """
        logging.debug("Create object node (node_id:%s)" % (node_id))
        ZWaveObject.__init__(self, node_id, network)
        #No cache management for values in nodes
        self.values = dict()
        self._is_locked = False
        self._isReady = False

    def __str__(self):
        """
        The string representation of the node.

        :rtype: str

        """
        return 'home_id: [%s] id: [%s] name: [%s] model: [%s]' % \
          (self._network.home_id_str, self._object_id, self.name, self.product_name)

    @property
    def node_id(self):
        """
        The id of the node.

        :rtype: int

        """
        return self._object_id

    @property
    def name(self):
        """
        The name of the node.

        :rtype: str

        """
        return self._network.manager.getNodeName(self.home_id, self.object_id).decode("UTF-8")

    @name.setter
    def name(self, value):
        """
        Set the name of the node.

        :param value: The new name of the node
        :type value: str

        """
        self._network.manager.setNodeName(self.home_id, self.object_id, value.encode("UTF-8"))

    @property
    def location(self):
        """
        The location of the node.

        :rtype: str

        """
        return self._network.manager.getNodeLocation(self.home_id, self.object_id).decode("UTF-8")

    @location.setter
    def location(self, value):
        """
        Set the location of the node.

        :param value: The new location of the node
        :type value: str

        """
        self._network.manager.setNodeLocation(self.home_id, self.object_id, value.encode("UTF-8"))

    @property
    def product_name(self):
        """
        The product name of the node.

        :rtype: str

        """
        return self._network.manager.getNodeProductName(self.home_id, self.object_id).decode("UTF-8")

    @product_name.setter
    def product_name(self, value):
        """
        Set the product name of the node.

        :param value: The new name of the product
        :type value: str

        """
        self._network.manager.setNodeProductName(self.home_id, self.object_id, value.encode("UTF-8"))

    @property
    def product_type(self):
        """
        The product type of the node.

        :rtype: str

        """
        return self._network.manager.getNodeProductType(self.home_id, self.object_id).decode("UTF-8")

    @property
    def product_id(self):
        """
        The product Id of the node.

        :rtype: str

        """
        return self._network.manager.getNodeProductId(self.home_id, self.object_id).decode("UTF-8")

    @property
    def capabilities(self):
        """
        The capabilities of the node.

        :rtype: set()

        """
        caps = set()
        if self.is_routing_device:
            caps.add('routing')
        if self.is_listening_device:
            caps.add('listening')
        if self.is_frequent_listening_device:
            caps.add('frequent')
        if self.is_security_device:
            caps.add('security')
        if self.is_beaming_device:
            caps.add('beaming')
        if self.node_id == self._network.controller.node_id:
            for cap in self._network.controller.capabilities:
                caps.add(cap)
        return caps

    @property
    def neighbors(self):
        """
        The neighbors of the node.

        :rtype: set()

        """
        return self._network.manager.getNodeNeighbors(self.home_id, self.object_id)

    @property
    def num_groups(self):
        """
        Gets the number of association groups reported by this node.

        :rtype: int

        """
        return self._network.manager.getNumGroups(self.home_id, self.object_id)

    @property
    def groups(self):
        """
        Get the association groups reported by this node

        In Z-Wave, groups are numbered starting from one.  For example, if a call to
        GetNumGroups returns 4, the _groupIdx value to use in calls to GetAssociations
        AddAssociation and RemoveAssociation will be a number between 1 and 4.

        :rtype: dict()

        """
        groups = dict()
        number_groups = self.num_groups
        for i in range(1, number_groups+1):
            groups[i] = ZWaveGroup(i, network=self._network, node_id=self.node_id)
        return groups

    def test(self, count=1):
        """
        Send a number of test messages to every node and record results.

        :param count: The number of test messages to send.
        :type count: int

        """
        self._network.manager.testNetworkNode(self.home_id, self.object_id, count)

    @property
    def command_classes(self):
        """
        The commandClasses of the node.

        :rtype: set()

        """
        command_classes = set()
        for cls in self._network.manager.COMMAND_CLASS_DESC:
            if self._network.manager.getNodeClassInformation(self.home_id, self.object_id, cls):
                command_classes.add(cls)
        return command_classes

    @property
    def command_classes_as_string(self):
        """
        Return the command classes of the node as string.

        :rtype: set()

        """
        commands = self.command_classes
        command_str = set()
        for cls in commands :
            command_str.add(self._network.manager.COMMAND_CLASS_DESC[cls])
        return command_str

    def get_command_class_as_string(self, class_id):
        """
        Return the command class representation as string.

        :param class_id: the COMMAND_CLASS to get string representation
        :type class_id: hexadecimal code
        :rtype: str

        """
        return self._network.manager.COMMAND_CLASS_DESC[class_id].decode("UTF-8")

    def get_command_class_genres(self):
        """
        Return the list of genres of command classes

        :rtype: set()

        """
        return ['User', 'Basic', 'Config', 'System']

    def get_values_by_command_classes(self, genre='All', \
        type='All', readonly='All', writeonly='All'):
        """
        Retrieve values in a dict() of dicts(). The dict is indexed on the COMMAND_CLASS.
        This allows to browse values grouped by the COMMAND_CLASS.You can optionnaly filter for a command class,
        a genre and/or a type. You can also filter readonly and writeonly params.

        This method always filter the values.
        If you wan't to get all the node's values, use the property self.values instead.

        :param genre: the genre of value
        :type genre: 'All' or PyGenres
        :param type: the type of value
        :type type: 'All' or PyValueTypes
        :param readonly: Is this value readonly
        :type readonly: 'All' or True or False
        :param writeonly: Is this value writeonly
        :type writeonly: 'All' or True or False
        :rtype: dict(command_class : dict(valueids))

        """
        values = dict()
        for value in self.values :
            if (genre == 'All' or self.values[value].genre == genre) and \
              (type == 'All' or self.values[value].type == type) and \
              (readonly == 'All' or self.values[value].is_read_only == readonly) and \
              (writeonly == 'All' or self.values[value].is_write_only == writeonly):
                if self.values[value].command_class not in values :
                    values[self.values[value].command_class] = dict()
                values[self.values[value].command_class][value] = self.values[value]
        return values

    def get_values_for_command_class(self, class_id):
        """
        Retrieve the set of values for a command class.
        Deprecated
        For backward compatibility only.
        Use get_values instead

        :param class_id: the COMMAND_CLASS to get values
        :type class_id: hexadecimal code or string
        :type writeonly: 'All' or True or False
        :rtype: set() of classId

        """
        #print class_id
        return self.get_values(class_id=class_id)

    def get_values(self, class_id='All', genre='All', \
        type='All', readonly='All', writeonly='All'):
        """
        Retrieve the set of values. You can optionnaly filter for a command class,
        a genre and/or a type. You can also filter readonly and writeonly params.

        This method always filter the values.
        If you wan't to get all the node's values, use self.values instead.

        :param class_id: the COMMAND_CLASS to get values
        :type class_id: hexadecimal code or string
        :param genre: the genre of value
        :type genre: 'All' or PyGenres
        :param type: the type of value
        :type type: 'All' or PyValueTypes
        :param readonly: Is this value readonly
        :type readonly: 'All' or True or False
        :param writeonly: Is this value writeonly
        :type writeonly: 'All' or True or False
        :rtype: set() of Values

        """
        ret = dict()
        for value in self.values:
            if (class_id == 'All' or self.values[value].command_class == class_id) and \
              (genre == 'All' or self.values[value].genre == genre) and \
              (type == 'All' or self.values[value].type == type) and \
              (readonly == 'All' or self.values[value].is_read_only == readonly) and \
              (writeonly == 'All' or self.values[value].is_write_only == writeonly):
                ret[value] = self.values[value]
        return ret

    def add_value(self, value_id):
        """
        Add a value to the node

        :param value_id: The id of the value to add
        :type value_id: int
        :param command_class: The command_class of the value
        :type command_class: str
        :rtype: bool

        """
        value = ZWaveValue(value_id, network=self.network, parent=self)
        self.values[value_id] = value

    def change_value(self, value_id):
        """
        Change a value of the node.
        Not implemented

        :param value_id: The id of the value to change
        :type value_id: int

        """
        pass

    def refresh_value(self, value_id):
        """
        Refresh a value of the node.
        Not implemented

        :param value_id: The id of the value to change
        :type value_id: int

        """
        return self._network.manager.refreshValue(value_id)

    def remove_value(self, value_id):
        """
        Change a value of the node. Todo

        :param value_id: The id of the value to change
        :type value_id: int
        :return: The result of the operation
        :rtype: bool

        """
        if value_id in self.values :
            logging.debug("Remove value : %s" % self.values[value_id])
            del(self.values[value_id])
            return True
        return False

    def set_field(self, field, value):
        """
        A helper to set a writable field : name, location, product_name, ...

        :param field: The field to set : name, location, product_name, manufacturer_name
        :type field: str
        :param value: The value to set
        :type value: str
        :rtype: bool

        """
        value = value.encode("UTF-8")

        if field == "name":
            self.name=value
        elif field == "location":
            self.location=value
        elif field == "product_name":
            self.product_name=value
        elif field == "manufacturer_name":
            self.manufacturer_name=value

    def has_command_class(self, class_id):
        """
        Check that this node use this commandClass.

        :param classId: the COMMAND_CLASS to check
        :type classId: hexadecimal code
        :rtype: bool

        """
        return class_id in self.command_classes

    @property
    def manufacturer_id(self):
        """
        The manufacturer id of the node.

        :rtype: str

        """
        return self._network.manager.getNodeManufacturerId(self.home_id, self.object_id).decode("UTF-8")

    @property
    def manufacturer_name(self):
        """
        The manufacturer name of the node.

        :rtype: str

        """
        return self._network.manager.getNodeManufacturerName(self.home_id, self.object_id).decode("UTF-8")

    @manufacturer_name.setter
    def manufacturer_name(self, value):
        """
        Set the manufacturer name of the node.

        :param value: The new manufacturer name of the node
        :type value: str

        """
        self._network.manager.setNodeManufacturerName(self.home_id, self.object_id, value.encode("UTF-8"))

    @property
    def generic(self):
        """
        The generic type of the node.

        :rtype: int

        """
        return self._network.manager.getNodeGeneric(self.home_id, self.object_id)

    @property
    def basic(self):
        """
        The basic type of the node.

        :rtype: int

        """
        return self._network.manager.getNodeBasic(self.home_id, self.object_id)

    @property
    def specific(self):
        """
        The specific type of the node.

        :return: The specific type of the node
        :rtype: int

        """
        return self._network.manager.getNodeSpecific(self.home_id, self.object_id)

    @property
    def security(self):
        """
        The security type of the node.

        :return: The security type of the node
        :rtype: int

        """
        return self._network.manager.getNodeSecurity(self.home_id, self.object_id)

    @property
    def version(self):
        """
        The version of the node.

        :return: The version of the node
        :rtype: int

        """
        return self._network.manager.getNodeVersion(self.home_id, self.object_id)

    @property
    def is_listening_device(self):
        """
        Is this node a listening device.

        :rtype: bool

        """
        return self._network.manager.isNodeListeningDevice(self.home_id, self.object_id)

    @property
    def is_beaming_device(self):
        """
        Is this node a beaming device.

        :rtype: bool

        """
        return self._network.manager.isNodeBeamingDevice(self.home_id, self.object_id)

    @property
    def is_frequent_listening_device(self):
        """
        Is this node a frequent listening device.

        :rtype: bool

        """
        return self._network.manager.isNodeFrequentListeningDevice(self.home_id, self.object_id)

    @property
    def is_security_device(self):
        """
        Is this node a security device.

        :rtype: bool

        """
        return self._network.manager.isNodeSecurityDevice(self.home_id, self.object_id)

    @property
    def is_routing_device(self):
        """
        Is this node a routing device.

        :rtype: bool

        """
        return self._network.manager.isNodeRoutingDevice(self.home_id, self.object_id)

    @property
    def is_locked(self):
        """
        Is this node locked.

        :rtype: bool

        """
        return self._is_locked

    @property
    def is_sleeping(self):
        """
        Is this node sleeping.

        :rtype: bool

        """
        return not self.isNodeAwake


#    @property
#    def level(self):
#        """
#        The level of the node.
#        Todo
#        """
#        values = self._getValuesForCommandClass(0x26)  # COMMAND_CLASS_SWITCH_MULTILEVEL
#        if values:
#            for value in values:
#                vdic = value.value_data
#                if vdic and vdic.has_key('type') and vdic['type'] == 'Byte' and vdic.has_key('value'):
#                    return int(vdic['value'])
#        return 0

#    @property
#    def is_on(self):
#        """
#        Is this node On.
#        Todo
#        """
#        values = self._getValuesForCommandClass(0x25)  # COMMAND_CLASS_SWITCH_BINARY
#        if values:
#            for value in values:
#                vdic = value.value_data
#                if vdic and vdic.has_key('type') and vdic['type'] == 'Bool' and vdic.has_key('value'):
#                    return vdic['value'] == 'True'
#        return False

#    @property
#    def signal_strength(self):
#        """
#        The signal strenght of this node.
#        Todo
#        """
#        return 0

    @property
    def max_baud_rate(self):
        """
        Get the maximum baud rate of a node

        """
        return self._network.manager.getNodeMaxBaudRate(self.home_id, self.object_id)

    def refresh_info(self):
        """
        Trigger the fetching of fixed data about a node.

        Causes the nodes data to be obtained from the Z-Wave network in the same way
        as if it had just been added.  This method would normally be called
        automatically by OpenZWave, but if you know that a node has been changed,
        calling this method will force a refresh of the data held by the library.  This
        can be especially useful for devices that were asleep when the application was
        first run.

        :rtype: bool

        """
        return self._network.manager.refreshNodeInfo(self.home_id, self.object_id)#

    def request_all_config_params(self):
        """
        Request the values of all known configurable parameters from a device.

        """
        logging.debug('Requesting config params for node [%s]' % (self.object_id,))
        self._network.manager.requestAllConfigParams(self.home_id, self.object_id)

    def request_config_param(self, param):
        """
        Request the value of a configurable parameter from a device.

        Some devices have various parameters that can be configured to control the
        device behaviour.  These are not reported by the device over the Z-Wave network
        but can usually be found in the devices user manual.  This method requests
        the value of a parameter from the device, and then returns immediately,
        without waiting for a response.  If the parameter index is valid for this
        device, and the device is awake, the value will eventually be reported via a
        ValueChanged notification callback.  The ValueID reported in the callback will
        have an index set the same as _param and a command class set to the same value
        as returned by a call to Configuration::StaticGetCommandClassId.

        :param param: The param of the node.
        :type param:

        """
        logging.debug('Requesting config param %s for node [%s]' % (param, self.object_id))
        self._network.manager.requestConfigParam(self.home_id, self.object_id, param)

    def set_config_param(self, param, value, size=2):
        """
        Set the value of a configurable parameter in a device.

        Some devices have various parameters that can be configured to control the
        device behaviour.  These are not reported by the device over the Z-Wave network
        but can usually be found in the devices user manual.  This method returns
        immediately, without waiting for confirmation from the device that the change
        has been made.

        :param param: The param of the node.
        :type param:
        :param value: The value of the param.
        :type value:
        :param size: Is an optional number of bytes to be sent for the parameter value. Defaults to 2.
        :type size: int
        :return:
        :rtype: bool

        """
        logging.debug('Set config param %s for node [%s]' % (param, self.object_id,))
        return self._network.manager.setConfigParam(self.home_id, self.object_id, param, value, size)

#    def setNodeOn(self, node):
#        """
#        """
#        self._log.debug('Requesting setNodeOn for node {0}'.format(node.id))
#        self._manager.setNodeOn(node.home_id, node.id)

#    def setNodeOff(self, node):
#        """
#        """
#        self._log.debug('Requesting setNodeOff for node {0}'.format(node.id))
#        self._manager.setNodeOff(node.home_id, node.id)

#    def setNodeLevel(self, node, level):
#        """
#        """
#        self._log.debug('Requesting setNodeLevel for node {0} with new level {1}'.format(node.id, level))
#        self._manager.setNodeLevel(node.home_id, node.id, level)

    def isNodeAwake(self):
        """
        Is this node a awake.

        :rtype: bool

        """

        return self._network.manager.isNodeAwake(self.home_id, self.object_id)

    @property
    def isNodeFailed(self):
        """
        Is this node is presume failed.

        :rtype: bool

        """

        return self._network.manager.isNodeFailed(self.home_id, self.object_id)

    @property
    def getNodeQueryStage(self):
        """
        Is this node a awake.

        :rtype: string

        """
        return self._network.manager.getNodeQueryStage(self.home_id, self.object_id).decode("UTF-8")

    @property
    def isReady(self):
        """
        Get whether the node is ready to operate (QueryStage Completed).

        :rtype: bool

        """
        return self._isReady

    @isReady.setter
    def isReady(self, value):
        """
        Set whether the node is ready to operate.
        automatically set to True by notification SIGNAL_NODE_QUERIES_COMPLETE
        
        :param value: is node ready
        :type value: bool

        """
        self._isReady = value

    @property
    def isNodeInfoReceived(self):
        """
        Get whether the node information has been received. Returns True if the node information has been received yet

        :rtype: bool

        """
        return self._network.manager.isNodeInfoReceived(self.home_id, self.object_id)

    @property
    def type(self):
        """
        Get a human-readable label describing the node
        :rtype: str
        """
        return self._network.manager.getNodeType(self.home_id, self.object_id).decode("UTF-8")
