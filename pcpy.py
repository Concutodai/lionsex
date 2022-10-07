from subprocess import Popen, PIPE, DEVNULL
from os import environ, getlogin
from os.path import isfile, exists
from shutil import which
import platform
import psutil
import socket
import getpass
import time
#from logos import logo_array

Debug = False

def run_command(command):
    process = Popen(command, stdout=PIPE, universal_newlines=True, shell=True,stderr=DEVNULL)
    stdout, stderr = process.communicate()
    del stderr
    return stdout

def os_name():
    if isfile('/bedrock/etc/os-release'):
        os_file = '/bedrock/etc/os-release'
    elif isfile('/etc/os-release'):
        os_file = '/etc/os-release'


    pretty_name = run_command(("cat "+os_file+" | grep 'PRETTY_NAME'")).replace("PRETTY_NAME=", "").replace('''"''', "")
    return pretty_name


def model_info():
    product_info = ""
    if exists("/sys/devices/virtual/dmi/id/product_name"):
        with open("/sys/devices/virtual/dmi/id/product_name", "r") as f:
            line = f.read().rstrip('\n')
            product_info = line

    if exists("/sys/devices/virtual/dmi/id/product_version"):
        line = run_command("cat /sys/devices/virtual/dmi/id/product_version").rstrip('\n')
        if product_info == "":
            product_info = line
        else:
            product_info = str(product_info+" "+line)
    return product_info


def misc_func():
    try:
      shell_name = environ["SHELL"].split('/')[-1]
    except:
      try:
        shell_name = environ["SHELL"].split('/')[0]
      except:
        try:
          shell_name = environ["SHELL"].split('/')[1]
        except:
          shell_name = 'Unknown (bash?)'
    
    shell_ver = ""
    if shell_name == "fish":
        shell_ver = run_command("fish --version").replace("fish, version ","")
    elif shell_name == "bash":
        shell_ver = environ['BASH_VERSION'].split('(')[0]
    if shell_ver != "":
        shell = str(shell_name+" "+shell_ver).rstrip('\n')
    else:
        shell = shell_name
    
    resolution = run_command("cat /sys/class/drm/*/modes").split('\n')[0]
    terminal_emu = environ["TERM"]
    kernel = run_command("uname -r")
    uptime = run_command("uptime -p").replace("up ", "")
    return shell, resolution, terminal_emu, kernel, uptime

def pac_msg_util(input, pac_manager, pac_msg):
    return f'{pac_msg} {str(input)} ({pac_manager})'

def pac_msg_append(command, pac_manager, pac_msg):
    binary = command.split(" ")[0]
    if which(binary) != None:
        num = len(run_command(command).splitlines())
        if num != 0:
            return pac_msg_util(len(run_command(command).splitlines()), pac_manager, pac_msg)
        else:
            return pac_msg
    else:
        return pac_msg

def hostname():
    username = environ['USER']
    try:
      hostname = run_command('hostname').rstrip('\n')
    except:
      hostname = ''
    
    try:
      if len(hostname) <= 0:
        hostname = socket.gethostname()
    except:
      pass
      
    try:
      if len(hostname) <= 0:
        hostname = platform.node()
    except:
      pass
      
    try:
      if len(hostname) <= 0:
        hostname = socket.getfqdn()
    except:
      pass

    try:
      if len(hostname) <= 0:
        hostname = environ['COMPUTERNAME']
    except:
      pass

    if len(hostname) <= 0:
      hostname = 'Unknown'
    
    return f'{username}@{hostname}'

