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
import shlex
import os
import csv
import pprint
from optparse import OptionParser


def get_device_irq_dict():

    devicemap = {}
    for line in csv.reader(open("/proc/interrupts"), delimiter=' '):
        devicemap[line[-1]] = line[1].translate(None,':')
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
        procname = "/proc/irq/%s/smp_affinity" % (irqnumber)
        if os.path.exists(procname):
            procfile = open(procname, 'w')
            procfile.write(irqmask)
            procfile.close()
            print "Set IRQ:%s to cores: %s" % (irqnumber, ', '.join(str(x) for x in irq['cores']))
            print "mask: %s procfile: %s" % (irqmask, procname)
        else:
            print "****** ERROR ****** The irq %s, for %s  does not exists" % ( irqnumber, irq['name'] )


def main():

    # Example irq data structure
    # irqlist = [ { 'irq': '259', 'cores': [32,21] },\
    #            { 'irq': '370', 'cores': [36]      } ]

    parser = OptionParser(usage="%prog -j JSONFILE",version = "%prog 0.1")
    parser.add_option("-j", "--json", dest="jsonfile",
            help="the json configuration file", metavar="JSONFILE")
    parser.add_option("-a","--auto-irq",action="store_true", dest="auto_irq", default=False,
            help="look up the IRQs from device names")
    (options,args) = parser.parse_args()

    if not options.jsonfile:
        parser.print_help()
        parser.error("You must specify a json file with -j or --json")
    if not os.path.exists(options.jsonfile):
        parser.parse_args()
        parse.error("The file: " + options.jsonfile + "does not exist.")


    #json_data = open("irq.json").read()
    json_data = open(options.jsonfile).read()
    irqdict = json.loads(json_data)

    if options.auto_irq:
        reset_irq_on_device(irqdict)

    write_proc(irqdict)

if __name__ == "__main__":
    main()

# Some debugging junk
#
#  ddpprint.pprint(irqdict,width=120)
#  bmask = total_mask(cpulist,"binary")
#  hmask1 = total_mask(cpulist,"hex")
#  hmask2 = total_mask(irqlist[0]['cores'],"hex")
#  hreal = total_mask([36],"hex")
#  print hmask2
#  print hreal
