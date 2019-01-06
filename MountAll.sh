#!/bin/bash
sudo mount  //172.16.10.143/buildengine /mnt/BuildEngine -o user=machine
sudo mount.cifs  //hydra/d /mnt/hydra/ -o user=machine,vers=2.1
