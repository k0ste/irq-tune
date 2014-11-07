irq-tune
==========

Manually configure you IRQ setting to performance tune your system. This is 
particularly useful for high bandwidth servers with 40GE NICS and SSD storage


Edit the included JSON file to map IRQs to cores. IRQ can be mapped to multiple
cores if need be

For example:

```json
[
  { "irq": "259", "cores": [36, 37], "slot":"1", "note":"iodrive-0000:0e:00.0-0" },
  { "irq": "290", "cores": [0],  "slot":"3", "note":"mlx1-0" }
}
```

For now only significant fields above are `irq` and `cores`.

You can grep through your proc file system like this:

    cat /proc/interrupts | awk  '{print $1" " $51}' | grep iodrive
    cat /proc/interrupts | awk  '{print $1" " $51}' | grep mlx1

To see how you cores are arranged on your system do this:

```
numactl --hardware | grep cpus
node 0 cpus: 0 4 8 12 16 20 24 28 32 36 40 44
node 1 cpus: 1 5 9 13 17 21 25 29 33 37 41 45
node 2 cpus: 2 6 10 14 18 22 26 30 34 38 42 46
node 3 cpus: 3 7 11 15 19 23 27 31 35 39 43 47
```

    

