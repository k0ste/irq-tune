#!/bin/python
# vim: set expandtab ts=4 sw=4:

# irq-tune
#
# Author: Ian Gable <igable@uvic.ca>
#
# Read this to understand more about what this script does:
# https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Performance_Tuning_Guide/s-cpu-irq.html
#
#

import subprocess
import json
import os, sys
import csv
from optparse import OptionParser

def get_device_irq_dict():

    devicemap = {}
    for line in csv.reader(open("/proc/interrupts"), delimiter=' '):
        # IRQ number < 100, most of single CPU systems (like Xeon E3)
        if line[1] == "":
            if sys.version_info.major < 3:
                devicemap[line[-1]] = line[2].translate(None, ':')
            else:
                map = str.maketrans('', '', ':')
                devicemap[line[-1]] = line[2].translate(map)
        # IRQ number > 100, more than one CPU or many queues
        else:
            if sys.version_info.major < 3:
                devicemap[line[-1]] = line[1].translate(None, ':')
            else:
                map = str.maketrans('', '', ':')
                devicemap[line[-1]] = line[1].translate(map)
    return devicemap

def reset_irq_on_device(irqdict):

    devicemap = get_device_irq_dict()

    for irq in irqdict:
        irq['irq'] = devicemap[irq['name']]

def get_mask(selectedcpu):

    cpumask = ""
    for cpu in range(0, 48):
        if(cpu == selectedcpu):
            cpumask = "1" + cpumask
        else:
            cpumask = "0" + cpumask
    return cpumask

def add_commas(mask):

    split_mask = [mask[x:x + 8] for x in range(0, len(mask), 8)]
    comma_sep = ""
    for i in range(0, len(split_mask)):
        if (i < 1):
            comma_sep = split_mask[i]
        else:
            comma_sep = comma_sep + "," + split_mask[i]
    return comma_sep

def total_mask(cpulist, masktype):

    masklist = []
    formatted_mask = ""
    for cpu in cpulist:
        masklist.append(get_mask(cpu))
    ormask = int(0)
    for mask in masklist:
        ormask = ormask | int(mask, 2)
    if masktype == "binary":
        formatted_mask = format(ormask, '048b')
    else:
        formatted_mask = format(ormask, '016x')
    return add_commas(formatted_mask)


def write_proc(irqlist):

    for irq in irqlist:
        irqmask = total_mask(irq['cores'], "hex")
        irqnumber = irq['irq']
        procname = "/proc/irq/{0}/smp_affinity".format(irqnumber)
        if os.path.exists(procname):
            procfile = open(procname, 'w')
            procfile.write(irqmask)
            procfile.close()
            print("Set IRQ [{0}]: {1} to cores: {2}".format(irq['name'], irqnumber, ', '.join(str(x) for x in irq['cores'])))
            print("mask: {0} procfile: {1}".format(irqmask, procname))
        else:
            print("****** ERROR ****** The IRQ {0}, for {1} does not exists".format(irqnumber, irq['name']))

def main():

    parser = OptionParser(usage="%prog -j JSONFILE", version="%prog 0.1")
    parser.add_option("-j", "--json", dest="jsonfile",
            help="the json configuration file", metavar="JSONFILE")
    parser.add_option("-a", "--auto-irq", action="store_true", dest="auto_irq",
            default=False, help="look up the IRQs from device names")
    (options,args) = parser.parse_args()

    if not options.jsonfile:
        parser.print_help()
        parser.error("You must specify a json file with -j or --json")
    if not os.path.exists(options.jsonfile):
        parser.parse_args()
        parse.error("The file: " + options.jsonfile + "does not exist.")

    json_data = open(options.jsonfile).read()
    irqdict = json.loads(json_data)

    if options.auto_irq:
        reset_irq_on_device(irqdict)

    write_proc(irqdict)

if __name__ == "__main__":
    main()
