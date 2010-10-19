#!/usr/bin/env python
"""
Copyright 2010 Free Software Foundation, Inc.

This file is part of GNU Radio

GNU Radio Companion is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

GNU Radio Companion is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

MAIN_TMPL = """\
<?xml version="1.0"?>
<block>
	<name>UHD: Single USRP $sourk.title()</name>
	<key>uhd_single_usrp_$(sourk)</key>
	<import>from gnuradio import uhd</import>
	<make>uhd.single_usrp_$(sourk)(
	device_addr=\$dev_addr,
	io_type=uhd.io_type_t.\$type.type,
	num_channels=\$nchan,
)
self.\$(id).set_subdev_spec(\$sd_spec)
self.\$(id).set_samp_rate(\$samp_rate)
#for $n in range($max_nchan)
\#if \$nchan() > $n
self.\$(id).set_center_freq(\$center_freq$(n), $n)
self.\$(id).set_gain(\$gain$(n), $n)
	\#if \$ant$(n)()
self.\$(id).set_antenna(\$ant$(n), $n)
	\#end if
\#end if
#end for
</make>
	<callback>set_samp_rate(\$samp_rate)</callback>
	#for $n in range($max_nchan)
	<callback>set_center_freq(\$center_freq$(n), $n)</callback>
	<callback>set_gain(\$gain$(n), $n)</callback>
	<callback>set_antenna(\$ant$(n), $n)</callback>
	#end for
	<param>
		<name>Input Type</name>
		<key>type</key>
		<type>enum</type>
		<option>
			<name>Complex</name>
			<key>complex</key>
			<opt>type:COMPLEX_FLOAT32</opt>
			<opt>vlen:1</opt>
		</option>
		<option>
			<name>Short</name>
			<key>short</key>
			<opt>type:COMPLEX_INT16</opt>
			<opt>vlen:2</opt>
		</option>
	</param>
	<param>
		<name>Num Channels</name>
		<key>nchan</key>
		<value>1</value>
		<type>int</type>
		<hide>part</hide>
		<option>
			<name>Single Channel</name>
			<key>1</key>
		</option>
		<option>
			<name>Dual Channel</name>
			<key>2</key>
		</option>
		<option>
			<name>Quad Channel</name>
			<key>4</key>
		</option>
	</param>
	<param>
		<name>Device Addr</name>
		<key>dev_addr</key>
		<value>addr=192.168.10.2</value>
		<type>string</type>
		<hide>
			\#if \$dev_addr()
				none
			\#else
				part
			\#end if
		</hide>
	</param>
	<param>
		<name>Subdev Spec</name>
		<key>sd_spec</key>
		<value></value>
		<type>string</type>
		<hide>
			\#if \$sd_spec()
				none
			\#else
				part
			\#end if
		</hide>
	</param>
	<param>
		<name>Samp Rate (Sps)</name>
		<key>samp_rate</key>
		<value>samp_rate</value>
		<type>real</type>
	</param>
	$params
	<check>$max_nchan >= \$nchan</check>
	<check>\$nchan > 0</check>
	<check>(len((\$sd_spec).split()) or 1) == \$nchan</check>
	<$sourk>
		<name>$direction</name>
		<type>\$type</type>
		<vlen>\$type.vlen</vlen>
		<nports>\$nchan</nports>
	</$sourk>
	<doc>
The UHD Single USRP $sourk.title() Block:

Device Address:
The device address is a delimited string used to locate UHD devices on your system. \\
If left blank, the first UHD device found will be used. \\
Used args to specify a specfic device.
USRP2 Example: addr=192.168.10.2
USRP1 Example: serial=12345678

Sample rate:
The sample rate is the number of samples per second input by this block. \\
The UHD device driver will try its best to match the requested sample rate. \\
If the requested rate is not possible, the UHD block will print an error at runtime.

Subdevice specification:
Select the subdevice or subdevices for each channel using a markup string. \\
The markup string consists of a list of dboard_slot:subdev_name pairs (one pair per channel). \\
If left blank, the UHD will try to select the first subdevice on your system. \\
See the application notes for further details.
Single channel example: A:AB
Dual channel example: A:AB B:0

Antenna:
For subdevices/daughterboards with only one antenna, this may be left blank. \\
Otherwise, the user should specify one of the possible antenna choices. \\
See the daughterboard application notes for the possible antenna choices.
	</doc>
</block>
"""

PARAMS_TMPL = """
	<param>
		<name>Ch$(n): Center Freq (Hz)</name>
		<key>center_freq$(n)</key>
		<value>0</value>
		<type>real</type>
		<hide>\#if \$nchan() > $n then 'none' else 'all'#</hide>
	</param>
	<param>
		<name>Ch$(n): Gain (dB)</name>
		<key>gain$(n)</key>
		<value>0</value>
		<type>real</type>
		<hide>\#if \$nchan() > $n then 'none' else 'all'#</hide>
	</param>
	<param>
		<name>Ch$(n): Antenna</name>
		<key>ant$(n)</key>
		<value></value>
		<type>string</type>
		<hide>
			\#if not \$nchan() > $n
				all
			\#elif \$ant$(n)()
				none
			\#else
				part
			\#end if
		</hide>
	</param>
"""

def parse_tmpl(_tmpl, **kwargs):
	from Cheetah import Template
	return str(Template.Template(_tmpl, kwargs))

max_num_channels = 4

if __name__ == '__main__':
	import sys
	for file in sys.argv[1:]:
		if 'source' in file:
			sourk = 'source'
			direction = 'out'
		elif 'sink' in file:
			sourk = 'sink'
			direction = 'in'
		else: raise Exception, 'is %s a source or sink?'%file

		params = ''.join([parse_tmpl(PARAMS_TMPL, n=n) for n in range(max_num_channels)])
		open(file, 'w').write(parse_tmpl(MAIN_TMPL,
			max_nchan=max_num_channels,
			params=params,
			sourk=sourk,
			direction=direction,
		))
