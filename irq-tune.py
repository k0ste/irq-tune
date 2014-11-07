#!/bin/python

# https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Performance_Tuning_Guide/s-cpu-irq.html
import subprocess
import json
import shlex

def get_mask(selectedcpu):

  cpumask =""
  for cpu in range (0, 48):
    if(cpu == selectedcpu):
      cpumask = "1" + cpumask
    else:
      cpumask = "0" + cpumask
  return cpumask


def add_commas(mask):
  split_mask = [mask[x:x+8] for x in range(0,len(mask),8)]
  comma_sep =""
  for i in range(0,len(split_mask)):
    if (i < 1):
      comma_sep = split_mask[i]
    else:
      comma_sep = comma_sep + "," + split_mask[i]
  return comma_sep
 

def total_mask(cpulist, masktype ):
  masklist = []
  formatted_mask =""
  for cpu in cpulist:
    masklist.append(get_mask(cpu))
  #print masklist
  ormask = int(0)
  for mask in masklist:
    ormask = ormask | int(mask,2)
  #print format(int('11111111',2),'010x')
  if masktype == "binary":
    formatted_mask = format(ormask,'048b')
  else:
    formatted_mask = format(ormask,'016x')
  return add_commas(formatted_mask)

def write_proc(irqlist):

  for irq in irqlist:
    irqmask = total_mask(irq['cores'],"hex")
    irqnumber = irq['irq']
    procname = "/proc/irq/%s/smp_affinity" % ( irqnumber )
    procfile = open(procname,'w')
    procfile.write(irqmask)
    procfile.close()

    print "Set IRQ:%s to cores: %s" % ( irqnumber , ', '.join(str(x) for x in irq['cores']) )
    print "mask: %s procfile: %s" % (irqmask, procname)
 

def main():

  irqlist = [ { 'irq': '259', 'cores': [32] },\
              { 'irq': '370', 'cores': [36]      } ]
  cpulist = [0,1,2,3]

  bmask = total_mask(cpulist,"binary")
  hmask1 = total_mask(cpulist,"hex")
  hmask2 = total_mask(irqlist[0]['cores'],"hex")
  hreal = total_mask([36],"hex")
  #print hmask1
  #print hmask2
  #print hreal

  json_data = open("irq.json").read()
  irqdict = json.loads(json_data)

  #write_proc(irqlist)
  write_proc(irqdict)
  #print(test_load)
 
    #bash_command = "echo \"%s\" > /proc/irq/%s/smp_affinity" % (irqmask, irqnumber)
    #bash_command = "echo 'hello%s' > junk" % ( "doggy")
    #bash_test = "echo 'irq_mask: %s irq_number: %s' " % (irqmask, irqnumber)
    #print bash_command
    #print shlex.split(bash_command),
    #process = subprocess.Popen(shlex.split(bash_command), stdout=subprocess.PIPE)
    #process = subprocess.Popen([r"echo","'hollow blix'"], stdout=open("/root/irq/junk",'w'))
    #output = process.communicate()[0]
    #print output



if __name__ == "__main__":
  main()
