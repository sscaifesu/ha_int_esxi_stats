"""Sensor platform for esxi_stats."""
import logging
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, DOMAIN_DATA, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    for cond in hass.data[DOMAIN_DATA]["monitored_conditions"]:
        for obj in hass.data[DOMAIN_DATA][cond]:
            async_add_entities([esxiSensor(hass, discovery_info, cond, obj)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    config = config_entry.data
    for cond in hass.data[DOMAIN_DATA]["monitored_conditions"]:
        for obj in hass.data[DOMAIN_DATA][cond]:
            async_add_devices([esxiSensor(hass, config, cond, obj, config_entry)], True)


class esxiSensor(Entity):
    """ESXi_stats Sensor class."""

    def __init__(self, hass, config, cond, obj, config_entry=None):
        """Init."""
        self.hass = hass
        self.attr = {}
        self._config_entry = config_entry
        self._state = None
        self.config = config
        self._options = self._config_entry.options
        self._cond = cond
        self._obj = obj
        self._name = self._obj

    async def async_update(self):
        """Update the sensor."""
        await self.hass.data[DOMAIN_DATA]["client"].update_data()
        self._data = self.hass.data[DOMAIN_DATA][self._cond][self._obj]

        # Set vmhost state and measurement
        if self._cond == "vmhost":
            self._state = self._data[self._options["host_state"]]
            self._measurement = measureFormat(self._options["host_state"])

        # Set datastore state and measurement
        if self._cond == "datastore":
            self._state = self._data[self._options["ds_state"]]
            self._measurement = measureFormat(self._options["ds_state"])

        # Set license state and measurement
        if self._cond == "license":
            self._state = self._data[self._options["license_state"]]
            self._measurement = measureFormat(self._options["license_state"])

        # Set VM state and measurement
        if self._cond == "vm":
            self._state = self._data[self._options["vm_state"]]
            self._measurement = measureFormat(self._options["vm_state"])

        # Set attributes
        for key, value in self._data.items():
            self.attr[key] = value

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return "{}_52446d23-5e54-4525-8018-56da195d276f_{}_{}".format(
            self.config["host"].replace(".", "_"), self._cond, self._obj
        )

    @property
    def should_poll(self):
        """Return the name of the sensor."""
        return True

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{} {} {}".format(DEFAULT_NAME, self._cond, self._name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._measurement

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr

    @property
    def device_info(self):
        """Return device info for this sensor."""
        if self._config_entry is None:
            indentifier = {(DOMAIN, self.config["host"].replace(".", "_"))}
        else:
            indentifier = {(DOMAIN, self._config_entry.entry_id)}
        return {
            "identifiers": indentifier,
            "name": "ESXi Stats",
            "manufacturer": "VMware, Inc.",
        }


def measureFormat(input):
    """Returns measurement in readable form"""
    return input.replace("_", " ").title()
