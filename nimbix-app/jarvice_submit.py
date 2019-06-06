#!/usr/bin/python
#A wrapper around jarvice_cli to submit a job and wait for it to end

from __future__ import print_function
import os
from subprocess import check_output, check_call
import json
import jinja2
import argparse
import sys
import traceback
import logging

#Username and Apikey
username = ""
apikey = ""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def exec_and_wait(job_json):
       out = check_output(["jarvice_cli", "-username", username, "-apikey", apikey, "submit", "-j", job_json])
       data = json.loads(out)
       job_id = str(data['number'])
       print("job id is " + job_id)
       logger.info("job id is %s ", job_id)
       if job_id:
           out = check_output(["jarvice_cli", "-username", username, "-apikey", apikey, "wait_for", "-number", job_id ])
           logger.info("job %s terminated", job_id)
           return 0
       print("failed to submit job")
       logger.error("failed to submit job")
       return 1


def exec_and_wait_dry_run(job_json):
        logger.info("command to be executed is:")
        logger.info("jarvice_cli -username %s -apikey %s submit -j %s", username, apikey, job_json)
        return 0

#Find relevant machine type based on number of CPUs and GPUs
#This method assumes that the required cpus and gpus exactly matches
#with Nimbix provided resource types
#Example JSON o/p
'''
{
    "nc3": {
        "mc_scale_max": 128,
        "mc_slave_gpus": 0,
        "mc_scratch": 100,
        "mc_scale_min": 1,
        "mc_ram": 128,
        "mc_swap": 64,
        "mc_description": "16 core, 128GB RAM (accelerated OpenGL on master)",
        "mc_price": 2.5,
        "mc_gpus": 1,
        "mc_slave_ram": 128,
        "mc_cores": 16,
        "mc_scale_select": ""
    },
    "nc5": {
        "mc_scale_max": 2,
        "mc_slave_gpus": 0,
        "mc_scratch": 300,
        "mc_scale_min": 1,
        "mc_ram": 512,
        "mc_swap": 64,
        "mc_description": "16 core, 512GB RAM (accelerated OpenGL on master)",
        "mc_price": 6.52,
        "mc_gpus": 0,
        "mc_slave_ram": 512,
        "mc_cores": 16,
        "mc_scale_select": ""
    }
}
'''
def get_mc_type(num_cpus, num_gpus, arch):

   if arch == "INTEL":
       default_mc_type = "nc3"
   if arch == "POWER":
       default_mc_type = "np8c0"

   out = check_output(["jarvice_cli", "-username", username, "-apikey", apikey, "machines"])
   data = json.loads(out)
   #{mc_type: [ ram, cores, gpus]
   mc_list = {}
   logger.debug("List of machines in Nimbix %s", data)
   for key, value in data.iteritems():
       logger.debug("key: %s, mc_ram: %d, mc_cores: %d, mc_gpus: %d", key, value['mc_ram'], value['mc_cores'], value['mc_gpus'])
       logger.debug("mc_description: %s", value['mc_description'])
       if arch not in value['mc_description']:
           continue
       mc_list[key] = [ value['mc_ram'], value['mc_cores'], value['mc_gpus']]

   for mc_type, values in mc_list.iteritems():
      if str(values[1]) == str(num_cpus) and str(values[2]) == str(num_gpus):
          return mc_type
   return default_mc_type

def find_best_fit(num_res, sorted_list):
   logger.debug("sorted_list: %s, num_res: %d", sorted_list, num_res)
   return min(sorted_list, key=lambda x:abs(x - num_res))