def pac_msg_madness():
    pac_msg = "Packages:"
    pac_msg = pac_msg_append("kiss -l", "kiss", pac_msg)
    pac_msg = pac_msg_append("pacman -Qq --color never", "pacman", pac_msg)
    pac_msg = pac_msg_append("dpkg-query -f '.\n' -W", "dpkg", pac_msg)
    pac_msg = pac_msg_append("rpm -qa", "rpm", pac_msg)
    pac_msg = pac_msg_append("xbps-query -l", "xbps", pac_msg)
    pac_msg = pac_msg_append("apk info", "apk", pac_msg)
    pac_msg = pac_msg_append("opkg list-installed", "opkg", pac_msg)
    pac_msg = pac_msg_append("pacman-g2 -Q", "pacman-g2", pac_msg)
    pac_msg = pac_msg_append("lvu installed", "lvu", pac_msg)
    pac_msg = pac_msg_append("tce-status -i", "tce-status", pac_msg)
    pac_msg = pac_msg_append("pkg_info", "pkg_info", pac_msg)
    pac_msg = pac_msg_append("tazpkg list", "tazpkg", pac_msg)
    pac_msg = pac_msg_append("gaze installed", "sorcery", pac_msg)
    pac_msg = pac_msg_append("alps showinstalled", "alps", pac_msg)
    pac_msg = pac_msg_append("butch list", "butch", pac_msg)
    pac_msg = pac_msg_append("mine -q", "mine", pac_msg)
    return pac_msg


def de_info():
    try:
      de = environ['DESKTOP_SESSION']
    except:
      de = "Unknown"
      
    if de.lower() == 'gnome'.lower():
        wm = "Mutter"
    else:
        wm = "Unknown"
    wmtheme, theme, icons = "", "", ""
    return de, wm, wmtheme, theme, icons