'''
Get the machine type which is closest to the required resources
'''
def get_mc_type_best_fit(num_cpus, num_gpus, arch):

   if arch == "INTEL":
       default_mc_type = "nc3"
   if arch == "POWER":
       default_mc_type = "np8c0"

   cpu_list = []
   gpu_list = []
   out = check_output(["jarvice_cli", "-username", username, "-apikey", apikey, "machines"])
   data = json.loads(out)
   #{mc_type: [ ram, cores, gpus]
   mc_list = {}
   for key, value in data.iteritems():
       logger.debug("key: %s, mc_ram: %d, mc_cores: %d, mc_gpus: %d", key, value['mc_ram'], value['mc_cores'], value['mc_gpus'])
       logger.debug("mc_description: %s", value['mc_description'])
       if arch not in value['mc_description']:
           continue
       mc_list[key] = [ value['mc_ram'], value['mc_cores'], value['mc_gpus']]
       cpu_list.append(value['mc_cores'])
       gpu_list.append(value['mc_gpus'])

   logger.debug("CPU list: %s", cpu_list)
   logger.debug("GPU list: %s", gpu_list)
   logger.debug("Machine list: %s", mc_list)
   cpus = find_best_fit(num_cpus, sorted(set(cpu_list)))
   logger.info("Required cpus: %d", cpus)
   gpus = find_best_fit(num_gpus, sorted(set(gpu_list)))
   logger.info("Required gpus: %d", gpus)

   for mc_type, values in mc_list.iteritems():
      #Find best fit machine having required cpu and gpus
      if str(values[1]) == str(cpus) and str(values[2]) == str(gpus):
          return mc_type
      #What if best fit is not available in the list
   return default_mc_type


def create_job_json(app_name, app_command, app_command_args, mc_type):
   template_loader = jinja2.FileSystemLoader( searchpath="./")
   template_env = jinja2.Environment( loader=template_loader )
   TEMPLATE_FILE = "/job_template.json"
   template = template_env.get_template( TEMPLATE_FILE )
   json_text = template.render(app_name=app_name, command=app_command, command_args=app_command_args, mc_type=mc_type)

   logger.debug("Json Job Description: %s", json_text)

   with open('/job.json', 'wb') as outfile:
       outfile.write(json_text)
       #This is required otherwise JSON parsing will fail
       outfile.write('\n')

   outfile.close()

def remote_exec():
   global username
   global apikey
   parser = argparse.ArgumentParser()
   parser.add_argument('--log_level', type=str, default='INFO', help='Log level - INFO, DEBUG')
   parser.add_argument('--dry_run', action='store_true', help='Dry Run - just dump the complete remote command')
   args = parser.parse_args()

   if args.log_level == "INFO":
       logger.setLevel(logging.INFO)
   if args.log_level == "DEBUG":
       logger.setLevel(logging.DEBUG)


   username = os.environ.get("USERNAME")
   apikey = os.environ.get("APIKEY")
   app_name = os.environ.get("APP_NAME")
   app_command = os.environ.get("APP_COMMAND")
   #App command args is optional. For batch jobs its required though
   app_command_args = os.environ.get("APP_COMMAND_ARGS")

   if username == None or apikey == None or app_name == None or app_command == None:
       logger.critical("Username, APIKey, App Name and Command  are must")
       sys.exit()

   #Get required CPUs and GPUs. Default 1
   num_cpus = os.getenv("NUM_CPUS", 1)
   num_gpus = os.getenv("NUM_GPUS", 1)
   arch = os.getenv("ARCH", "POWER")

   logger.debug("APP_NAME: %s APP_COMMAND: %s, APP_COMMAND_ARGS: %s, NUM_CPUS: %s, NUM_GPUS: %s", app_name, app_command, 
                                         app_command_args, num_cpus, num_gpus)

   try:
      if args.dry_run:
         exec_and_wait_dry_run("/job.json")
      else: 
         mc_type = get_mc_type_best_fit(int(num_cpus), int(num_gpus), arch)
         logger.info("machine type to be used: %s", mc_type)
         create_job_json(app_name, app_command, app_command_args, mc_type)
         if exec_and_wait("/job.json"):
             logger.info("Error in running jarvice job")

   except Exception as e:
       logger.error('Unexpected error when running jarvice_cli', exc_info=True)

def main():
   if os.environ.get("REMOTE") :
       remote_exec()
   else:
       #Execute the command as-is
       app_command_args = os.environ.get("APP_COMMAND_ARGS")
       try:
           check_call(["/bin/bash", "-c", app_command_args])
       except Exception as e:
           logger.error('Unexpected error when running command', exc_info=True)

if __name__== "__main__":
   main()