#cpu stuff
def fetch_cpu_info():
    cpu_count = len(run_command("ls /sys/class/cpuid/ | sort").split('\n')) - 1 
    cpu_info = run_command("cat /proc/cpuinfo | grep 'model name'").split('\n')[0].replace("model name	: ","").replace("Core(TM)","").replace("(R)","").replace("CPU","").replace("  "," ").split('@')[0]
    try:
      cpu_max_freq = int(run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"))
    except:
      cpu_max_freq = 0

    cpu_max_freq_mhz = cpu_max_freq / 1000
    cpu_max_freq_ghz = cpu_max_freq / 1000 / 1000

    if cpu_max_freq_ghz > 1:
        cpu_freq_info = str(str(round(cpu_max_freq_ghz, 3))+"GHz")
    else:
        cpu_freq_info = str(str(round(cpu_max_freq_mhz, 3))+"MHz")

    full_cpu_info = f'{cpu_info}({cpu_count}) @ {cpu_freq_info}'
    del cpu_freq_info, cpu_count, cpu_info, cpu_max_freq_mhz, cpu_max_freq_ghz
    return full_cpu_info


def non_debug():
    pac_msg = pac_msg_madness()
    full_cpu_info = fetch_cpu_info()
    product_info = model_info()
    pretty_name = os_name()
    hostname_info = hostname()
    shell, resolution, terminal_emu, kernel, uptime = misc_func()
    gpu, memory = "", ""
    return pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime, hostname_info, gpu, memory

def debug():
    global pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime, hostname
    total_time = 0

    start_time = time.time()
    hostname = hostname()
    end_time = time.time()
    hostname_time = end_time - start_time
    total_time += hostname_time
    print("hostname time:",str(round(hostname, 5)))

    start_time = time.time()
    pac_msg = pac_msg_madness()
    end_time = time.time()
    pac_msg_time = end_time - start_time
    total_time += pac_msg_time
    print("pac_msg time:",str(round(pac_msg_time, 5)))

    start_time = time.time()
    full_cpu_info = fetch_cpu_info()
    end_time = time.time()
    cpu_time = end_time - start_time
    total_time += cpu_time
    print("cpu time:",str(round(cpu_time, 5)))

    start_time = time.time()
    product_info = model_info()
    end_time = time.time()
    model_time = end_time - start_time
    total_time += model_time
    print("model_info time:",str(round(model_time, 5)))

    start_time = time.time()
    pretty_name = os_name()
    end_time = time.time()
    os_time = end_time - start_time
    total_time += os_time
    print("os_name time:",str(round(os_time, 5)))

    start_time = time.time()
    shell, resolution, terminal_emu, kernel, uptime = misc_func()
    end_time = time.time()
    misc_func_time = end_time - start_time
    total_time += misc_func_time
    print("Misc function time:",str(round(misc_func_time, 5)))

    print("Total time:",str(round(total_time, 5))+'\n')
# debug()

#def dash_gen(num):
#    result = ""
#    for i in range(num):
#        result = str(result+"-")
#    return result

def space_gen(num):
    result = ""
    for i in range(num):
        result = str(result+" ")
    return result

def get_ram():
  ram_info = f'{int(psutil.virtual_memory()[3]/1e+6)}MiB / {int(psutil.virtual_memory()[0]/1e+6)}MiB'
  
  return ram_info

def seconds_elapsed():
    uptime_info = f'{int(int(time.time() - psutil.boot_time())/3600)} hours'
  
    return uptime_info

def display_array():
    pac_msg, full_cpu_info, product_info, pretty_name, shell, resolution, terminal_emu, kernel, uptime, hostname, gpu, memory = non_debug()
    de, wm, wmtheme, theme, icons = de_info()
    data = []
    if hostname != "":
        data.append(hostname.rstrip('\n'))
        #data.append(dash_gen(len(hostname.rstrip('\n'))))
    
    if pretty_name != "":
        data.append(f'OS: {pretty_name}'.rstrip('\n'))
    
    if product_info != "":
        data.append(f'Host: {product_info}'.rstrip('\n'))
    
    if kernel != "":
        data.append(f'Kernel: {kernel}'.rstrip('\n'))
    
    if uptime != "":
        data.append(f'Uptime: {uptime}'.rstrip('\n'))
    elif seconds_elapsed() != "":
        data.append(f'Uptime: {seconds_elapsed()}')

    if pac_msg != "Packages:":
        data.append(pac_msg.rstrip('\n'))

    if shell != "" and not 'Unknown' in de:
        data.append(f'Shell: {shell}')

    if resolution != "":
        data.append(f'Resolution: {resolution}')
    
    if de != "" and not 'Unknown' in de:
        data.append(f'DE: {de}')
    
    if wm != "" and not 'Unknown' in de:
        data.append(f'WM: {wm}')
    
    if wmtheme != "" and not 'Unknown' in de:
        data.append(f'WM Theme: {wmtheme}')
    
    if theme != "":
        data.append(f'Theme: {theme}')
    
    if icons != "":
        data.append(f'Icons: {icons}')
    
    if terminal_emu != "" and not 'Unknown' in de:
        data.append(f'Terminal: {terminal_emu}')
    
    if full_cpu_info != "":
        data.append(f'CPU: {full_cpu_info}')
    
    if gpu != "":
        data.append(f'GPU: {gpu}')

    if memory != "":
        data.append(f'Memory: {memory}')
    elif get_ram() != "":
        data.append(f'Memory: {get_ram()}')
    
    return data



def logo_test():
    #bedrock_logo = logo_array[0]
    #sel_logo = bedrock_logo
    sys_info = display_array()
    #max_size = max(len(sel_logo), len(sys_info))
    #tmp = []
    #for ele in sel_logo:
    #    tmp.append(len(ele))
    #max_logo_len = max(tmp)
    #del tmp
    #for i in range(max_size):
        #if i > int(len(sys_info)-1):
        #    print(str(sel_logo[i]))
        #elif i > int(len(sel_logo)-1):
            #print(str(space_gen(max_logo_len))+"   "+str(sys_info[i]))
    #if Debug:
      #print("   "+str(sys_info)) #i
        #else:
            #print("   "+str(sys_info[i]))

    return sys_info

#print(logo_test())

def get_user():
  try:
    user = getlogin() # os.getlogin()

    if user is None or len(user) >= 0 or user == 'None':
      user = environ['USERNAME']
  except:
    try:
      user = environ['USERNAME']

      if user is None or len(user) >= 0 or user == 'None':
        user = environ.get('USERNAME')
    except:
      try:
        user = environ.get('USERNAME')
      except:
        pass

  if user is None or len(user) >= 0 or user == 'None':
    user = getpass.getuser()
  
  return str(user)

def fetch(DebugF):
  if Debug or DebugF:
    print(logo_test())

  return logo_test()